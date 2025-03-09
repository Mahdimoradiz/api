from django.db.models import Max, Min
import random
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.views import APIView
from post.models import Post, Like, Save, Comment
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
import moviepy as mp
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework.generics import ListAPIView
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
import io
from post.serializers import (
    AddCommentSerializer,
    PostSerializer,
    LikeSerializer,
    SavePostSerializer,
    CommentSerializer,
    ReelSerializer,
    ReplySerializer,
    UploadPostSerializer
)


class PostListView(APIView):
    pagination_class = PageNumberPagination

    def get(self, request):
        posts = Post.objects.filter(post_type='post')
        paginator = self.pagination_class()
        paginator.page_size = 3
        result_page = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PostDetailView(APIView):
    def get(self, request, id):
        post = get_object_or_404(Post, id=id)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)




class UploadPostView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        post_type = request.data.get("post_type", "feed")
        limits = settings.VIDEO_LIMITS.get(post_type, settings.VIDEO_LIMITS["feed"])
        print(f"Token: {request.headers.get('Authorization')}")


        total_size = sum(f.size for f in request.FILES.values())
        if total_size > 500 * 1024 * 1024:  # 500MB
            return Response({"detail": "The file size is larger than 500 MB"},
                            status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)


        for f in request.FILES.values():
            if f.content_type not in settings.ALLOWED_FILE_TYPES:
                return Response({"detail": "Unsupported file type"},
                                status=status.HTTP_400_BAD_REQUEST)

    
        for f in request.FILES.values():
            if f.content_type.startswith("video/"):
                try:
                    video_data = io.BytesIO(f.read()) 
                    video = mp.VideoFileClip(video_data)
                    if video.duration > limits["duration"]:
                        return Response({"detail": "Video duration exceeds limit"},
                                        status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({"detail": f"Error processing video: {str(e)}"},
                                    status=status.HTTP_400_BAD_REQUEST)


        serializer = UploadPostSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"detail": str(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikeCreateDestroyView(generics.GenericAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        global post_id
        post_id = request.data.get('post')
        user = request.user
        post = Post.objects.get(id=post_id)

        like, created = Like.objects.get_or_create(post=post, user=user)

        if created:
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "already like this post"}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = request.user
        post = Post.objects.get(id=post_id)

        try:
            like = Like.objects.get(post=post, user=user)
            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Like.DoesNotExist:
            return Response({"detail": "like not found"}, status=status.HTTP_404_NOT_FOUND)


class RandomPostPagination(PageNumberPagination):
    page_size = 3


class ExploreListView(ListAPIView):
    serializer_class = PostSerializer
    pagination_class = RandomPostPagination

    def get_queryset(self):
        return Post.objects.order_by('?')


class SavePostView(generics.GenericAPIView):
    queryset = Save.objects.all()
    serializer_class = SavePostSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        global post_id
        post_id = request.data.get('post')
        user = request.user
        post = Post.objects.get(id=post_id)

        save, created = Save.objects.get_or_create(post=post, user=user)

        if created:
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "already save this post"}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = request.user
        post = Post.objects.get(id=post_id)

        try:
            save = Save.objects.get(post=post, user=user)
            save.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Save.DoesNotExist:
            return Response({"detail": "save not found"}, status=status.HTTP_404_NOT_FOUND)


class CommentAPIView(APIView):
    def get(self, request, post_id):
        # Use the related name to filter comments for a specific post
        comments = Comment.objects.filter(post__id=post_id)  # or simply post=post_id
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class AddCommentView(APIView):
    def post(self, request, post_id):
        print(request.data)
        # Get the post for which the comment is being made
        post = get_object_or_404(Post, id=post_id)

        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        # Create new comment with the user specified
        serializer = AddCommentSerializer(data=request.data)
        if serializer.is_valid():
            # Assign the user who is making the comment and the post
            comment = serializer.save(post=post, user=request.user)
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddReplyView(APIView):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)

        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = ReplySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(comment=comment, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReelListView(APIView):
    pagination_class = PageNumberPagination

    def get(self, request):
        posts = Post.objects.filter(post_type='reel')
        paginator = self.pagination_class()
        paginator.page_size = 3
        result_page = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
