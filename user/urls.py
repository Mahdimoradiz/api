from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('auth/user/', views.UserDetailView.as_view(), name='user_detail'),
    path('csrf/', views.get_csrf_token, name='get_csrf_token'),
    path('register/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
