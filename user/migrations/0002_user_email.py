# Generated by Django 5.1.1 on 2024-09-30 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.CharField(default=1, max_length=50, unique=True, verbose_name='email'),
            preserve_default=False,
        ),
    ]
