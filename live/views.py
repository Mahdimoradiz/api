from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .serializers import StreamSerializer, MessageSerializer, LikeSerializer, CommentSerializer
from .models import Stream, Message, Like, Comment
import uuid


class StreamStartView(APIView):
    def post(self, request):
        stream_key = str(uuid.uuid4())
        
        stream = Stream.objects.create(
            user=request.user,
            stream_key=stream_key,
            stream_title=request.data.get("stream_title"),
            is_active=True
        )
        
        serializer = StreamSerializer(stream)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StreamStopView(APIView):
    def post(self, request, stream_id):
        try:
            stream = Stream.objects.get(id=stream_id, user=request.user)
            stream.is_active = False
            stream.save()
            return Response({"message": "Stream stopped successfully."}, status=status.HTTP_200_OK)
        except Stream.DoesNotExist:
            return Response({"error": "Stream not found or not authorized."}, status=status.HTTP_404_NOT_FOUND)


class StreamListView(generics.ListAPIView):
    queryset = Stream.objects.all()
    serializer_class = StreamSerializer


class MessageListView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class LikeListView(generics.ListCreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer


class CommentListView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer