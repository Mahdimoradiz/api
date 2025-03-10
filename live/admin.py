from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Sum
from django.urls import reverse
from django.utils import timezone
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from rangefilter.filters import DateRangeFilter
from .models import (
    Stream,
    Message,
    Like,
    Comment,
    StreamTag,
    StreamCategory,
    StreamStatistics
)


@admin.register(StreamTag)
class StreamTagAdmin(ImportExportModelAdmin):
    """Admin interface for StreamTag model."""
    list_display = ('name', 'slug', 'streams_count', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    def streams_count(self, obj):
        return obj.stream_set.count()
    streams_count.short_description = _('Streams Count')


@admin.register(StreamCategory)
class StreamCategoryAdmin(ImportExportModelAdmin):
    """Admin interface for StreamCategory model."""
    list_display = ('name', 'slug', 'parent', 'streams_count', 'icon_preview')
    list_filter = ('parent',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'icon_preview')
    
    def icon_preview(self, obj):
        if obj.icon:
            return format_html(
                '<img src="{}" width="50" height="50" />',
                obj.icon.url
            )
        return "No Icon"
    icon_preview.short_description = _('Icon Preview')
    
    def streams_count(self, obj):
        return obj.stream_set.count()
    streams_count.short_description = _('Streams Count')


class MessageInline(admin.TabularInline):
    """Inline admin for messages in Stream admin."""
    model = Message
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('user', 'content', 'created_at', 'is_moderated')
    show_change_link = True
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


class CommentInline(admin.TabularInline):
    """Inline admin for comments in Stream admin."""
    model = Comment
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('user', 'content', 'created_at', 'is_edited')
    show_change_link = True


class StreamStatisticsInline(admin.StackedInline):
    """Inline admin for stream statistics."""
    model = StreamStatistics
    readonly_fields = (
        'total_viewers', 'peak_viewers', 'average_viewers',
        'total_likes', 'total_comments', 'engagement_rate'
    )
    can_delete = False
    max_num = 0


@admin.register(Stream)
class StreamAdmin(ImportExportModelAdmin):
    """Advanced admin interface for Stream model."""
    
    class StreamResource(resources.ModelResource):
        """Resource for import/export functionality."""
        class Meta:
            model = Stream
            fields = (
                'id', 'user__username', 'stream_title', 'status',
                'created_at', 'viewer_count', 'is_active'
            )
            export_order = fields
    
    resource_class = StreamResource
    
    list_display = (
        'stream_title',
        'user',
        'status_badge',
        'viewer_count',
        'created_at',
        'duration_display',
        'engagement_metrics'
    )
    list_filter = (
        'status',
        'is_active',
        ('created_at', DateRangeFilter),
        'category',
        'tags'
    )
    search_fields = (
        'stream_title',
        'user__username',
        'description'
    )
    readonly_fields = (
        'stream_key',
        'created_at',
        'updated_at',
        'started_at',
        'ended_at',
        'duration_display',
        'engagement_metrics'
    )
    autocomplete_fields = ['user', 'tags', 'category']
    filter_horizontal = ('tags',)
    inlines = [StreamStatisticsInline, MessageInline, CommentInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'user',
                'stream_title',
                'description',
                'thumbnail',
                'category'
            )
        }),
        (_('Stream Details'), {
            'fields': (
                'stream_key',
                'status',
                'is_active',
                'tags'
            )
        }),
        (_('Timing Information'), {
            'fields': (
                'scheduled_start',
                'started_at',
                'ended_at',
                'duration_display'
            )
        }),
        (_('Statistics'), {
            'fields': (
                'viewer_count',
                'max_viewers',
                'engagement_metrics'
            )
        })
    )
    
    actions = [
        'make_active',
        'make_inactive',
        'reset_statistics'
    ]

    def status_badge(self, obj):
        colors = {
            'PL': 'blue',
            'LV': 'green',
            'EN': 'red',
            'SP': 'orange'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = _('Status')

    def duration_display(self, obj):
        if obj.duration:
            hours = obj.duration.seconds // 3600
            minutes = (obj.duration.seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "-"
    duration_display.short_description = _('Duration')

    def engagement_metrics(self, obj):
        likes = obj.likes.count()
        comments = obj.comments.count()
        if obj.viewer_count:
            engagement = (likes + comments) / obj.viewer_count * 100
            return format_html(
                """
                Likes: {}<br>
                Comments: {}<br>
                Engagement Rate: {:.1f}%
                """,
                likes, comments, engagement
            )
        return "-"
    engagement_metrics.short_description = _('Engagement')

    @admin.action(description=_('Mark selected streams as active'))
    def make_active(self, request, queryset):
        updated = queryset.update(
            is_active=True,
            status=Stream.StreamStatus.LIVE,
            started_at=timezone.now()
        )
        self.message_user(
            request,
            _(f'{updated} streams were marked as active.')
        )

    @admin.action(description=_('Mark selected streams as inactive'))
    def make_inactive(self, request, queryset):
        updated = queryset.update(
            is_active=False,
            status=Stream.StreamStatus.ENDED,
            ended_at=timezone.now()
        )
        self.message_user(
            request,
            _(f'{updated} streams were marked as inactive.')
        )

    @admin.action(description=_('Reset stream statistics'))
    def reset_statistics(self, request, queryset):
        for stream in queryset:
            StreamStatistics.objects.filter(stream=stream).update(
                viewer_count=0,
                max_viewers=0,
                total_likes=0,
                total_comments=0,
                engagement_rate=0
            )
        self.message_user(
            request,
            _('Statistics have been reset for selected streams.')
        )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""
    list_display = (
        'truncated_content',
        'user',
        'stream',
        'created_at',
        'is_moderated'
    )
    list_filter = (
        'is_moderated',
        'is_pinned',
        ('created_at', DateRangeFilter)
    )
    search_fields = (
        'content',
        'user__username',
        'stream__stream_title'
    )
    actions = ['moderate_messages', 'unmoderate_messages']
    
    def truncated_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    truncated_content.short_description = _('Content')

    @admin.action(description=_('Mark selected messages as moderated'))
    def moderate_messages(self, request, queryset):
        queryset.update(is_moderated=True)
        self.message_user(request, _('Selected messages have been moderated.'))

    @admin.action(description=_('Mark selected messages as unmoderated'))
    def unmoderate_messages(self, request, queryset):
        queryset.update(is_moderated=False)
        self.message_user(request, _('Selected messages have been unmoderated.'))


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment model."""
    list_display = (
        'truncated_content',
        'user',
        'stream',
        'created_at',
        'is_edited',
        'has_replies'
    )
    list_filter = (
        'is_edited',
        ('created_at', DateRangeFilter),
        'stream'
    )
    search_fields = (
        'content',
        'user__username',
        'stream__stream_title'
    )
    readonly_fields = ('created_at', 'updated_at', 'edited_at')
    
    def truncated_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    truncated_content.short_description = _('Content')
    
    def has_replies(self, obj):
        return obj.replies.exists()
    has_replies.boolean = True
    has_replies.short_description = _('Has Replies')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Admin interface for Like model."""
    list_display = ('user', 'stream', 'created_at')
    list_filter = (('created_at', DateRangeFilter), 'stream')
    search_fields = ('user__username', 'stream__stream_title')
    readonly_fields = ('created_at',)


# Register additional models if needed
# admin.site.register(StreamStatistics)

# Customize admin site header and title
admin.site.site_header = _('Stream Management')
admin.site.site_title = _('Stream Admin Portal')
admin.site.index_title = _('Welcome to Stream Management Portal')