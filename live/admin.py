from django.contrib import admin
from django.utils.html import format_html
from .models import Stream, Message, Like, Comment


class StreamAdmin(admin.ModelAdmin):
    """
    Custom Admin interface for Stream model. This adds sorting, filtering, and more readable formatting for stream data.
    """
    list_display = ('stream_title', 'user', 'start_time', 'end_time', 'is_active', 'view_count', 'quality', 'get_auto_delete_time', 'password', 'duration_display')
    list_filter = ('quality', 'is_active', 'auto_delete_time')
    search_fields = ('stream_title', 'user__username', 'stream_key')
    ordering = ('-start_time',)
    list_per_page = 10
    readonly_fields = ('get_auto_delete_time', 'duration_display')

    def duration_display(self, obj):
        """
        Display the duration of the stream in a human-readable format (e.g. minutes:seconds).
        """
        minutes = obj.video_duration // 60
        seconds = obj.video_duration % 60
        return f"{minutes}m {seconds}s"
    duration_display.short_description = 'Video Duration'

    def get_auto_delete_time(self, obj):
        """
        Display when the stream will be auto-deleted.
        """
        return obj.get_auto_delete_time()
    get_auto_delete_time.short_description = 'Auto Delete Time'


class MessageAdmin(admin.ModelAdmin):
    """
    Custom Admin interface for Message model. This adds sorting, filtering, and makes it easier to view messages related to streams.
    """
    list_display = ('stream', 'user', 'content', 'timestamp')
    list_filter = ('timestamp', 'stream')
    search_fields = ('stream__stream_title', 'user__username', 'content')
    ordering = ('-timestamp',)
    list_per_page = 15


class LikeAdmin(admin.ModelAdmin):
    """
    Custom Admin interface for Like model. This interface helps to manage and view which users liked which streams.
    """
    list_display = ('user', 'stream')
    list_filter = ('stream', 'user')
    search_fields = ('user__username', 'stream__stream_title')
    ordering = ('-stream',)
    list_per_page = 20


class CommentAdmin(admin.ModelAdmin):
    """
    Custom Admin interface for Comment model. It allows admins to manage and view comments made by users on live streams.
    """
    list_display = ('user', 'stream', 'content', 'timestamp')
    list_filter = ('timestamp', 'stream')
    search_fields = ('user__username', 'stream__stream_title', 'content')
    ordering = ('-timestamp',)
    list_per_page = 20


# Registering the models with the admin site
admin.site.register(Stream, StreamAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Comment, CommentAdmin)