from django.db import models
from user.models import User
from datetime import timedelta
from django.utils import timezone


class Stream(models.Model):
    """
    This model represents a live stream on the platform. It stores information about the stream,
    such as the stream's key, title, start and end times, quality, and whether it is active.
    The model also tracks user-specific information and provides functionality for auto-deletion
    of streams based on selected time frames (12h, 24h, 72h).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streams')
    stream_key = models.CharField(max_length=255, unique=True)
    stream_title = models.CharField(max_length=255)
    start_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    end_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    quality = models.CharField(
        max_length=20,
        choices=[('1080p', '1080p'), ('720p', '720p'), ('480p', '480p')],
        default='1080p'
    )

    password = models.CharField(max_length=255, null=True, blank=True)

    view_count = models.IntegerField(default=0)
    video_duration = models.IntegerField(default=0)

    auto_delete_time = models.CharField(
        max_length=10,
        choices=[('12h', '12 hours'), ('24h', '24 hours'), ('72h', '72 hours')],
        default='24h'
    )

    def get_end_time(self):
        if not self.is_active:
            start_time = self.start_time if self.start_time else timezone.now()
            return start_time + timedelta(hours=24)
        return None

    def get_auto_delete_time(self):
        """
        Calculate the auto-delete time based on the selected option (12h, 24h, 72h).
        Returns the expected deletion time.
        """
        if not self.is_active:
            if self.auto_delete_time == '12h':
                return self.start_time + timedelta(hours=12)
            elif self.auto_delete_time == '24h':
                return self.start_time + timedelta(hours=24)
            elif self.auto_delete_time == '72h':
                return self.start_time + timedelta(hours=72)
            return self.start_time
        else:
            return None

    def activate(self):
        self.is_active = True
        self.save()

    def deactivate(self):
        self.is_active = False
        self.end_time = timezone.now()
        self.save()

    def increment_view_count(self):
        self.view_count += 1
        self.save()

    def decrement_view_count(self):
        if self.view_count > 0:
            self.view_count -= 1
            self.save()

    def __str__(self):
        return self.stream_title


class Message(models.Model):
    """
    Represents a message sent by a user during a live stream.
    This model links the message to both the stream and the user.
    It also records the timestamp when the message was sent.
    """
    stream = models.ForeignKey(Stream, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message by {self.user.username} on {self.stream.stream_title}"


class Like(models.Model):
    """
    Represents a like action performed by a user on a specific live stream.
    This model tracks which user liked which stream.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_likes')
    stream = models.ForeignKey(Stream, related_name='likes', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} liked {self.stream.stream_title}"


class Comment(models.Model):
    """
    Represents a comment made by a user on a live stream.
    This model captures the user's comment content, links it to the specific stream,
    and records the time the comment was made.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='live_comments')
    stream = models.ForeignKey(Stream, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.stream.stream_title}"