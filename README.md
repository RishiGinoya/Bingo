# Indian Bingo Game 

A real-time multiplayer Indian Bingo game built with Django Channels and WebSockets.

## 🚀 Quick Links

- **Deploy to Production**: See [QUICK_START.md](QUICK_START.md) for Render.com deployment
- **Detailed Deployment Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive instructions
- **Local Development**: Follow setup instructions below

## Features 

### Game Mechanics
- **Indian Bingo Rules**: 5x5 grid with numbers 1-25 (no columns)
- **Win Condition**: Complete 5 lines (horizontal, vertical, or diagonal)
- **Turn-Based Play**: Players take strict turns selecting numbers
- **Real-time Updates**: All actions broadcast instantly to all players

### Board Setup
- **Random Generation**: Generate random 1-25 board with one click
- **Manual Fill**: Click cells sequentially to fill 1-25 manually
- **Clear & Retry**: Clear board and regenerate as needed
- **Pre-Game Only**: Board setup disabled once game starts

### Player Management
- **Ready System**: Players mark ready after filling board
- **Visual Status**: Green (ready), Yellow (not ready), Gray (disconnected)
- **Host Controls**: Start button enabled only when all players ready
- **Player List**: Real-time player status with host indicator ()

### Gameplay
- **Strict Turns**: Only current player can select numbers
- **Turn Rotation**: Automatic turn advancement after each selection
- **Board Locking**: Non-active players see disabled boards
- **Line Tracking**: Real-time counter showing X/5 lines complete
- **BINGO Button**: Auto-enables at 5 complete lines

### Auto-Cleanup
- **Game End**: Room auto-deletes 35 seconds after winner declared
- **All Disconnect**: Room auto-deletes when all players leave
- **No History**: Database automatically cleaned (privacy focused)
- **Auto-Redirect**: Players redirected to home after cleanup

## Technical Stack 

- **Backend**: Django 5.2+
- **WebSockets**: Django Channels 4.0+
- **ASGI Server**: Daphne 4.0+
- **Database**: SQLite (development)
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Real-time**: WebSocket connections with SessionMiddleware

## Setup Instructions 

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Start the ASGI Server

**Important**: Must use Daphne for WebSocket support:

```bash
daphne -b 0.0.0.0 -p 8000 bingo_project.asgi:application
```

### 4. Access the Game

Open http://127.0.0.1:8000/ in your browser

## How to Play 

### Creating a Game
1. Go to home page
2. Enter your name
3. Click "Create Room"
4. Share the room code with other players

### Joining a Game
1. Get room code from host
2. Enter your name and room code
3. Click "Join Room"

### Preparing Your Board
**Option 1 - Random Generation:**
- Click " Generate Random Numbers"
- Board fills with random 1-25 arrangement
- Click " Clear Grid" to regenerate if desired

**Option 2 - Manual Fill:**
- Click " Fill Manually"
- Click any 25 empty cells in any order
- Numbers 1-25 placed sequentially
- Click "Cancel" to stop manual mode

### Getting Ready
1. Fill your board completely (25 numbers)
2. Click " Ready to Play" button (auto-enables)
3. Wait for all players to mark ready
4. Host's "Start Game" enables when all ready

### Playing the Game
1. **Your Turn**:
   - Board is enabled (clickable)
   - Status shows "Your turn! Select a number"
   - Click any number from your board
   
2. **Other's Turn**:
   - Board is disabled (grayed out)
   - Status shows "{Player}'s turn - wait for them"
   - Watch as their selection auto-marks on your board

3. **Winning**:
   - Complete 5 lines (any combination of rows/columns/diagonals)
   - BINGO button auto-enables
   - Click " BINGO!" to claim victory
   - Winner validated automatically

### After Game Ends
- Winner announcement shown to all
- Room closes automatically after 30 seconds
- All players redirected to home page
- Create new room to play again

## Game Rules 

### Indian Bingo Specifics
- **Board Size**: 5x5 grid (25 cells)
- **Number Range**: 1-25 (unlike American 1-75)
- **No Columns**: Numbers distributed randomly, no B-I-N-G-O structure
- **Win Requirement**: 5 complete lines (rows, columns, or diagonals)
- **Maximum Lines**: 12 possible (5 rows + 5 columns + 2 diagonals)

### Turn-Based Rules
- Players alternate in order they joined
- Must wait for your turn to select
- One selection per turn
- Turn advances immediately after selection
- Cannot skip turns

### Validation
- Server validates all BINGO claims
- Checks if claimed lines are actually complete
- Verifies all marked numbers were actually called
- Invalid claims notify player with line count

## Project Structure 

```
bingo_project/
 game/
    consumers.py      # WebSocket consumer (game logic)
    models.py         # Room & Player models
    views.py          # HTTP views (create/join)
    routing.py        # WebSocket URL routing
    urls.py           # HTTP URL patterns
 templates/
    base.html         # Base template
    index.html        # Home page (create/join)
    room.html         # Game room (main UI)
 static/
    css/
        style.css     # Game styling
 bingo_project/
    settings.py       # Django settings
    asgi.py           # ASGI configuration
    urls.py           # Main URL config
 requirements.txt      # Python dependencies
 manage.py            # Django management
 README.md            # This file
```

## Configuration 

### Key Settings (settings.py)

```python
INSTALLED_APPS = [
    'daphne',  # Must be first for ASGI
    'django.contrib.staticfiles',
    'game',
]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"  # Dev only
    }
}
```

### Production Recommendations
- Use Redis for `CHANNEL_LAYERS` instead of InMemory
- Set `DEBUG = False`
- Configure proper `ALLOWED_HOSTS`
- Use PostgreSQL instead of SQLite
- Set up proper logging
- Use environment variables for secrets

## Troubleshooting 

### WebSocket Connection Failed
- Ensure using Daphne, not `runserver`
- Check SessionMiddleware in ASGI config
- Verify CHANNEL_LAYERS configured

### Board Not Updating
- Check browser console for errors
- Verify all players on same server
- Refresh page to reconnect

### Ready Button Not Enabling
- Ensure board has exactly 25 numbers
- All numbers must be > 0
- Check no empty cells remain

### Start Button Not Enabling
- All players must click Ready
- Host must wait for all ready status
- Check player list for unready players

## Development Notes 

### Database Auto-Cleanup
- Rooms delete 35s after winner
- Rooms delete when all disconnect
- No persistent game history
- Privacy-focused design

### Session Management
- Django sessions pass username to WebSocket
- Session created on room create/join
- SessionMiddlewareStack in ASGI critical

### Turn Management
- `current_turn_player` in Room model
- Rotates through connected players
- Server enforces turn order
- Client validates before sending

## License 

This project is for educational purposes.

## Support 

For issues or questions:
1. Check troubleshooting section
2. Review browser console for errors
3. Check server logs for backend errors
4. Ensure all migrations applied
5. Verify dependencies installed

Enjoy playing Indian Bingo! 
