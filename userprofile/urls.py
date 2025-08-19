from django.urls import path
from .views import UserProfileDetailView, UserProfileEditView, FollowUserView,UnfollowUserView, FollowersListView, FollowingListView, ProfileListView


urlpatterns = [
    path('api/users/<int:user_id>/', UserProfileDetailView.as_view()),
    path('api/users/me/', UserProfileEditView.as_view()),
    path('api/users/follow/', FollowUserView.as_view()),
    path('api/users/unfollow/', UnfollowUserView.as_view()),
    path('api/users/following/', FollowingListView.as_view()),
    path('api/users/follower/', FollowersListView.as_view()),
    path('api/users/profile-list', ProfileListView.as_view())
]