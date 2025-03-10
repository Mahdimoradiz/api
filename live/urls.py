from django.urls import path, include
from rest_framework_nested import routers
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .views import (
    StreamStartView,
    StreamStopView,
    StreamExploreView,
    CommentListView,
    StreamViewSet,
    MessageViewSet,
    StreamStatisticsViewSet,
    StreamCategoryViewSet,
    StreamTagViewSet
)

app_name = 'live'

# Main router
router = routers.DefaultRouter()
router.register(r'streams', StreamViewSet, basename='stream')
router.register(r'categories', StreamCategoryViewSet, basename='category')
router.register(r'tags', StreamTagViewSet, basename='tag')

# Nested routers for stream-related endpoints
stream_router = routers.NestedDefaultRouter(router, r'streams', lookup='stream')
stream_router.register(r'messages', MessageViewSet, basename='stream-messages')
stream_router.register(r'statistics', StreamStatisticsViewSet, basename='stream-statistics')

# URL patterns with versioning support
urlpatterns = [
    # API Version 1
    path('v1/', include([
        # Stream management
        path('streams/start/', 
            StreamStartView.as_view(), 
            name='stream-start'
        ),
        path('streams/<int:stream_id>/stop/', 
            StreamStopView.as_view(), 
            name='stream-stop'
        ),
        # Stream listing and exploration
        path('streams/explore/', 
            StreamExploreView.as_view(), 
            name='stream-explore'
        ),
        # Comments
        path('streams/<int:stream_id>/comments/', 
            CommentListView.as_view(), 
            name='stream-comments'
        ),
        # Include routers
        path('', include(router.urls)),
        path('', include(stream_router.urls)),
    ])),
    # API Version 2 (for future use)
    path('v2/', include([
        # Future v2 endpoints will go here
    ])),
    
]

# Custom error handlers
handler400 = 'live.error_handlers.bad_request'
handler403 = 'live.error_handlers.permission_denied'
handler404 = 'live.error_handlers.not_found'
handler500 = 'live.error_handlers.server_error'


if settings.DEBUG:
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    
    schema_view = get_schema_view(
        openapi.Info(
            title=_("Live Streaming API"),
            default_version='v1',
            description=_("API documentation for the Live Streaming service"),
            terms_of_service="https://www.example.com/terms/",
            contact=openapi.Contact(email="contact@example.com"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
    )
    
    urlpatterns += [
        # Remove the docs/ URL pattern that uses include_docs_urls
        path('swagger/', schema_view.with_ui(
            'swagger', cache_timeout=0
        ), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui(
            'redoc', cache_timeout=0
        ), name='schema-redoc'),
    ]