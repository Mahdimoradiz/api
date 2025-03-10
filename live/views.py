from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Prefetch, Avg
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters import rest_framework as django_filters
from django.utils import timezone
import logging
import uuid
import random
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    StreamSerializer, 
    MessageSerializer,
    LikeSerializer, 
    CommentSerializer,
    StreamExploreSerializer,
    StreamStatisticsSerializer,
    StreamCategorySerializer,
    StreamTagSerializer
)
from .models import Stream, Message, Like, Comment, StreamStatistics, StreamCategory, StreamTag
from .permissions import IsOwnerOrReadOnly  # permissions.py is in the live directory
from .filters import StreamFilter, MessageFilter  # filters.py is in the live directory 
from .pagination import CustomPageNumberPagination, StreamPagination, MessagePagination  # pagination.py is in the live directory

logger = logging.getLogger(__name__)

class BaseStreamView(APIView):
    """Base class for stream views with common functionality."""
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    pagination_class = CustomPageNumberPagination

    def get_stream(self, stream_id):
        """Get stream object with cached results."""
        cache_key = f'stream_{stream_id}'
        stream = cache.get(cache_key)
        
        if not stream:
            stream = get_object_or_404(Stream, id=stream_id)
            cache.set(cache_key, stream, timeout=300)  # Cache for 5 minutes
            
        return stream


