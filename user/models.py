from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):

        if not username:
            raise ValueError("Users must have an username")
        
        if password is None:
            raise ValueError("Password must be set.")
        
        username = username.lower()
        
        user = User(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        """
        Creates and saves a superuser with the given username and password.
        """

        user = self.create_user(
            username,
            email=email,
            password=password,
        )
        user.is_admin = True
        user.is_active = True  
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(
        max_length=50,
        verbose_name="username",
        unique=True,
    )
    email = models.EmailField(
        max_length=255,  
        verbose_name="email",
        unique=True,
    )

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
    
    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


