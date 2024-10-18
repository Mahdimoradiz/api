from django.contrib import admin
from . import models


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    list_per_page = 5


admin.site.register(models.Like)
admin.site.register(models.Comment)
admin.site.register(models.Reply)

admin.site.register(models.Save)
admin.site.register(models.TestPost)
