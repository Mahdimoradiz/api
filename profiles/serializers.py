from rest_framework.serializers import ModelSerializer
from .models import Profile
from profiles.models import User,Block
from rest_framework import serializers, viewsets
from .abbreviation import NumberUtils


class ProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    username_i = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Profile
        fields = ['id', 'picture', 'bio', 'followers_count', 'following_count', 'name', 'slug', 'username_i']

    def get_followers_count(self, obj):
        followers_count = obj.user.followers.count()
        return NumberUtils(followers_count).abbreviate()

    def get_following_count(self, obj):
        following_count = obj.user.following.count()
        return NumberUtils(following_count).abbreviate()


class UserSerializer(ModelSerializer):
    class Meta:
        model = User 
        fields = ['id', 'username']


class BlockSerializer(serializers.ModelSerializer):
    blocker_username = serializers.CharField(source='blocker.username', read_only=True)
    blocked_username = serializers.CharField(source='blocked.username', read_only=True)

    class Meta:
        model = Block
        fields = ['id', 'blocker_username', 'blocked_username', 'block_date']
