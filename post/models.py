from django.db import models
from user.models import User
from django.core.exceptions import ValidationError


class Post(models.Model):
    file = models.FileField(upload_to="profile/image")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=1300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    FILE_TYPES = (
        ('reel', 'Reel'),
        ('post', 'Post'),
        ('carousel', 'Carousel'),
    )

    post_type = models.CharField(max_length=10, choices=FILE_TYPES, default='post')

    def clean(self):
        file_size_mb = self.file.size / (1024 * 1024)

        if self.post_type == 'reel':
            if file_size_mb > 100:
                raise ValidationError('Rails posts cannot be larger than 100MB.')

        elif self.post_type == 'post':
            if file_size_mb > 100:
                raise ValidationError('Normal mail cannot exceed 100MB.')

        elif self.post_type == 'carousel':
            if file_size_mb > 100:
                raise ValidationError('Slide post cannot be larger than 100MB.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "post"
        verbose_name_plural = "posts"
        ordering = ["-created_at"]


class FileUploadBase(models.Model):
    file = models.FileField(upload_to="uploads/", blank=True, null=True)
    likes = models.IntegerField(default=0)

    class Meta:
        abstract = True

    def clean(self):
        if self.file:
            if not self.file.name.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                raise ValidationError("Only image files are allowed. '.png', '.jpg', '.jpeg', '.gif'")
            if self.file.size > 5 * 1024 * 1024:  # 5 MB limit
                raise ValidationError("File size must be less than 5 MB.")


class Comment(FileUploadBase):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"
        ordering = ['-created_at']


class Reply(FileUploadBase):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name='replies', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.text[:20]}"

    class Meta:
        verbose_name = "reply"
        verbose_name_plural = "replies"
        ordering = ['-created_at']


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        ordering = ['created_at']
        verbose_name = "like"
        verbose_name_plural = "likes"

    def __str__(self):
        return f'{self.user} liked {self.post}'


class Save(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ['created_at']
        verbose_name = "save"
        verbose_name_plural = "saves"


class TestPost(models.Model):
    post = models.FileField(upload_to="test/file")
