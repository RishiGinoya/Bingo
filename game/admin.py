from django.contrib import admin
from .models import Room, Player

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['code', 'host_name', 'game_started', 'is_active', 'created_at', 'player_count']
    list_filter = ['game_started', 'is_active', 'created_at']
    search_fields = ['code', 'host_name']
    readonly_fields = ['code', 'created_at']
    
    def player_count(self, obj):
        return obj.players.count()
    player_count.short_description = 'Players'

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'room', 'is_host', 'is_connected', 'joined_at']
    list_filter = ['is_host', 'is_connected', 'joined_at']
    search_fields = ['name', 'room__code']
    readonly_fields = ['joined_at']

