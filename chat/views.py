from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChatRoom, Message
from accounts.models import CustomUser


@csrf_exempt
def send_message(request, room_id):
    if request.method == 'POST':
        room = ChatRoom.objects.get(id=room_id)
        text = request.POST.get('message')
        msg = Message.objects.create(room=room, sender=request.user, text=text)
        return JsonResponse({'sender': request.user.username, 'text': msg.text})

User = get_user_model()

@login_required
def dashboard(request):
    # Get all rooms the user is part of
    rooms = ChatRoom.objects.filter(participants=request.user)
    # Get all users to start new chats with
    users = CustomUser.objects.exclude(id=request.user.id)
    return render(request, 'chat/dashboard.html', {
        'rooms': rooms,
        'users': users,
    })


@login_required
def room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    messages = Message.objects.filter(room=room).order_by('timestamp')
    return render(request, 'chat/room.html', {
        'room': room,
        'messages': messages,
    })