class StreamStartView(BaseStreamView):
    """Create and start a new stream with advanced validation."""

    def post(self, request):
        """Start a new stream with validation and logging."""
        try:
            serializer = StreamSerializer(data={
                **request.data,
                'stream_key': str(uuid.uuid4()),
                'is_active': True,
                'user': request.user.id
            })
            
            if serializer.is_valid():
                stream = serializer.save()
                logger.info(f"Stream created: {stream.id} by user {request.user.id}")
                
                # Cache the new stream
                cache_key = f'stream_{stream.id}'
                cache.set(cache_key, stream, timeout=300)
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
            logger.error(f"Stream creation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.exception("Unexpected error in stream creation")
            return Response(
                {"error": "Internal server error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StreamStopView(BaseStreamView):
    """Stop an active stream with validation and caching."""

    def post(self, request, stream_id):
        """Stop stream with cache invalidation."""
        try:
            stream = self.get_stream(stream_id)
            
            if stream.user != request.user:
                return Response(
                    {"error": "Not authorized"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
                
            if not stream.is_active:
                return Response(
                    {"error": "Stream already stopped"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            stream.is_active = False
            stream.save()
            
            # Invalidate cache
            cache.delete(f'stream_{stream_id}')
            logger.info(f"Stream stopped: {stream_id} by user {request.user.id}")
            
            return Response(
                {"message": "Stream stopped successfully"}, 
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.exception(f"Error stopping stream {stream_id}")
            return Response(
                {"error": "Internal server error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StreamListView(generics.ListAPIView):
    """List streams with advanced filtering and caching."""
    permission_classes = [IsAuthenticated]
    serializer_class = StreamSerializer
    filter_backends = [
        django_filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = StreamFilter
    search_fields = ['stream_title', 'user__username']
    ordering_fields = ['created_at', 'viewer_count']
    pagination_class = CustomPageNumberPagination

    @method_decorator(cache_page(60))  # Cache for 1 minute
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """Get streams with optimized queries and annotations."""
        return Stream.objects.select_related('user').prefetch_related(
            Prefetch('likes', queryset=Like.objects.select_related('user')),
            Prefetch('comments', queryset=Comment.objects.select_related('user'))
        ).annotate(
            like_count=Count('likes', distinct=True),
            comment_count=Count('comments', distinct=True)
        )


class StreamExploreView(BaseStreamView):
    """Advanced stream exploration with personalization."""

    @method_decorator(cache_page(30))  # Cache for 30 seconds
    def get(self, request):
        """Get personalized stream recommendations."""
        try:
            # Get user preferences (implement your logic here)
            user_preferences = self._get_user_preferences(request.user)
            
            # Get active streams with annotations
            active_streams = Stream.objects.select_related('user').prefetch_related(
                'likes', 'comments'
            ).filter(
                is_active=True
            ).exclude(
                user=request.user
            ).annotate(
                popularity_score=Count('likes') + Count('comments') * 2
            ).order_by('-popularity_score')[:50]  # Get top 50 streams
            
            # Apply personalization
            recommended_streams = self._personalize_streams(
                active_streams, 
                user_preferences
            )
            
            serializer = StreamExploreSerializer(recommended_streams[:10], many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.exception("Error in stream exploration")
            return Response(
                {"error": "Internal server error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_user_preferences(self, user):
        """Get cached user preferences."""
        cache_key = f'user_preferences_{user.id}'
        preferences = cache.get(cache_key)
        
        if not preferences:
            # Implement your preference calculation logic here
            preferences = {}  # Placeholder
            cache.set(cache_key, preferences, timeout=3600)  # Cache for 1 hour
            
        return preferences

    def _personalize_streams(self, streams, preferences):
        """Apply personalization algorithm to streams."""
        # Implement your personalization logic here
        return random.sample(list(streams), min(len(streams), 10))


class MessageListView(generics.ListCreateAPIView):
    """Real-time message handling with optimization."""
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get messages with caching and optimization."""
        stream_id = self.kwargs.get('stream_id')
        cache_key = f'stream_messages_{stream_id}'
        queryset = cache.get(cache_key)
        
        if not queryset:
            queryset = Message.objects.select_related(
                'user', 'stream'
            ).filter(
                stream_id=stream_id
            )
            cache.set(cache_key, queryset, timeout=10)  # Cache for 10 seconds
            
        return queryset

    def perform_create(self, serializer):
        """Create message with cache invalidation."""
        message = serializer.save(user=self.request.user)
        cache.delete(f'stream_messages_{message.stream_id}')
        logger.info(f"New message in stream {message.stream_id}")


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling comments.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(
            stream_id=self.kwargs.get('stream_pk')
        ).select_related('user')

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            stream_id=self.kwargs.get('stream_pk')
        )


class LikeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling likes.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LikeSerializer

    def get_queryset(self):
        return Like.objects.filter(
            stream_id=self.kwargs.get('stream_pk')
        ).select_related('user')

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            stream_id=self.kwargs.get('stream_pk')
        )


class StreamViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing streams with advanced functionality.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = StreamSerializer
    filterset_class = StreamFilter
    pagination_class = StreamPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['stream_title', 'description', 'user__username']
    ordering_fields = ['created_at', 'viewer_count', 'likes_count']
    ordering = ['-created_at']

    def get_queryset(self):
        return Stream.objects.select_related(
            'user', 'category'
        ).prefetch_related(
            'tags', 'likes', 'comments'
        ).annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_like(self, request, pk=None):
        """Toggle like status for a stream."""
        stream = self.get_object()
        like, created = Like.objects.get_or_create(
            user=request.user,
            stream=stream
        )
        
        if not created:
            like.delete()
            return Response(
                {"status": "unliked"},
                status=status.HTTP_200_OK
            )
            
        return Response(
            {"status": "liked"},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True)
    def analytics(self, request, pk=None):
        """Get detailed analytics for a stream."""
        stream = self.get_object()
        analytics = {
            'total_viewers': stream.viewer_count,
            'peak_viewers': stream.max_viewers,
            'likes_count': stream.likes.count(),
            'comments_count': stream.comments.count(),
            'average_engagement': stream.statistics.engagement_rate
        }
        return Response(analytics)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing stream messages.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = MessageFilter
    ordering = ['-created_at']

    def get_queryset(self):
        return Message.objects.filter(
            stream_id=self.kwargs['stream_pk']
        ).select_related('user')

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            stream_id=self.kwargs['stream_pk']
        )

    @action(detail=True, methods=['post'])
    def moderate(self, request, pk=None, stream_pk=None):
        """Moderate a message."""
        message = self.get_object()
        message.is_moderated = True
        message.save()
        return Response(
            {"status": "moderated"},
            status=status.HTTP_200_OK
        )


class StreamStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for stream statistics (read-only).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = StreamStatisticsSerializer

    def get_queryset(self):
        return StreamStatistics.objects.filter(
            stream_id=self.kwargs['stream_pk']
        ).select_related('stream')

    @action(detail=True)
    def peak_times(self, request, pk=None, stream_pk=None):
        """Get peak viewing times for the stream."""
        statistics = self.get_object()
        # Implement peak times logic here
        return Response({
            "peak_times": {
                "hour": statistics.peak_hour,
                "viewers": statistics.peak_viewers
            }
        })


class StreamCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing stream categories.
    """
    queryset = StreamCategory.objects.annotate(
        streams_count=Count('stream')
    )
    serializer_class = StreamCategorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    @action(detail=True)
    def streams(self, request, slug=None):
        """Get all streams in this category."""
        category = self.get_object()
        streams = Stream.objects.filter(
            category=category,
            is_active=True
        ).select_related('user')
        
        page = self.paginate_queryset(streams)
        if page is not None:
            serializer = StreamSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = StreamSerializer(streams, many=True)
        return Response(serializer.data)


class StreamTagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing stream tags.
    """
    queryset = StreamTag.objects.annotate(
        streams_count=Count('stream')
    )
    serializer_class = StreamTagSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @action(detail=True)
    def streams(self, request, slug=None):
        """Get all streams with this tag."""
        tag = self.get_object()
        streams = Stream.objects.filter(
            tags=tag,
            is_active=True
        ).select_related('user')
        
        page = self.paginate_queryset(streams)
        if page is not None:
            serializer = StreamSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = StreamSerializer(streams, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def trending(self, request, slug=None):
        """Get trending streams with this tag."""
        tag = self.get_object()
        streams = Stream.objects.filter(
            tags=tag,
            is_active=True,
            created_at__gte=timezone.now() - timezone.timedelta(days=1)
        ).annotate(
            engagement=Count('likes') + Count('comments')
        ).order_by('-engagement')[:10]
        
        serializer = StreamSerializer(streams, many=True)
        return Response(serializer.data)


class FeaturedStreamsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StreamSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return Stream.objects.filter(
            is_active=True,
            is_featured=True 
        ).select_related('user')
        


class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        return Stream.objects.filter(
            is_active=True,
            is_featured=True 
        ).select_related('user')