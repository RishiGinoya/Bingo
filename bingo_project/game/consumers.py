import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Player
import logging

logger = logging.getLogger(__name__)

class BingoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_code = self.scope['url_route']['kwargs']['room_code']
            self.room_group_name = f'bingo_{self.room_code}'
            
            # Get session data asynchronously
            session_data = await self.get_session_data()
            if not session_data:
                logger.warning(f"No session found for room {self.room_code}")
                await self.close(code=4000)
                return
                
            self.user_name = session_data.get('user_name')
            self.is_host = session_data.get('is_host', False)

            # Check if session data exists
            if not self.user_name:
                logger.warning(f"No user_name in session for room {self.room_code}")
                await self.close(code=4000)
                return

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()

            # Get or create player with board
            player_id, board, is_new = await self.get_or_create_player()
            
            if not player_id:
                logger.error(f"Failed to create player {self.user_name} in room {self.room_code}")
                await self.close(code=4001)
                return
            
            # Send empty board if new player, otherwise send saved board
            if not board:
                board = []  # Empty board - player will fill it
            
            # Send initial data to the connecting user
            room_data = await self.get_room_data()
            await self.send(text_data=json.dumps({
                'type': 'game_init',
                'board': board,
                'player_name': self.user_name,
                'is_host': self.is_host,
                'room_data': room_data
            }))

            # Notify others that a new player joined
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'player_joined',
                    'player_name': self.user_name,
                    'is_host': self.is_host
                }
            )
            
            logger.info(f"Player {self.user_name} connected to room {self.room_code}")
            
        except Exception as e:
            logger.error(f"Error in connect: {str(e)}")
            await self.close(code=4002)

    async def disconnect(self, close_code):
        logger.info(f"Player {getattr(self, 'user_name', 'Unknown')} disconnected from room {getattr(self, 'room_code', 'Unknown')} with code {close_code}")
        
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        
        # Mark player as disconnected
        if hasattr(self, 'user_name') and hasattr(self, 'room_code'):
            await self.mark_player_disconnected()
            
            # Check if all players have disconnected, if so delete the room
            all_disconnected = await self.check_all_disconnected()
            if all_disconnected:
                await self.cleanup_room()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'start_game':
                if self.is_host:
                    await self.start_game()
            
            elif action == 'player_ready':
                await self.handle_player_ready()
            
            elif action == 'generate_random_board':
                await self.handle_generate_random_board()
            
            elif action == 'clear_board':
                await self.handle_clear_board()
            
            elif action == 'manual_fill_cell':
                cell_index = data.get('cell_index')
                if cell_index is not None:
                    await self.handle_manual_fill_cell(cell_index)
            
            elif action == 'select_number':
                number = data.get('number')
                if number:
                    await self.handle_number_selection(number)
            
            elif action == 'claim_bingo':
                board_state = data.get('board_state', [])
                await self.check_bingo(board_state)
            
            elif action == 'chat_message':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': data['message'],
                        'sender': self.user_name
                    }
                )
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'An error occurred processing your request'
            }))

    @database_sync_to_async
    def get_session_data(self):
        """Get session data asynchronously to avoid sync/async conflict"""
        try:
            session = self.scope.get('session', {})
            return {
                'user_name': session.get('user_name'),
                'is_host': session.get('is_host', False)
            }
        except Exception as e:
            logger.error(f"Error getting session data: {str(e)}")
            return None

    @database_sync_to_async
    def get_or_create_player(self):
        try:
            room = Room.objects.get(code=self.room_code)
            player, created = Player.objects.get_or_create(
                room=room,
                name=self.user_name,
                defaults={
                    'is_host': self.is_host,
                    'channel_name': self.channel_name,
                    'is_connected': True
                }
            )
            
            # If not created, update connection status
            if not created:
                player.is_connected = True
                player.channel_name = self.channel_name
                player.save()
            
            # Get board data
            board = []
            if player.board_state:
                board = json.loads(player.board_state)
            
            # Return player id, board, and whether it needs a new board
            needs_board = created and not board
            return player.id, board, needs_board
            
        except Room.DoesNotExist:
            logger.error(f"Room {self.room_code} does not exist")
            return None, [], False
        except Exception as e:
            logger.error(f"Error in get_or_create_player: {str(e)}")
            return None, [], False
    
    @database_sync_to_async
    def save_player_board(self, player_id, board):
        try:
            player = Player.objects.get(id=player_id)
            player.board_state = json.dumps(board)
            player.save()
        except Player.DoesNotExist:
            logger.error(f"Player {player_id} not found")
        except Exception as e:
            logger.error(f"Error saving board: {str(e)}")

    @database_sync_to_async
    def check_all_disconnected(self):
        """Check if all players in the room are disconnected"""
        try:
            room = Room.objects.get(code=self.room_code)
            connected_count = room.players.filter(is_connected=True).count()
            return connected_count == 0
        except Room.DoesNotExist:
            return True
    
    @database_sync_to_async
    def cleanup_room(self):
        """Delete room and all associated player data"""
        try:
            room = Room.objects.get(code=self.room_code)
            # Delete all players (cascade will handle this, but explicit is better)
            room.players.all().delete()
            # Delete the room
            room.delete()
            logger.info(f"Room {self.room_code} and all player data deleted from database")
            return True
        except Room.DoesNotExist:
            logger.warning(f"Room {self.room_code} not found for cleanup")
            return False
    
    async def delayed_cleanup(self, delay_seconds):
        """Cleanup room after a delay (for winner announcement)"""
        import asyncio
        await asyncio.sleep(delay_seconds)
        
        # Send notification before cleanup
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'room_closing',
                'message': 'Game completed! Room will close shortly.'
            }
        )
        
        # Wait a bit more for the message to be delivered
        await asyncio.sleep(5)
        
        # Cleanup the room
        await self.cleanup_room()

    @database_sync_to_async
    def mark_player_disconnected(self):
        Player.objects.filter(
            room__code=self.room_code,
            name=self.user_name
        ).update(is_connected=False)

    @database_sync_to_async
    def get_room_data(self):
        try:
            room = Room.objects.get(code=self.room_code)
            players = list(room.players.all().values('name', 'is_host', 'is_connected', 'is_ready'))
            
            # Parse drawn numbers
            drawn_numbers = []
            if room.drawn_numbers:
                drawn_numbers = [int(n) for n in room.drawn_numbers.split(',') if n]
            
            return {
                'host_name': room.host_name,
                'game_started': room.game_started,
                'current_number': room.current_number,
                'drawn_numbers': drawn_numbers,
                'players': players,
                'current_turn_player': room.current_turn_player
            }
        except Room.DoesNotExist:
            return {}
        except Exception as e:
            logger.error(f"Error in get_room_data: {str(e)}")
            return {}

    async def start_game(self):
        # Check if all players are ready
        all_ready, not_ready_players = await self.check_all_players_ready()
        if not all_ready:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Waiting for players to be ready: {not_ready_players}'
            }))
            return
        
        success, current_turn_player = await self.mark_game_started()
        if success:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_started',
                    'message': 'Game has started! Good luck!',
                    'current_turn_player': current_turn_player
                }
            )
    
    async def handle_player_ready(self):
        """Mark player as ready and broadcast to all"""
        # Check if board is filled
        board_filled = await self.check_player_board_filled()
        if not board_filled:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Please fill your board completely before marking ready!'
            }))
            return
        
        success = await self.mark_player_ready()
        if success:
            # Broadcast ready status to all players
            ready_status = await self.get_ready_status()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'player_ready_update',
                    'player_name': self.user_name,
                    'ready_status': ready_status
                }
            )
    
    async def handle_generate_random_board(self):
        """Generate a random board for the player"""
        board = self.generate_bingo_board()
        player_id = await self.get_player_id()
        if player_id:
            await self.save_player_board(player_id, board)
            await self.send(text_data=json.dumps({
                'type': 'board_generated',
                'board': board
            }))
    
    async def handle_clear_board(self):
        """Clear the player's board"""
        player_id = await self.get_player_id()
        if player_id:
            await self.save_player_board(player_id, [])
            await self.send(text_data=json.dumps({
                'type': 'board_cleared'
            }))
    
    async def handle_manual_fill_cell(self, cell_index):
        """Fill a cell with the next sequential number (1-25)"""
        player_id = await self.get_player_id()
        if not player_id:
            return
        
        # Get current board
        current_board = await self.get_player_board(player_id)
        if not current_board:
            current_board = [0] * 25  # Initialize empty board with 0s
        
        # Find the next number to place (1-25)
        filled_numbers = [n for n in current_board if n > 0]
        if len(filled_numbers) >= 25:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Board is already full!'
            }))
            return
        
        # Check if cell is already filled
        if current_board[cell_index] > 0:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'This cell is already filled!'
            }))
            return
        
        # Place the next number
        next_number = len(filled_numbers) + 1
        current_board[cell_index] = next_number
        
        # Save the board
        await self.save_player_board(player_id, current_board)
        
        await self.send(text_data=json.dumps({
            'type': 'cell_filled',
            'cell_index': cell_index,
            'number': next_number,
            'board': current_board
        }))

    @database_sync_to_async
    def get_player_id(self):
        try:
            player = Player.objects.get(room__code=self.room_code, name=self.user_name)
            return player.id
        except Player.DoesNotExist:
            return None
    
    @database_sync_to_async
    def get_player_board(self, player_id):
        try:
            player = Player.objects.get(id=player_id)
            if player.board_state:
                return json.loads(player.board_state)
            return []
        except Player.DoesNotExist:
            return []
    
    @database_sync_to_async
    def check_player_board_filled(self):
        """Check if current player's board is filled"""
        try:
            player = Player.objects.get(room__code=self.room_code, name=self.user_name)
            if not player.board_state:
                return False
            board = json.loads(player.board_state)
            return len(board) == 25 and all(n > 0 for n in board)
        except Player.DoesNotExist:
            return False
    
    @database_sync_to_async
    def mark_player_ready(self):
        """Mark player as ready"""
        try:
            player = Player.objects.get(room__code=self.room_code, name=self.user_name)
            player.is_ready = True
            player.save()
            return True
        except Player.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_ready_status(self):
        """Get list of all players with their ready status"""
        try:
            room = Room.objects.get(code=self.room_code)
            players = room.players.filter(is_connected=True).values('name', 'is_ready')
            return list(players)
        except Room.DoesNotExist:
            return []
    
    @database_sync_to_async
    def check_all_players_ready(self):
        """Check if all connected players are ready"""
        try:
            room = Room.objects.get(code=self.room_code)
            players = room.players.filter(is_connected=True)
            not_ready = [p.name for p in players if not p.is_ready]
            return len(not_ready) == 0, ', '.join(not_ready)
        except Room.DoesNotExist:
            return False, "Room not found"

    @database_sync_to_async
    def check_all_boards_filled(self):
        """Check if all connected players have filled their boards (25 numbers)"""
        try:
            room = Room.objects.get(code=self.room_code)
            players = room.players.filter(is_connected=True)
            
            for player in players:
                if not player.board_state:
                    return False
                board = json.loads(player.board_state)
                # Check if board has 25 valid numbers
                if len(board) != 25 or any(n <= 0 for n in board):
                    return False
            
            return True
        except Room.DoesNotExist:
            return False

    @database_sync_to_async
    def mark_game_started(self):
        try:
            room = Room.objects.get(code=self.room_code)
            if not room.game_started:
                room.game_started = True
                # Set first connected player as the starting turn
                first_player = room.players.filter(is_connected=True).order_by('id').first()
                if first_player:
                    room.current_turn_player = first_player.name
                room.save()
                return True, room.current_turn_player
            return False, room.current_turn_player
        except Room.DoesNotExist:
            return False, ""

    async def handle_number_selection(self, number):
        """Handle when a player selects a number from their board"""
        # Check if this player can select (turn-based)
        can_select, message, _ = await self.check_player_turn()
        
        if not can_select:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': message
            }))
            return
        
        success, drawn_numbers, next_turn_player = await self.mark_number_as_called(number)
        if success:
            # Broadcast the selected number to all players
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'number_called',
                    'number': number,
                    'drawn_numbers': drawn_numbers,
                    'selected_by': self.user_name,
                    'current_turn_player': next_turn_player
                }
            )
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'This number has already been selected!'
            }))

    @database_sync_to_async
    def check_player_turn(self):
        """Check if this player can select a number (strict turn-based)"""
        try:
            room = Room.objects.get(code=self.room_code)
            
            # Check if it's this player's turn
            if room.current_turn_player != self.user_name:
                return False, f"It's {room.current_turn_player}'s turn!", False
            
            return True, "", False
            
        except Room.DoesNotExist:
            return False, "Room not found", False
        except Exception as e:
            logger.error(f"Error in check_player_turn: {str(e)}")
            return False, "Error checking turn", False

    @database_sync_to_async
    def get_player_count(self):
        """Get total number of connected players"""
        try:
            room = Room.objects.get(code=self.room_code)
            return room.players.filter(is_connected=True).count()
        except Room.DoesNotExist:
            return 0
        except Exception as e:
            logger.error(f"Error getting player count: {str(e)}")
            return 0

    @database_sync_to_async
    def mark_number_as_called(self, number):
        """Mark a number as called/selected by a player"""
        try:
            room = Room.objects.get(code=self.room_code)
            
            # Get drawn numbers
            drawn = []
            if room.drawn_numbers:
                drawn = [int(n) for n in room.drawn_numbers.split(',') if n]
            
            # Check if number already called
            if number in drawn:
                return False, drawn, room.current_turn_player
            
            # Mark number as called
            drawn.append(number)
            room.drawn_numbers = ','.join(map(str, drawn))
            room.current_number = number
            
            # Rotate to next player
            connected_players = list(room.players.filter(is_connected=True).order_by('id').values_list('name', flat=True))
            if connected_players:
                try:
                    current_index = connected_players.index(self.user_name)
                    next_index = (current_index + 1) % len(connected_players)
                    room.current_turn_player = connected_players[next_index]
                except ValueError:
                    # Current player not in list, set first player
                    room.current_turn_player = connected_players[0]
            
            room.save()
            
            return True, drawn, room.current_turn_player
        except Room.DoesNotExist:
            return False, [], ""
        except Exception as e:
            logger.error(f"Error in mark_number_as_called: {str(e)}")
            return False, [], ""

    async def check_bingo(self, board_state):
        is_valid, complete_lines = await self.validate_bingo(board_state)
        
        if is_valid:
            # Announce winner
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'bingo_winner',
                    'winner': self.user_name
                }
            )
            
            # Schedule room cleanup after 30 seconds to allow players to see results
            # Note: In production, you might want to use Celery or similar for scheduled tasks
            import asyncio
            asyncio.create_task(self.delayed_cleanup(30))
        else:
            await self.send(text_data=json.dumps({
                'type': 'invalid_bingo',
                'message': f'Invalid BINGO! You need 5 complete lines. You have {complete_lines} lines.'
            }))

    @database_sync_to_async
    def validate_bingo(self, board_state):
        """
        board_state is a list of dicts: [{'number': 5, 'marked': True}, ...]
        Indian Bingo: Check if player has 5 complete lines
        """
        try:
            room = Room.objects.get(code=self.room_code)
            
            # Parse drawn numbers
            drawn = set()
            if room.drawn_numbers:
                drawn = set([int(n) for n in room.drawn_numbers.split(',') if n])
            
            # Extract marked numbers and validate they were called
            marked_positions = []
            for idx, cell in enumerate(board_state):
                if cell.get('marked'):
                    number = cell.get('number')
                    # Check if this number was actually drawn
                    if number not in drawn:
                        return False, 0
                    marked_positions.append(idx)
            
            # Check if marked positions form 5 complete lines (Indian Bingo rule)
            complete_lines = self.count_complete_lines(marked_positions)
            if complete_lines >= 5:
                return True, complete_lines
            
            return False, complete_lines
        except Room.DoesNotExist:
            return False, []

    def count_complete_lines(self, marked_positions):
        """Count complete lines (rows, columns, diagonals) - Indian Bingo needs 5 lines to win"""
        if len(marked_positions) < 5:
            return 0
        
        marked_set = set(marked_positions)
        complete_lines = 0
        
        # Check rows (0-4, 5-9, 10-14, 15-19, 20-24)
        for row in range(5):
            row_indices = set(range(row * 5, row * 5 + 5))
            if row_indices.issubset(marked_set):
                complete_lines += 1
        
        # Check columns
        for col in range(5):
            col_indices = set(range(col, 25, 5))
            if col_indices.issubset(marked_set):
                complete_lines += 1
        
        # Check diagonals
        diagonal1 = {0, 6, 12, 18, 24}  # Top-left to bottom-right
        diagonal2 = {4, 8, 12, 16, 20}  # Top-right to bottom-left
        
        if diagonal1.issubset(marked_set):
            complete_lines += 1
        if diagonal2.issubset(marked_set):
            complete_lines += 1
        
        return complete_lines

    def generate_bingo_board(self):
        """Generate Indian Bingo board: 25 random numbers from 1-25"""
        # Simply pick 25 unique random numbers from 1 to 25
        board = random.sample(range(1, 26), 25)
        return board

    # Handler methods for group messages
    async def player_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'player_name': event['player_name'],
            'is_host': event.get('is_host', False)
        }))

    async def game_started(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_started',
            'message': event['message'],
            'current_turn_player': event.get('current_turn_player', '')
        }))

    async def number_called(self, event):
        await self.send(text_data=json.dumps({
            'type': 'number_called',
            'number': event['number'],
            'drawn_numbers': event['drawn_numbers'],
            'selected_by': event.get('selected_by'),
            'current_turn_player': event.get('current_turn_player', '')
        }))

    async def bingo_winner(self, event):
        await self.send(text_data=json.dumps({
            'type': 'bingo_winner',
            'winner': event['winner']
        }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
            'sender': event['sender']
        }))
    
    async def player_ready_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_ready_update',
            'player_name': event['player_name'],
            'ready_status': event['ready_status']
        }))
    
    async def room_closing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'room_closing',
            'message': event['message']
        }))