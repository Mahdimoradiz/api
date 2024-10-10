from rest_framework.serializers import ModelSerializer
from .models import Post, Like, Save, Comment, Reply
from rest_framework import serializers
from profiles.abbreviation import NumberUtils
from django.contrib.contenttypes.models import ContentType

class AddCommentSerializer(serializers.ModelSerializer):
    replay_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'text', 'user', 'post', 'created_at', 'replay_count', 'file']


    def validate_post(self, value):

        if isinstance(value, list):
            if len(value) == 1:
                return value[0] 
            else:
                raise serializers.ValidationError("Post field should not be a list or must contain exactly one element.")
        return value

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError("Comment text cannot be empty.")
        return value

    def validate_file(self, value):
        # Ensure that the uploaded file is an image or video
        if value and not value.name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.mp4')):  # Include other video formats as needed
            raise serializers.ValidationError("Only image or video files are allowed.")
        if value and value.size > 5 * 1024 * 1024:  # 5 MB limit
            raise serializers.ValidationError("File size must be less than 5 MB.")
        return value
    
    def get_replay_count(self, obj):
        replay_count = obj.replies.count()  # Assuming there is a related name 'replies' for replies
        return replay_count
    
    
    

class ReplySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    profile_image = serializers.ImageField(source='user.profiles.picture', read_only=True)

    class Meta:
        model = Reply
        fields = ['id', 'text', 'user', 'comment', 'created_at', 'username', 'profile_image']



class PostSerializer(ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    profile_image = serializers.ImageField(source='user.profiles.picture', read_only=True)
    
    
    class Meta:
        model = Post
        fields = ['id', 'description', 'created_at', 'updated_at', 'file', 'username', 'profile_image']



class LikeSerializer(ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'created_at']


class SavePostSerializer(ModelSerializer):
    class Meta:
        model = Save
        fields = ['id', 'post', 'user', 'created_at']
        
        
class ReelSerializer(ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    profile_image = serializers.ImageField(source='user.profiles.picture', read_only=True)
    
    
    class Meta:
        model = Post
        fields = ['id', 'description', 'created_at', 'updated_at', 'file', 'username', 'profile_image']
        

class CommentSerializer(ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    profile_image = serializers.ImageField(source='user.profiles.picture', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'text', 'user', 'post', 'created_at', 'username', 'profile_image', 'file']
        
    


class AddPostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"