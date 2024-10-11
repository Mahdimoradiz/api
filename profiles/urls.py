from . import views
from django.urls import path, include


urlpatterns = [
    path('list/', views.ProfileListView.as_view(), name='profile_list'),
    path('<slug:identifier>/', views.ProfileDetailView.as_view(), name="profile_detail"),
    path('<slug:identifier>/update', views.ProfileEditView.as_view(), name="profile_eite"),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('blocked-users/', views.BlockedListView.as_view(), name='blocked-list'), 
    path('search-users/', views.ProfileSearchView.as_view(), name='profile-search'),
    path('profile/<int:user_id>/following-status/', views.following_status, name='following_status'),
]
