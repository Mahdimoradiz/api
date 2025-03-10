from django_filters import rest_framework as filters
from django.utils.translation import gettext_lazy as _
from .models import Stream, StreamCategory


class StreamFilter(filters.FilterSet):
    """
    Advanced filter set for Stream model with multiple filtering options.
    """
    title = filters.CharFilter(
        field_name='stream_title',
        lookup_expr='icontains',
        label=_('Title contains')
    )
    
    user = filters.CharFilter(
        field_name='user__username',
        lookup_expr='iexact',
        label=_('Username')
    )
    
    category = filters.ModelChoiceFilter(
        queryset=StreamCategory.objects.all(),
        label=_('Category')
    )
    
    tags = filters.CharFilter(
        field_name='tags__name',
        lookup_expr='iexact',
        label=_('Tag name')
    )
    
    status = filters.ChoiceFilter(
        choices=Stream.StreamStatus.choices,
        label=_('Stream status')
    )
    
    is_active = filters.BooleanFilter(label=_('Is active'))
    
    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label=_('Created after')
    )
    
    created_before = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label=_('Created before')
    )
    
    min_viewers = filters.NumberFilter(
        field_name='viewer_count',
        lookup_expr='gte',
        label=_('Minimum viewers')
    )
    
    max_viewers = filters.NumberFilter(
        field_name='viewer_count',
        lookup_expr='lte',
        label=_('Maximum viewers')
    )

    class Meta:
        model = Stream
        fields = [
            'title',
            'user',
            'category',
            'tags',
            'status',
            'is_active',
            'created_after',
            'created_before',
            'min_viewers',
            'max_viewers'
        ]


class MessageFilter(filters.FilterSet):
    """
    Filter set for Message model.
    """
    content = filters.CharFilter(
        lookup_expr='icontains',
        label=_('Content contains')
    )
    
    user = filters.CharFilter(
        field_name='user__username',
        lookup_expr='iexact',
        label=_('Username')
    )
    
    created_after = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label=_('Created after')
    )
    
    is_moderated = filters.BooleanFilter(label=_('Is moderated'))

    class Meta:
        model = Stream
        fields = ['content', 'user', 'created_after', 'is_moderated'] 