from django.db import models
from django.forms import ValidationError
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from user.models import User

# Constants for default values and gender choices
DEFAULT_PROFILE_PICTURE = '/profile/avatar/user.jpg'

GENDER_CHOICES = [
    ('M', _("Male")),
    ('F', _("Female")),
    ('O', _("Other"))
]

FOLLOW_PERMISSION_CHOICES = [
    ('ALL', _("Everyone")),
    ('NONE', _("No one"))
]

# Profile Model to manage User's profile information
class Profile(models.Model):
    """
    Model to represent a user's profile including personal information,
    media, privacy settings, and statistics like followers, following, and posts count.
    """

    # Basic Information: Linking the profile to a user through a One-to-One relationship
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,  # When user is deleted, the profile is also deleted
        related_name="profiles",  # Reverse relation from User to Profile
        verbose_name=_("User")
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Name")
    )
    username = models.CharField(
        max_length=100,
        unique=True,  # Ensures that username is unique across all profiles
        verbose_name=_("Username")
    )
    slug = models.SlugField(
        unique=True,  # Unique Slug for URL paths
        blank=True,
        null=True,
        verbose_name=_("Slug")
    )
    bio = models.TextField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Bio")
    )

    # Media Fields for Profile and Cover Photos
    picture = models.ImageField(
        upload_to="image/profile/picture",  # Directory for profile pictures
        blank=True,
        null=True,
        default=DEFAULT_PROFILE_PICTURE,  # Default image if the user doesn't upload one
        verbose_name=_("Profile Picture")
    )
    cover_photo = models.ImageField(
        upload_to="image/profile/covers",  # Directory for cover photos
        blank=True,
        null=True,
        verbose_name=_("Cover Photo")
    )

    # Personal Information Fields
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Location")
    )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name=_("Website")
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Birth Date")
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,  # Choices for gender (Male, Female, Other)
        blank=True,
        null=True,
        verbose_name=_("Gender")
    )

    # Privacy Settings to manage who can see/follow the profile
    is_private = models.BooleanField(
        default=False,
        verbose_name=_("Private Account")  # Private account flag
    )
    show_birthdate = models.BooleanField(
        default=True,
        verbose_name=_("Show Birthdate")
    )
    who_can_follow = models.CharField(
        max_length=10,
        choices=FOLLOW_PERMISSION_CHOICES,  # Who can follow this profile (Everyone or No one)
        default='ALL',
        verbose_name=_("Who Can Follow")
    )

    # Statistics: Followers, Following, and Posts count
    posts_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Posts Count")
    )
    followers_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Followers Count")
    )
    following_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Following Count")
    )

    # Timestamps for tracking creation and updates
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"), # Automatically sets when profile is created
        blank=True,
        null=True
    )
    updated_at = models.DateField(
        auto_now=True,
        verbose_name=_("Updated At")  # Automatically updates on profile changes
    )

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        indexes = [
            models.Index(fields=['username']),  # Index on username for faster lookups
            models.Index(fields=['created_at']),  # Index on creation date
        ]

    def __str__(self):
        """String representation of the Profile object (returns username)"""
        return self.user.username

    def save(self, *args, **kwargs):
        """
        Override save method to generate a slug from the username if not provided.
        This allows clean URLs like /user/username/ instead of /user/123/.
        """
        if not self.slug:
            self.slug = slugify(self.username)  # Slugify the username for URL-friendly slugs
        super().save(*args, **kwargs)

    def set_default_picture(self):
        """Reset profile picture to default picture (e.g., when a user deletes their custom image)."""
        self.picture.delete(save=False)
        self.picture = DEFAULT_PROFILE_PICTURE
        self.save()

    def update_counters(self):
        """
        Update the profile statistics including the number of followers, following, and posts.
        Called after every follow/unfollow action to keep the counts accurate.
        """
        self.followers_count = self.user.followers.count()  # Count the followers of the user
        self.following_count = self.user.following.count()  # Count the users the profile follows
        self.posts_count = self.user.posts.count()  # Count the posts of the user
        self.save()

    def can_follow(self, user):
        """
        Check if a user can follow this profile based on privacy settings and block status.
        """
        if self.is_private and self.who_can_follow == 'NONE':
            return False  # Private accounts with 'None' permission can't be followed by anyone
        return not Block.objects.filter(
            blocked=self.user,
            blocker=user
        ).exists()  # Block check: if the user is blocked, they cannot follow

    def is_following(self, user):
        """Check if this profile is following a given user."""
        return Follow.objects.filter(
            user=self.user,
            followed_user=user
        ).exists()


