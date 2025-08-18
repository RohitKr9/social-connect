from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserSerializer, ChangePasswordSerializer
from django.contrib.auth import get_user_model
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken,TokenError

User = get_user_model()

class RegisterView(GenericAPIView):
    serializer_class = CustomUserSerializer

    def post(self, request):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        user = serializer.save()

        return Response({'user':CustomUserSerializer(user).data},
                        status=status.HTTP_201_CREATED)

class ChangePasswordView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data = request.data, context ={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response("inside if",status=status.HTTP_404_NOT_FOUND)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_200_OK)
        except TokenError:
            return Response("inside except",status=status.HTTP_400_BAD_REQUEST)
