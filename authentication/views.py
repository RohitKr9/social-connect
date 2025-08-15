from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserSerializer
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

class RegisterView(GenericAPIView):
    serializer_class = CustomUserSerializer

    def post(self, request):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        user = serializer.save()

        print("Printing user here-----Behold",  CustomUserSerializer(user).data)

        return Response({'user':CustomUserSerializer(user).data},
                        status=status.HTTP_201_CREATED)
