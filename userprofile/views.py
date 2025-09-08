from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListAPIView,ListCreateAPIView, RetrieveUpdateDestroyAPIView,CreateAPIView,DestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework  import status
from rest_framework.pagination import PageNumberPagination
from .serializers import UserProfileSerializer, UserFollowSerializer, ProfileListSerializer, CommentSerializer, PostSerializer
from .models import Profile, UserFollow, Post, Comment, Like
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .permissions import CanViewProfile, IsOwnerOrReadOnly
from django.db.models import F, Q



User = get_user_model()

# Create your views here.
class UserProfileDetailView(GenericAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = get_object_or_404(User, id=user_id)
            profile = get_object_or_404(Profile, user=user)

            profile.update_stats()  

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
                profile.update_stats()
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
        print(request.data, "------This is the request data")
        profile = get_object_or_404(Profile, id=request.data.get('following'))
        user_to_follow = profile.user 
        print(user_to_follow.id, "------This is the user to follow")
        serializer = UserFollowSerializer(data={'following':user_to_follow.id}, context={'request': request})
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
    serializer_class = ProfileListSerializer

    def get_queryset(self):
        following_user_ids = UserFollow.objects.filter(
            follower=self.request.user
        ).values_list('following_id', flat=True)

        return Profile.objects.filter(user__id__in=following_user_ids)

class FollowersListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileListSerializer

    def get_queryset(self):
        follower_user_ids = UserFollow.objects.filter(
            following=self.request.user
        ).values_list('follower_id', flat=True)

        return Profile.objects.filter(user__id__in=follower_user_ids)

class MyPostListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user, is_active=True)
       
class ProfileListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileListSerializer
    def get_queryset(self):
        following_user_ids = UserFollow.objects.filter(
            follower=self.request.user
        ).values_list('following_id', flat=True)

        return Profile.objects.exclude(
            user__id__in=list(following_user_ids) + [self.request.user.id]
        )

class PostPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostListCreateView(ListCreateAPIView):
    
    queryset = Post.objects.filter(is_active=True)
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PostPagination
    
    def perform_create(self, serializer):
        print(self.request.user)
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user

        following_ids = UserFollow.objects.filter(
            follower=user
        ).values_list('following_id', flat=True)

        allowed_user_ids = list(following_ids) + [user.id]

        return Post.objects.filter(
            Q(user__id__in=allowed_user_ids) |
            Q(user__profile__profile_visibility='public'),
            is_active=True).order_by('-created_at')

class PostDetailView(RetrieveUpdateDestroyAPIView):
   
    queryset = Post.objects.filter(is_active=True)
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

class PostLikeToggleView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        post = get_object_or_404(Post, id=pk, is_active=True)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if created:
            post.like_count = F('like_count') + 1
            post.save(update_fields=['like_count'])
            return Response({'status': 'liked', 'message': 'Post liked successfully'})
        else:
            like.delete()
            post.like_count = F('like_count') - 1
            post.save(update_fields=['like_count'])
            return Response({'status': 'unliked', 'message': 'Post unliked successfully'})
    
    def delete(self, request, pk):
        post = get_object_or_404(Post, id=pk, is_active=True)
        like = get_object_or_404(Like, user=request.user, post=post)
        like.delete()
        post.like_count = F('like_count') - 1
        post.save(update_fields=['like_count'])
        return Response({'status': 'unliked', 'message': 'Post unliked successfully'})

class PostLikeStatusView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return Response({'is_liked': False})
        
        post = get_object_or_404(Post, id=pk, is_active=True)
        is_liked = post.likes.filter(user=request.user).exists()
        return Response({'is_liked': is_liked})

class PostCommentListView(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        post_id = self.kwargs['pk']
        return Comment.objects.filter(post_id=post_id, is_active=True)

class PostCommentCreateView(CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        post = get_object_or_404(Post, id=post_id, is_active=True)
        serializer.save(user=self.request.user, post=post)
        post.comment_count = F('comment_count') + 1
        post.save(update_fields=['comment_count'])

class CommentDetailView(DestroyAPIView):
    queryset = Comment.objects.filter(is_active=True)
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        # Update comment count
        post = instance.post
        post.comment_count = F('comment_count') - 1
        post.save(update_fields=['comment_count'])
        return Response({'message': 'Comment deleted successfully'}, 
                       status=status.HTTP_204_NO_CONTENT)