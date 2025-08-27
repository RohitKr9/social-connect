from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CustomUser
from .serializers import CustomUserSerializer, ChangePasswordSerializer
from django.contrib.auth import get_user_model
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken,TokenError, UntypedToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import os
from .utility import EmailVerificationToken

User = get_user_model()

class RegisterView(GenericAPIView):
    serializer_class = CustomUserSerializer

    def post(self, request):    
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        user = serializer.save(is_active = False)

        token = EmailVerificationToken(user)

        current_site = os.getenv('DOMAIN', 'http://localhost:8000')
        relative_link = reverse('email-verify')
        abs_url = f"{current_site}{relative_link}?token={str(token)}"

        subject = 'Verify your email'
        message = f'Hi {user.username},\n\nClick the link to verify your email:\n{abs_url}'

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        return Response({'user':CustomUserSerializer(user).data},
                        status=status.HTTP_201_CREATED)
    

class EmailVerifyView(APIView):
    def get(self, request):
        token_str = request.query_params.get('token')
        if not token_str:
            return Response({'error': 'Token is required'}, status=400)

        try:
            token = UntypedToken(token_str)
            user_id = token['user_id']
            user = User.objects.get(id=user_id)

            if not user.is_active:
                user.is_active = True
                user.save()

            return Response({'message': 'Email verified successfully'}, status=200)
        except (TokenError, InvalidToken):
            return Response({'error': 'Invalid or expired token'}, status=400)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

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
