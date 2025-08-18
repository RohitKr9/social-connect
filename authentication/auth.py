from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db import models



class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, identifier=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        try:
            user = UserModel.objects.get(
                models.Q(email=identifier) | models.Q(username=identifier)
            )
        except UserModel.DoesNotExist:
            return None
       
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None