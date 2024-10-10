from django.db import models
from django.utils.text import slugify
from user.models import User


DEFAULT_PROFILE_PICTURE = 'img/user.jpg'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profiles")
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    picture = models.ImageField(upload_to="image/profile/picture", blank=True, null=True, default=DEFAULT_PROFILE_PICTURE)
    slug = models.SlugField(unique=True, blank=True, null=True)
    bio = models.TextField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def set_default_picture(self):
        self.picture.delete(save=False)
        self.picture = DEFAULT_PROFILE_PICTURE
        self.save()

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = "profile"
        verbose_name_plural = "profiles"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.username)
        super().save(*args, **kwargs)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")  # کاربری که فالو می‌کند
    followed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")  # کاربری که فالو شده است
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} follows {self.followed_user.username}"


class Block(models.Model):
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking')
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocker')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"