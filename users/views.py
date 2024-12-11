from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from utilities.firebase import create_firebase_user, login_firebase_user, logout_firebase_user
from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer
from .models import CustomUser
from rest_framework.permissions import IsAuthenticated
from utilities.authentication import FirebaseAuthentication
from utilities.utils import ResponseInfo
from django.http import JsonResponse
from rest_framework.decorators import api_view
import requests
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import auth
import json
import smtplib

load_dotenv()

class RegisterAPIView(CreateAPIView):
    """
    API view for registering a new user.
    """
    permission_classes = ()
    authentication_classes = ()
    serializer_class = RegisterSerializer

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(RegisterAPIView, self).__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        `POST` method to register a new user.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        display_name = serializer.validated_data.get('display_name', None)  # Optional field

        try:
            # Create the user in Firebase
            firebase_user = create_firebase_user(email, password, display_name)

            # Save the user to the CustomUser model
            CustomUser.objects.create(uid=firebase_user.uid, email=email, display_name=display_name)

            self.response_format["data"] = {"uid": firebase_user.uid, "email": email, "display_name": display_name}
            self.response_format["message"] = ["User registered successfully"]
            return Response(self.response_format, status=status.HTTP_201_CREATED)

        except Exception as e:
            self.response_format["error"] = str(e)
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(CreateAPIView):
    """
    API view for logging in a user using Firebase.
    """
    permission_classes = ()
    authentication_classes = ()
    serializer_class = LoginSerializer

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(LoginAPIView, self).__init__(**kwargs)

    def post(self, request, *args, **kwargs):
        """
        `POST` method to log in a user with Firebase.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = login_firebase_user(email, password)
            self.response_format["data"] = user
            self.response_format["message"] = ["Login successful"]
            return Response(self.response_format, status=status.HTTP_200_OK)
        except Exception as e:
            self.response_format["error"] = str(e)
            self.response_format["message"] = ["Login failed"]
            return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(CreateAPIView):
    """
    API view for logging out a user.
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (FirebaseAuthentication,)
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        """
        `POST` method to log out a user.
        """
        uid = request.user.uid
        logout_firebase_user(uid)

        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

# views.py

Your code snippet outlines a Django view function for generating and sending a password reset link via email. Below is an explanation of the code along with potential improvements:

Code Review & Improvements

1. Error Handling:

The generate_password_reset_link function has a generic except block that returns the exception as a string. This could expose sensitive server information. Use specific exceptions, or log the error securely and provide a user-friendly message instead.



2. Environment Variables:

Ensure EMAIL_ID and EMAIL_PASSWORD are securely stored and properly configured in the environment. Use libraries like python-decouple or django-environ for safer handling of environment variables.



3. Hardcoded SMTP Settings:

Consider using Django’s built-in email functionalities (django.core.mail) for sending emails, which is more secure and integrates better with Django settings.



4. CSRF Exemption:

The @csrf_exempt decorator removes CSRF protection, which is risky. If possible, use CSRF tokens or restrict the endpoint's access.



5. Use JSON Response Properly:

When returning JSON responses, ensure that the status codes and messages adhere to API best practices.



6. Validation:

Check if the email is registered in the system before generating the reset link.



7. SMTP Connection Handling:

Add error handling for the SMTP connection and avoid calling .quit() if the connection fails prematurely.



8. Send Emails in Background:

Sending emails synchronously could block the request thread. Use a task queue like Celery or Django-Q for sending emails asynchronously.




Revised Code

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import auth
import json
import smtplib
import os

@csrf_exempt
def generate_password_reset_link(request):
    if request.method == "POST":
        try:
            # Parse the request body
            data = json.loads(request.body)
            email = data.get("email")
            
            if not email:
                return JsonResponse({"error": "Email is required"}, status=400)

            # Generate the reset link
            link = auth.generate_password_reset_link(email)
            
            # Send the email
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.starttls()
                smtp.login(os.getenv('EMAIL_ID'), os.getenv('EMAIL_PASSWORD'))
                message = f"Subject: Password Reset\n\nClick this link to reset your password: {link}"
                smtp.sendmail(os.getenv('EMAIL_ID'), email, message)

            return JsonResponse({"message": "Password reset link sent successfully."}, status=200)

        except ValueError as e:
            return JsonResponse({"error": "Invalid email address."}, status=400)
        except smtplib.SMTPException as e:
            return JsonResponse({"error": "Failed to send email."}, status=500)
        except Exception as e:
            return JsonResponse({"error": "An unexpected error occurred."}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


@api_view(['POST'])
def refresh_id_token(request):
    refresh_token = request.data.get('refresh_token')
    
    if not refresh_token:
        return JsonResponse({'error': 'Refresh token is required'}, status=400)
    
    FIREBASE_WEB_API_KEY = settings.FIREBASE_WEB_API_KEY

    # Firebase endpoint to refresh ID token
    url = f"https://securetoken.googleapis.com/v1/token?key={FIREBASE_WEB_API_KEY}"
    
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        return JsonResponse(response.json())
    else:
        return JsonResponse({'error': 'Failed to refresh ID token'}, status=response.status_code)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UploadedFile  # Your model for storing file URLs
import mimetypes
import firebase_admin
from firebase_admin import storage
from rest_framework.permissions import IsAuthenticated
from utilities.firebase import upload_app_file 

class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Automatically detect content type
        mime_type, encoding = mimetypes.guess_type(file.name)
        content_type = mime_type if mime_type else 'application/octet-stream'

        try:
            # Upload the file to Firebase and get the public URL
            file_url = upload_app_file(file, 'user')

            # Save the file URL and associate it with the logged-in user
            uploaded_file = UploadedFile.objects.create(
                user=request.user,  # Associate with the logged-in user
                file_name=file.name,
                file_url=file_url
            )

            return Response({"message": "File uploaded successfully.", "file_url": uploaded_file.file_url}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def upload_file_to_firebase(file, content_type):
    # Assuming Firebase storage is initialized
    bucket = firebase_admin.storage.bucket()

    # Create a blob for the file
    blob = bucket.blob(f"uploads/{file.name}")

    # Upload the file and set the content type
    blob.upload_from_file(file, content_type=content_type)

    # Make the file publicly accessible
    blob.make_public()

    # Return the public URL of the uploaded file
    return blob.public_url



from .models import UploadedFile
from django.shortcuts import get_object_or_404

class RetrieveFileView(APIView):
    """
    View to retrieve file URLs stored in Firebase.
    """

    def get(self, request, file_id):
        # Fetch the file object using its ID
        file_obj = get_object_or_404(UploadedFile, id=file_id)

        # Retrieve the file URL from the database
        file_url = file_obj.file_url

        # Return the file URL in the response
        return Response({"file_url": file_url}, status=status.HTTP_200_OK)
