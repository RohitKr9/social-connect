from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework  import status
from .serializers import UserProfileSerializer
from .models import Profile
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
                print(serializer.data, "-----------------------")
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