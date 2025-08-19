from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework  import status
from .serializers import UserProfileSerializer, UserFollowSerializer, ProfileListSerializer
from .models import Profile, UserFollow
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .permissions import CanViewProfile


User = get_user_model()

# Create your views here.
class UserProfileDetailView(GenericAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, CanViewProfile]

    def get(self, request, user_id):
        try:
            user = get_object_or_404(User, id=user_id)
            profile = get_object_or_404(Profile, user=user)

            self.check_object_permissions(request, profile)
            
            serializer = self.get_serializer(profile, context={'request': request})
            
            return Response({
                'profile': serializer.data,
                'can_edit': request.user == user if request.user.is_authenticated else False
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)

class UserProfileEditView(GenericAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            #profile = get_object_or_404(Profile, user=user)
            profile, created = Profile.objects.get_or_create(user=self.request.user)

            serializer = self.get_serializer(profile, data=request.data, partial=True, context={'request':request})

            if serializer.is_valid():
                serializer.save()
                return Response({
                    'profile':serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'error':'profile update failed'
            },status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({
                'error': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)

class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserFollowSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UnfollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        following_id = request.data.get('following')
        try:
            follow_instance = UserFollow.objects.get(follower=request.user, following_id=following_id)
            follow_instance.delete()
            return Response({"detail": "Unfollowed successfully."}, status=status.HTTP_204_NO_CONTENT)
        except UserFollow.DoesNotExist:
            return Response({"detail": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)

class FollowingListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserFollowSerializer

    def get_queryset(self):
        return UserFollow.objects.filter(follower=self.request.user)

class FollowersListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserFollowSerializer

    def get_queryset(self):
        return UserFollow.objects.filter(following=self.request.user)
    
class ProfileListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileListSerializer
    def get_queryset(self):
        return Profile.objects.all()
