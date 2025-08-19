from django.urls import path
from .views import UserProfileDetailView, UserProfileEditView


urlpatterns = [
    path('api/users/<int:user_id>/', UserProfileDetailView.as_view()),
    path('api/users/me/', UserProfileEditView.as_view()),
]