from datetime import timedelta
from rest_framework_simplejwt.tokens import Token

class EmailVerificationToken(Token):
    lifetime = timedelta(hours=24)  
    token_type = 'email_verification'

    def __init__(self, user):
        super().__init__()
        self['user_id'] = user.id
        self['email'] = user.email
