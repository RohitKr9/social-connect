from django.urls import path
from .views import UserProfileDetailView, UserProfileEditView, FollowUserView,UnfollowUserView, FollowersListView, FollowingListView, ProfileListView, PostListCreateView, PostDetailView, PostCommentCreateView, PostCommentListView, PostLikeStatusView, PostLikeToggleView, CommentDetailView, MyPostListView


urlpatterns = [
    path('api/users/<int:user_id>/', UserProfileDetailView.as_view()),
    path('api/users/me', UserProfileEditView.as_view()),
    path('api/users/follow/', FollowUserView.as_view()),
    path('api/users/unfollow/', UnfollowUserView.as_view()),
    path('api/users/following/', FollowingListView.as_view()),
    path('api/users/follower/', FollowersListView.as_view()),
    path('api/users/profile-list', ProfileListView.as_view()),
    path('api/users/myposts/', MyPostListView.as_view()),
    path('api/posts/', PostListCreateView.as_view()), #create list
    path('api/posts/<int:pk>/', PostDetailView.as_view()), #get put delete
    path('api/posts/<int:pk>/like/', PostLikeToggleView.as_view()), #like unlike
    path('api/posts/<int:pk>/like-status/', PostLikeStatusView.as_view()),
    path('api/posts/<int:pk>/comments/', PostCommentCreateView.as_view()),
    path('api/posts/<int:pk>/comments-list/', PostCommentListView.as_view()),
    path('api/comments/<int:pk>/', CommentDetailView.as_view())
]