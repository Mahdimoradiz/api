from django.contrib import admin
from . import models

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user",)


@admin.register(models.Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("user",)


admin.site.register(models.Block)
