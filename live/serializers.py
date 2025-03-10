from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import (
    Stream,
    Message,
    Like,
    Comment,
    StreamTag,
    StreamCategory,
    StreamStatistics
)

User = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user information for nested serialization."""
    
    class Meta:
        model = User
        fields = ('id', 'username', 'profile_image')
        read_only_fields = fields


class StreamTagSerializer(serializers.ModelSerializer):
    """Serializer for stream tags."""
    streams_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = StreamTag
        fields = ('id', 'name', 'slug', 'streams_count')
        read_only_fields = ('slug',)

    def validate_name(self, value):
        """Ensure tag name is unique (case-insensitive)."""
        if StreamTag.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError(_("Tag with this name already exists."))
        return value


class StreamCategorySerializer(serializers.ModelSerializer):
    """Serializer for stream categories."""
    subcategories = serializers.SerializerMethodField()
    streams_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = StreamCategory
        fields = (
            'id', 'name', 'slug', 'description',
            'icon', 'parent', 'subcategories', 'streams_count'
        )
        read_only_fields = ('slug',)
    
    def get_subcategories(self, obj):
        """Get all subcategories for this category."""
        if obj.subcategories.exists():
            return StreamCategorySerializer(
                obj.subcategories.all(),
                many=True,
                context=self.context
            ).data
        return []


class StreamStatisticsSerializer(serializers.ModelSerializer):
    """Serializer for stream statistics."""
    
    class Meta:
        model = StreamStatistics
        fields = (
            'total_viewers',
            'peak_viewers',
            'average_viewers',
            'total_likes',
            'total_comments',
            'engagement_rate'
        )
        read_only_fields = fields


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for stream comments."""
    user = UserMinimalSerializer(read_only=True)
    replies_count = serializers.IntegerField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    is_edited = serializers.BooleanField(read_only=True)
    parent_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = (
            'id',
            'user',
            'content',
            'created_at',
            'updated_at',
            'is_edited',
            'edited_at',
            'parent',
            'parent_user',
            'replies_count',
            'likes_count'
        )
        read_only_fields = (
            'user',
            'is_edited',
            'edited_at',
            'created_at',
            'updated_at'
        )
    
    def get_parent_user(self, obj):
        """Get username of parent comment's author if exists."""
        if obj.parent:
            return obj.parent.user.username
        return None

    def validate_content(self, value):
        """Validate comment content."""
        if len(value.strip()) < 1:
            raise serializers.ValidationError(
                _("Comment content cannot be empty.")
            )
        return value

    def validate_parent(self, value):
        """Ensure parent comment belongs to same stream."""
        if value and value.stream_id != self.context['stream_id']:
            raise serializers.ValidationError(
                _("Parent comment must belong to the same stream.")
            )
        return value


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for stream messages."""
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = (
            'id',
            'user',
            'content',
            'created_at',
            'is_pinned',
            'is_moderated'
        )
        read_only_fields = ('user', 'is_moderated')

    def validate_content(self, value):
        """Validate message content."""
        if len(value.strip()) < 1:
            raise serializers.ValidationError(
                _("Message content cannot be empty.")
            )
        return value


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for stream likes."""
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ('id', 'user', 'stream', 'created_at')
        read_only_fields = ('user',)

    def validate_stream(self, value):
        """Ensure user hasn't already liked the stream."""
        user = self.context['request'].user
        if Like.objects.filter(user=user, stream=value).exists():
            raise serializers.ValidationError(
                _("You have already liked this stream.")
            )
        return value


class StreamSerializer(serializers.ModelSerializer):
    """Detailed serializer for streams."""
    user = UserMinimalSerializer(read_only=True)
    tags = StreamTagSerializer(many=True, required=False)
    category = StreamCategorySerializer(required=False)
    statistics = StreamStatisticsSerializer(read_only=True)
    duration = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    recent_messages = serializers.SerializerMethodField()
    
    class Meta:
        model = Stream
        fields = (
            'id',
            'user',
            'stream_key',
            'stream_title',
            'description',
            'thumbnail',
            'is_active',
            'status',
            'scheduled_start',
            'started_at',
            'ended_at',
            'duration',
            'viewer_count',
            'max_viewers',
            'tags',
            'category',
            'statistics',
            'is_liked',
            'likes_count',
            'comments_count',
            'recent_messages',
            'created_at',
            'updated_at'
        )
        read_only_fields = (
            'user',
            'stream_key',
            'started_at',
            'ended_at',
            'viewer_count',
            'max_viewers',
            'statistics'
        )

    def get_duration(self, obj):
        """Calculate stream duration in minutes."""
        if obj.started_at and obj.ended_at:
            duration = obj.ended_at - obj.started_at
            return int(duration.total_seconds() / 60)
        elif obj.started_at and obj.is_active:
            duration = timezone.now() - obj.started_at
            return int(duration.total_seconds() / 60)
        return 0

    def get_is_liked(self, obj):
        """Check if current user has liked the stream."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Like.objects.filter(user=user, stream=obj).exists()
        return False

    def get_recent_messages(self, obj):
        """Get 20 most recent messages."""
        messages = obj.messages.select_related('user').order_by('-created_at')[:20]
        return MessageSerializer(messages, many=True).data

    def validate_stream_title(self, value):
        """Validate stream title."""
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                _("Stream title must be at least 3 characters long.")
            )
        return value

    def validate_scheduled_start(self, value):
        """Ensure scheduled start is in the future."""
        if value and value < timezone.now():
            raise serializers.ValidationError(
                _("Scheduled start time must be in the future.")
            )
        return value

    def create(self, validated_data):
        """Create new stream with tags."""
        tags_data = validated_data.pop('tags', [])
        stream = Stream.objects.create(**validated_data)
        
        # Add tags
        for tag_data in tags_data:
            tag, _ = StreamTag.objects.get_or_create(name=tag_data['name'])
            stream.tags.add(tag)
        
        # Create statistics object
        StreamStatistics.objects.create(stream=stream)
        
        return stream


class StreamExploreSerializer(StreamSerializer):
    """Simplified serializer for stream exploration."""
    
    class Meta(StreamSerializer.Meta):
        fields = (
            'id',
            'user',
            'stream_title',
            'thumbnail',
            'is_active',
            'viewer_count',
            'category',
            'likes_count',
            'comments_count'
        )


class StreamUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating stream information."""
    
    class Meta:
        model = Stream
        fields = (
            'stream_title',
            'description',
            'thumbnail',
            'category',
            'tags'
        )

    def update(self, instance, validated_data):
        """Update stream with tags."""
        tags_data = validated_data.pop('tags', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update tags if provided
        if tags_data is not None:
            instance.tags.clear()
            for tag_data in tags_data:
                tag, _ = StreamTag.objects.get_or_create(name=tag_data['name'])
                instance.tags.add(tag)
        
        return instance