from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # For testing; later use proper CSRF
from accounts.models import CustomUser
from .models import ChatRoom, Message
from django.contrib import messages

@login_required
def dashboard(request):
    # Rooms the current user is in
    rooms = ChatRoom.objects.filter(participants=request.user).order_by('-created_at')
    # Other users to start chats with
    users = CustomUser.objects.exclude(id=request.user.id).order_by('username')
    return render(request, 'chat/dashboard.html', {
        'rooms': rooms,
        'users': users,
    })

@login_required
def start_chat(request, user_id):
    # Create or reuse a 1:1 room between the current user and another user
    other_user = get_object_or_404(CustomUser, id=user_id)
    if other_user.id == request.user.id:
        messages.error(request, "You can't start a chat with yourself.")
        return redirect('dashboard')

    # Try to find an existing room that contains both users
    room = (ChatRoom.objects
            .filter(participants=request.user)
            .filter(participants=other_user)
            .first())
    if not room:
        room = ChatRoom.objects.create(name=f"Chat_{min(request.user.id, other_user.id)}_{max(request.user.id, other_user.id)}")
        room.participants.add(request.user, other_user)

    return redirect('room', room_id=room.id)

@login_required
def start_chat_with_message(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        initial_message = request.POST.get('message', '').strip()

        other_user = get_object_or_404(CustomUser, id=user_id)

        # Prevent chatting with yourself
        if other_user == request.user:
            return JsonResponse({'error': "You cannot chat with yourself."}, status=400)

        # Find or create room
        room = ChatRoom.objects.filter(participants=request.user).filter(participants=other_user).first()
        if not room:
            room = ChatRoom.objects.create(name=f"Chat_{request.user.id}_{other_user.id}")
            room.participants.add(request.user, other_user)

        # Add initial message if provided
        if initial_message:
            Message.objects.create(room=room, sender=request.user, content=initial_message)

        return JsonResponse({'room_id': room.id})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    # Access control: only participants can view
    if not room.participants.filter(id=request.user.id).exists():
        messages.error(request, "You don't have access to this chat.")
        return redirect('dashboard')

    messages_qs = Message.objects.filter(room=room).order_by('timestamp')
    return render(request, 'chat/room.html', {
        'room': room,
        'messages': messages_qs,
    })

# For initial simplicity; later replace csrf_exempt with CSRF token in JS
@csrf_exempt
@login_required
def send_message(request, room_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    room = get_object_or_404(ChatRoom, id=room_id)

    # Access control: only participants can send
    if not room.participants.filter(id=request.user.id).exists():
        return JsonResponse({'error': 'Not allowed'}, status=403)

    text = request.POST.get('message', '').strip()
    if not text:
        return JsonResponse({'error': 'Empty message'}, status=400)

    msg = Message.objects.create(room=room, sender=request.user, content=text)

    return JsonResponse({
        'sender': request.user.username,
        'text': msg.content,
        'timestamp': msg.timestamp.strftime('%H:%M'),
    })