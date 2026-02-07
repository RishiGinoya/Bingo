# game/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Room, Player

def index(request):
    return render(request, 'index.html')

def health_check(request):
    """Health check endpoint for keep-alive services"""
    return JsonResponse({'status': 'ok', 'message': 'Bingo server is running'})

def join_room(request):
    if request.method == "POST":
        name = request.POST.get('name').strip()
        room_code = request.POST.get('room_code').upper().strip()
        
        try:
            room = Room.objects.get(code=room_code, is_active=True)
            
            # Check if name already taken in this room
            if Player.objects.filter(room=room, name=name).exists():
                return render(request, 'index.html', {'error': f'Name "{name}" is already taken in this room'})
            
            request.session['user_name'] = name
            request.session['room_code'] = room_code
            request.session['is_host'] = False
            
            return redirect(f'/room/{room_code}/')
        except Room.DoesNotExist:
            return render(request, 'index.html', {'error': 'Room not found'})
    
    return redirect('/')

def create_room(request):
    if request.method == "POST":
        name = request.POST.get('name').strip()
        
        # Create a new Room with the host name
        new_room = Room.objects.create(host_name=name)
        
        request.session['user_name'] = name
        request.session['room_code'] = new_room.code
        request.session['is_host'] = True
        
        return redirect(f'/room/{new_room.code}/')
    
    return redirect('/')

def room(request, room_code):
    if 'user_name' not in request.session:
        return redirect('/')
    
    room = get_object_or_404(Room, code=room_code, is_active=True)
    is_host = request.session.get('is_host', False)
    
    return render(request, 'room.html', {
        'room_code': room_code,
        'room': room,
        'user_name': request.session['user_name'],
        'is_host': is_host
    })