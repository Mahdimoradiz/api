from django.urls import path, include
from . import views


app_name = "post"

urlpatterns = [
    path('', views.PostListView.as_view(), name='list_view'),
    path('<int:id>/', views.PostDetailView.as_view(), name='detail_view'),
    path('upload/', views.UploadPostView.as_view(), name="upload_view"),
    path('explore/', views.ExploreListView.as_view(), name="explore_view"),
    path('like/', views.LikeCreateDestroyView.as_view(), name='like-create-destroy'),
    path('save/', views.SavePostView.as_view(), name="post_save"),
    path('<int:post_id>/comments/', views.CommentAPIView.as_view(), name='comments'),
    path('<int:post_id>/comments/add/', views.AddCommentView.as_view(), name='comments_add'),  
    path('reel/', views.ReelListView.as_view(), name="reel_list"),
    path('comment/<int:comment_id>/reply/', views.AddReplyView.as_view(), name='add-reply'),

]
