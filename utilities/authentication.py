from rest_framework import authentication, exceptions
from utilities.firebase import verify_firebase_token
from users.models import CustomUser

class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Custom Firebase Authentication class for Django REST framework.
    """
    def authenticate(self, request):
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None

        try:
            token_type, id_token = auth_header.split(' ')
        except ValueError:
            raise exceptions.AuthenticationFailed('Invalid token header.')

        if token_type != 'Bearer':
            raise exceptions.AuthenticationFailed('Invalid token type.')

        decoded_token = verify_firebase_token(id_token)
        uid = decoded_token.get('uid')

        # Get or create the user
        try:
            user = CustomUser.objects.get(uid=uid)
        except CustomUser.DoesNotExist:
            # If the user does not exist, create one (you can adjust this behavior)
            user = CustomUser.objects.create(uid=uid, email=decoded_token.get('email'))

        return (user, None)