# Follow Model for user-to-user follow relationships
class Follow(models.Model):
    """
    Represents a follow relationship between two users. A user can follow another user.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name=_("User")
    )
    followed_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",
        verbose_name=_("Followed User")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=True,
        verbose_name=_("Created At")
    )

    class Meta:
        unique_together = ('user', 'followed_user')  # Prevent duplicate follow entries
        indexes = [
            models.Index(fields=['user', 'followed_user'])  # Index to optimize lookups for followers/following
        ]

    def __str__(self):
        """String representation for the follow instance."""
        return f"{self.user.username} follows {self.followed_user.username}"

    def clean(self):
        """
        Validate that users cannot follow themselves. This is a business rule.
        """
        if self.user == self.followed_user:
            raise ValidationError(_("Users cannot follow themselves"))


# Block Model to manage blocking relationships between users
class Block(models.Model):
    """
    Represents a block relationship between two users. A user can block another user.
    When a user is blocked, the follow relationship is also deleted.
    """
    blocker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocker',
        verbose_name=_("Blocker")
    )
    blocked = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocking',
        verbose_name=_("Blocked User")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        blank=True,
        null=True
    )

    class Meta:
        unique_together = ('blocker', 'blocked')  # Prevent duplicate block relationships
        indexes = [
            models.Index(fields=['blocker', 'blocked'])  # Index to optimize block lookups
        ]

    def __str__(self):
        """String representation for the block instance."""
        return f"{self.blocker.username} blocked {self.blocked.username}"

    def clean(self):
        """
        Validate that users cannot block themselves. This is a business rule.
        """
        if self.blocker == self.blocked:
            raise ValidationError(_("Users cannot block themselves"))

    def save(self, *args, **kwargs):
        """
        Override save method to automatically remove any existing follow relationships when a block is created.
        This ensures that a blocked user cannot follow the blocker.
        """
        # Remove any existing follow relationships between the blocker and blocked user
        Follow.objects.filter(
            user=self.blocker,
            followed_user=self.blocked
        ).delete()
        Follow.objects.filter(
            user=self.blocked,
            followed_user=self.blocker
        ).delete()
        super().save(*args, **kwargs)


# Signal Handlers for automatic updates on follow/unfollow actions
@receiver(post_save, sender=Follow)
def update_follow_counts(sender, instance, created, **kwargs):
    """Update the follower/following counts when a new follow is created."""
    if created:
        instance.user.profile.following_count += 1
        instance.followed_user.profile.followers_count += 1
        instance.user.profile.save()
        instance.followed_user.profile.save()

@receiver(post_delete, sender=Follow)
def decrease_follow_counts(sender, instance, **kwargs):
    """Update the follower/following counts when a follow is deleted."""
    instance.user.profile.following_count -= 1
    instance.followed_user.profile.followers_count -= 1
    instance.user.profile.save()
    instance.followed_user.profile.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile when a new User is created."""
    if created:
        Profile.objects.create(
            user=instance,
            username=instance.username,
            name=instance.username
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Ensure the Profile exists and is saved with the User."""
    try:
        instance.profiles.save()
    except Profile.DoesNotExist:
        Profile.objects.create(
            user=instance,
            username=instance.username,
            name=instance.username
        )
