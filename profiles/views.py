from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .models import Profile, Block
from .serializers import ProfileSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from profiles.models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Follow
from rest_framework import generics

class ProfileSearchView(generics.ListAPIView):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        query = self.request.query_params.get('search', None)
        if query is not None:

            return Profile.objects.filter(user__username__icontains=query)
        return Profile.objects.none()
    
    
class ProfileDetailView(APIView):
    def get(self, request, identifier):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        # Retrieve profile by ID or slug
        if identifier.isdigit():
            profile = get_object_or_404(Profile, id=identifier)
        else:
            profile = get_object_or_404(Profile, slug=identifier)
        
        target_user = profile.user  # Retrieve the associated user of the profile

        # Check if either user has blocked the other
        block_response = self.check_blocked(request.user, target_user)
        if block_response:
            return block_response

        # Serialize and return profile data
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def check_blocked(self, user, target_user):
        """Checks if the user or the target_user has blocked each other."""
        if Block.objects.filter(blocker=user, blocked=target_user).exists():
            return Response({"error": "You have blocked this user"}, status=status.HTTP_403_FORBIDDEN)
        
        if Block.objects.filter(blocker=target_user, blocked=user).exists():
            return Response({"error": "You are blocked by this user"}, status=status.HTTP_403_FORBIDDEN)
        
        return None



@api_view(['POST'])
def follow_user(request, user_id):
    if request.user.is_authenticated:
        if request.user.id == user_id:
            return Response({"error": "You cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            followed_user = User.objects.get(id=user_id)
            follow, created = Follow.objects.get_or_create(user=request.user, followed_user=followed_user)
            if created:
                return Response({"message": "Followed successfully"}, status=status.HTTP_201_CREATED)
            return Response({"message": "Already following"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['DELETE'])
def unfollow_user(request, user_id):
    if request.user.is_authenticated:
        try:
            followed_user = User.objects.get(id=user_id)
            
            if followed_user == request.user:
                return Response({"error": "You cannot unfollow yourself"}, status=status.HTTP_400_BAD_REQUEST)
            
            follow = Follow.objects.get(user=request.user, followed_user=followed_user)
            follow.delete()
            return Response({"message": "Unfollowed successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response({"error": "Not following this user"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)


class ProfileEditView(APIView):
    def put(self, request, slug):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = get_object_or_404(Profile, slug=slug)

        if profile.user == request.user:
            serializer = ProfileSerializer(profile, data=request.data)  
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)  
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
        else:
            return Response({"error": "You do not have permission to edit this profile"}, status=status.HTTP_403_FORBIDDEN)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileListView(APIView):    
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10
    
    def get(self, request):
        profiles = Profile.objects.all()
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(profiles, request)
        serializer = ProfileSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    

class BlockedListView(APIView):
    def get(self, request, slug=None):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        blocked_users = Block.objects.filter(blocker=request.user).select_related('blocked')
        blocked_list = [{"username": block.blocked.username} for block in blocked_users]
        return Response(blocked_list, status=status.HTTP_200_OK)
    
    

class SearchUser(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')
        if query:
            profiles = Profile.objects.filter(name__icontains=query) | Profile.objects.filter(user__username__icontains=query)
            serializer = ProfileSerializer(profiles, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response([], status=status.HTTP_200_OK)