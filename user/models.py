"""
Custom User Model in Django

This implementation extends Django's AbstractBaseUser to create a custom user model.
It includes strong password validation, user authentication management, and additional
profile settings such as notification preferences, privacy settings, and account security.
"""

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import re
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

# ================================
# Custom User Manager
# ================================
class UserManager(BaseUserManager):
    """
    Custom manager for the User model, handling user creation and password validation.
    """
    def validate_password(self, password):
        """Strong password validation with multiple security checks"""
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError("Password must contain at least one special character")
        
    def create_user(self, username, email, password=None):
        """Creates and returns a regular user with the given credentials"""
        if not username:
            raise ValueError("Users must have a username")
        if password is None:
            raise ValueError("Password must be set")
        
        self.validate_password(password)
        username = username.lower()
        
        user = User(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        """Creates and returns a superuser with admin privileges"""
        user = self.create_user(
            username,
            email=email,
            password=password,
        )
        user.is_admin = True
        user.is_active = True  
        user.save(using=self._db)
        return user

# ================================
# Custom User Model
# ================================
class User(AbstractBaseUser):
    """
    Custom user model extending AbstractBaseUser, supporting unique username authentication.
    """
    username = models.CharField(max_length=50, unique=True, verbose_name="username")
    email = models.EmailField(max_length=255, unique=True, verbose_name="email")
    date_joined = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    last_activity = models.DateTimeField(auto_now=True, blank=True, null=True)
    last_login = models.DateTimeField(auto_now=True, blank=True, null=True)
    password_changed_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    # User permissions and settings
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    account_locked = models.BooleanField(default=False)
    show_email = models.BooleanField(default=False)
    show_birthday = models.BooleanField(default=False)
    
    # Notification Preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['-date_joined']
        indexes = [models.Index(fields=['username', 'email'])]
    
    # ================================
    # Authentication and Security Methods
    # ================================
    def increment_failed_login(self):
        """Increase failed login attempts and lock account if threshold is reached"""
        self.failed_login_attempts += 1
        self.last_login_attempt = timezone.now()
        if self.failed_login_attempts >= 5: 
            self.account_locked = True
        self.save()
    
    def reset_failed_login(self):
        """Reset failed login attempts and unlock account"""
        self.failed_login_attempts = 0
        self.account_locked = False
        self.save()
    
    def check_password_age(self):
        """Check if password age exceeds 90 days for security enforcement"""
        password_age = timezone.now() - self.password_changed_at
        return password_age > timedelta(days=90) 
    
    # ================================
    # User Representation and Permissions
    # ================================
    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        """Check if the user has a specific permission"""
        return True

    def has_module_perms(self, app_label):
        """Check if the user has permissions to access a module"""
        return True

    @property
    def is_staff(self):
        """Check if the user is part of the staff (admin users)"""
        return self.is_admin