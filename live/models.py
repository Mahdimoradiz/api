from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q, F, Count

import uuid
from datetime import timedelta


class BaseModel(models.Model):
    """Base model for all models with common fields."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Soft delete the object instead of permanent deletion."""
        self.is_deleted = True
        self.save()

    def restore(self):
        """Restore a soft-deleted object."""
        self.is_deleted = False
        self.save()


class StreamManager(models.Manager):
    """Custom manager for Stream model."""
    
    def active(self):
        """Return only active streams."""
        return self.filter(is_active=True, is_deleted=False)
    
    def popular(self):
        """Return streams ordered by popularity."""
        return self.annotate(
            popularity=Count('likes') + Count('comments') * 2 + F('viewer_count')
        ).order_by('-popularity')
    
    def recent(self):
        """Return recent streams within last 24 hours."""
        yesterday = timezone.now() - timedelta(days=1)
        return self.filter(created_at__gte=yesterday)


class Stream(BaseModel):
    """Model for live streaming sessions."""
    
    class StreamStatus(models.TextChoices):
        PLANNED = 'PL', _('Planned')
        LIVE = 'LV', _('Live')
        ENDED = 'EN', _('Ended')
        SUSPENDED = 'SP', _('Suspended')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='streams'
    )
    stream_key = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False
    )
    stream_title = models.CharField(
        max_length=200,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(200)
        ]
    )
    description = models.TextField(
        blank=True,
        max_length=1000
    )
    thumbnail = models.ImageField(
        upload_to='stream_thumbnails/',
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=False)
    status = models.CharField(
        max_length=2,
        choices=StreamStatus.choices,
        default=StreamStatus.PLANNED
    )
    scheduled_start = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    viewer_count = models.PositiveIntegerField(default=0)
    max_viewers = models.PositiveIntegerField(default=0)
    tags = models.ManyToManyField('StreamTag', blank=True)
    category = models.ForeignKey(
        'StreamCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    objects = StreamManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'status']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.stream_title} by {self.user.username}"

    def clean(self):
        """Validate stream data."""
        if self.scheduled_start and self.scheduled_start < timezone.now():
            raise ValidationError({
                'scheduled_start': _('Scheduled time cannot be in the past')
            })

    def start_stream(self):
        """Start the stream."""
        if self.status != self.StreamStatus.PLANNED:
            raise ValidationError(_('Stream can only be started from planned status'))
        
        self.is_active = True
        self.status = self.StreamStatus.LIVE
        self.started_at = timezone.now()
        self.save()

    def end_stream(self):
        """End the stream."""
        self.is_active = False
        self.status = self.StreamStatus.ENDED
        self.ended_at = timezone.now()
        self.save()

    def update_viewer_count(self, count):
        """Update current and max viewer count."""
        self.viewer_count = count
        if count > self.max_viewers:
            self.max_viewers = count
        self.save()

    def get_absolute_url(self):
        """Get URL for stream detail view."""
        return reverse('stream-detail', kwargs={'pk': self.pk})

    @property
    def duration(self):
        """Calculate stream duration."""
        if self.started_at and self.ended_at:
            return self.ended_at - self.started_at
        return None


class Message(BaseModel):
    """Model for stream chat messages."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    stream = models.ForeignKey(
        Stream,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    content = models.TextField(
        validators=[MaxLengthValidator(1000)]
    )
    is_pinned = models.BooleanField(default=False)
    is_moderated = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['stream', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"


class Like(BaseModel):
    """Model for stream likes."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    stream = models.ForeignKey(
        Stream,
        on_delete=models.CASCADE,
        related_name='likes'
    )

    class Meta:
        unique_together = ['user', 'stream']
        indexes = [
            models.Index(fields=['stream', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.stream.stream_title}"


class Comment(BaseModel):
    """Model for stream comments."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    stream = models.ForeignKey(
        Stream,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField(
        validators=[
            MinLengthValidator(1),
            MaxLengthValidator(500)
        ]
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stream', 'created_at']),
            models.Index(fields=['parent', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"

    def save(self, *args, **kwargs):
        if self.pk:
            self.is_edited = True
            self.edited_at = timezone.now()
        super().save(*args, **kwargs)


class StreamTag(BaseModel):
    """Model for stream tags."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class StreamCategory(BaseModel):
    """Model for stream categories."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.ImageField(
        upload_to='category_icons/',
        null=True,
        blank=True
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class StreamStatistics(BaseModel):
    """Model for tracking stream statistics."""
    stream = models.OneToOneField(
        Stream,
        on_delete=models.CASCADE,
        related_name='statistics'
    )
    total_viewers = models.PositiveIntegerField(default=0)
    peak_viewers = models.PositiveIntegerField(default=0)
    average_viewers = models.FloatField(default=0.0)
    total_likes = models.PositiveIntegerField(default=0)
    total_comments = models.PositiveIntegerField(default=0)
    engagement_rate = models.FloatField(default=0.0)

    def __str__(self):
        return f"Statistics for {self.stream.stream_title}"

    def update_statistics(self):
        """Update stream statistics."""
        self.total_likes = self.stream.likes.count()
        self.total_comments = self.stream.comments.count()
        if self.total_viewers > 0:
            self.engagement_rate = (self.total_likes + self.total_comments) / self.total_viewers
        self.save()