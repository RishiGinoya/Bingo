from django.db import models
import random, string
import json

class Room(models.Model):
    code = models.CharField(max_length=10, unique=True)
    host_name = models.CharField(max_length=50, default="Host")
    drawn_numbers = models.TextField(default="", blank=True)  # comma-separated numbers
    current_number = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    game_started = models.BooleanField(default=False)
    players_who_selected_this_round = models.TextField(default="", blank=True)  # comma-separated player names
    current_turn_player = models.CharField(max_length=50, default="", blank=True)  # whose turn it is
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        super().save(*args, **kwargs)

    def get_drawn_numbers_list(self):
        if self.drawn_numbers:
            return [int(n) for n in self.drawn_numbers.split(',') if n]
        return []

    def add_drawn_number(self, number):
        drawn = self.get_drawn_numbers_list()
        if number not in drawn:
            drawn.append(number)
            self.drawn_numbers = ','.join(map(str, drawn))
            self.current_number = number
            self.save()

    def get_available_numbers(self):
        drawn = set(self.get_drawn_numbers_list())
        return [n for n in range(1, 76) if n not in drawn]  # Traditional bingo 1-75

    def __str__(self):
        return f"Room {self.code} - Host: {self.host_name}"

class Player(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='players')
    name = models.CharField(max_length=50)
    channel_name = models.CharField(max_length=255, blank=True)
    board_state = models.TextField(default="")  # JSON string of board numbers
    is_host = models.BooleanField(default=False)
    is_connected = models.BooleanField(default=True)
    is_ready = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    def set_board(self, board_numbers):
        self.board_state = json.dumps(board_numbers)
        self.save()

    def get_board(self):
        if self.board_state:
            return json.loads(self.board_state)
        return []

    def __str__(self):
        return f"{self.name} in {self.room.code}"

    class Meta:
        unique_together = ['room', 'name']