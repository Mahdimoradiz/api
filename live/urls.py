from django.urls import path
from .views import (
    StreamStartView, StreamStopView, StreamListView,
    MessageListView, LikeListView, CommentListView, CommentDetailView
)

urlpatterns = [
    path('start/', StreamStartView.as_view(), name='start_stream'),
    path('stop/<int:stream_id>/', StreamStopView.as_view(), name='stop_stream'),
    path('streams/', StreamListView.as_view(), name='stream_list'),
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('likes/', LikeListView.as_view(), name='like_list'),
    path('comments/', CommentListView.as_view(), name='comment_list'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment_detail'),
]