from rest_framework import serializers
from .models import Stream, Message, Like, Comment
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class StreamSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Stream
        fields = [
            'id', 'user', 'stream_key', 'stream_title', 'start_time', 'end_time',
            'is_active', 'quality', 'password', 'view_count', 'video_duration', 'auto_delete_time'
        ]


class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    stream = serializers.PrimaryKeyRelatedField(queryset=Stream.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'stream', 'user', 'content', 'timestamp']


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    stream = serializers.PrimaryKeyRelatedField(queryset=Stream.objects.all())

    class Meta:
        model = Like
        fields = ['id', 'user', 'stream']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    stream = serializers.PrimaryKeyRelatedField(queryset=Stream.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'user', 'stream', 'content', 'timestamp']