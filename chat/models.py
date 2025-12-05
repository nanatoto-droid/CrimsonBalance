from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import CustomUser


User = get_user_model()

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    # participants = models.ManyToManyField(User, related_name='chat_rooms')
    participants = models.ManyToManyField(CustomUser)
    is_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"