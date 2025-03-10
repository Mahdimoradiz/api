from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db.models import Count
from django.utils import timezone
import csv
from django.http import HttpResponse
from . import models

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin interface for Profile model with enhanced UI and functionality"""
    
    # Display and Organization
    list_display = (
        'user', 'name', 'username', 'show_avatar',
        'is_private', 'created_at', 'followers_count',
        'following_count', 'account_age'
    )
    list_filter = ('is_private', 'gender', 'created_at', 'who_can_follow')
    search_fields = ('user__username', 'name', 'location', 'bio')
    readonly_fields = ('created_at', 'updated_at', 'show_full_avatar', 'account_age')
    list_per_page = 20
    
    # Available Actions
    actions = ['make_private', 'make_public', 'reset_profile_picture']
    
    # Fieldset Organization
    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('user', 'name'),
                ('username', 'picture', 'show_full_avatar'),
                'bio'
            ),
            'classes': ('wide',)
        }),
        ('Additional Information', {
            'fields': (
                ('location', 'website'),
                ('birth_date', 'gender')
            ),
            'classes': ('wide',)
        }),
        ('Privacy Settings', {
            'fields': ('is_private', 'show_birthdate', 'who_can_follow'),
            'classes': ('collapse',),
            'description': 'Configure user privacy settings'
        }),
        ('Statistics', {
            'fields': (
                ('followers_count', 'following_count'),
                'account_age'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # Avatar Display Methods
    def show_avatar(self, obj):
        """Display avatar thumbnail in list view"""
        if obj.picture:
            return mark_safe(
                f'<img src="{obj.picture.url}" '
                'width="50" height="50" '
                'style="border-radius: 50%; object-fit: cover; '
                'border: 2px solid #eee;" />'
            )
        return mark_safe(
            '<div style="width: 50px; height: 50px; '
            'border-radius: 50%; background-color: #eee; '
            'display: flex; align-items: center; '
            'justify-content: center;">'
            '<span style="color: #666;">No</span></div>'
        )
    show_avatar.short_description = 'Avatar'
    show_avatar.allow_tags = True

    def show_full_avatar(self, obj):
        """Display full-size avatar in detail view"""
        if obj.picture:
            return mark_safe(
                f'<img src="{obj.picture.url}" '
                'width="200" height="200" '
                'style="border-radius: 10px;" />'
            )
        return "No Avatar"
    show_full_avatar.short_description = 'Current Avatar'

    # Helper Methods
    def account_age(self, obj):
        """Calculate account age safely"""
        try:
            if not obj.created_at:
                return "N/A"
            age = timezone.now() - obj.created_at
            return f"{age.days} days"
        except (TypeError, ValueError):
            return "N/A"
    account_age.short_description = 'Account Age'

    # Bulk Actions
    def make_private(self, request, queryset):
        """Set selected profiles to private"""
        updated = queryset.update(is_private=True)
        self.message_user(
            request,
            f'{updated} profiles marked as private.'
        )
    make_private.short_description = 'Make selected profiles private'

    def make_public(self, request, queryset):
        """Set selected profiles to public"""
        updated = queryset.update(is_private=False)
        self.message_user(
            request,
            f'{updated} profiles marked as public.'
        )
    make_public.short_description = 'Make selected profiles public'

    def reset_profile_picture(self, request, queryset):
        """Reset profile pictures to default"""
        for profile in queryset:
            profile.set_default_picture()
        self.message_user(
            request,
            f'Reset profile pictures for {len(queryset)} profiles.'
        )
    reset_profile_picture.short_description = 'Reset profile pictures'

    # Custom Styling
    class Media:
        css_internal = """
            <style>
                /* Avatar Styling */
                .field-show_full_avatar img {
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                    border-radius: 10px;
                }
                .field-show_full_avatar img:hover {
                    transform: scale(1.05);
                }
                .field-show_avatar img {
                    border: 2px solid #eee;
                    border-radius: 50%;
                }

                /* Text Styling */
                .field-account_age {
                    color: #666;
                    font-weight: bold;
                }
                .field-followers_count,
                .field-following_count {
                    color: #007bff;
                }

                /* Layout Styling */
                .collapse {
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 15px 0;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                
                /* Form Elements */
                .actions select {
                    border-radius: 4px;
                    padding: 8px;
                    border: 1px solid #ddd;
                }
                
                /* Table Styling */
                thead th {
                    background: #343a40;
                    color: white;
                    padding: 12px;
                }
                tbody tr:hover {
                    background-color: #f5f5f5;
                    transition: background-color 0.2s;
                }
                
                /* Additional Enhancements */
                .field-name input,
                .field-username input {
                    border-radius: 4px;
                    padding: 6px 10px;
                }
                .field-bio textarea {
                    border-radius: 4px;
                    padding: 8px;
                }
            </style>
        """

@admin.register(models.Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'followed_user', 'created_at', 'relationship_age')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'followed_user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'relationship_age')
    raw_id_fields = ('user', 'followed_user')
    list_select_related = ('user', 'followed_user')
    
    def relationship_age(self, obj):
        """Calculate following duration safely"""
        from django.utils import timezone
        try:
            if not obj.created_at:
                return "N/A"
            age = timezone.now() - obj.created_at
            return f"{age.days} days"
        except (TypeError, ValueError):
            return "N/A"
    relationship_age.short_description = 'Following Duration'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'followed_user')

@admin.register(models.Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('blocker', 'blocked', 'created_at', 'block_duration')
    list_filter = ('created_at',)
    search_fields = ('blocker__username', 'blocked__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'block_duration')
    raw_id_fields = ('blocker', 'blocked')
    actions = ['remove_blocks', 'export_as_csv']

    def block_duration(self, obj):
        """Calculate block duration safely"""
        from django.utils import timezone
        try:
            if not obj.created_at:
                return "N/A"
            duration = timezone.now() - obj.created_at
            return f"{duration.days} days"
        except (TypeError, ValueError):
            return "N/A"
    block_duration.short_description = 'Block Duration'

    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from django.utils import timezone
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="blocks.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Blocker', 'Blocked', 'Created At', 'Duration'])
        
        for block in queryset:
            try:
                duration = self.block_duration(block)
                created_at = block.created_at.isoformat() if block.created_at else "N/A"
            except (AttributeError, TypeError, ValueError):
                duration = "N/A"
                created_at = "N/A"
                
            writer.writerow([
                block.blocker.username,
                block.blocked.username,
                created_at,
                duration
            ])
            
        return response
    export_as_csv.short_description = "Export selected blocks as CSV"


