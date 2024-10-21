import firebase_admin
from firebase_admin import credentials, auth, storage
from django.conf import settings
from rest_framework import exceptions

# Initialize Firebase App (this should only be done once in your entire project)
cred = credentials.Certificate({
  "type": "service_account",
  "project_id": "newproject-7ad97",
  "private_key_id": "24e4c97b6b9314bb69162167bc129618614b2c3c",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDasP055/MD/lhM\n/D1rHB2qKEeNcTV6TmZW3nuLPaHpgCUhXlqrXb5EcCpdlTN6dZkRKKj/eF8hfBRQ\nOGzh0CKhsAhUXKWJUNjZzqBA9K27HN/O1G2cyUAuz31VEV+2stdXas0MX1aLWSV8\n3RZlfxyjJOmtFBJjJiKXdVaC/3NUXkHPx/9d64kSn/qxP59FxbB25Huzejz7z5Xq\nWsSdZeK9y5sJKVtTqImdGPlgV3A7DB36RzhhdSXdcuEDVR0vefpj61aFKaD39x76\n9uqznGLrXRwYNP4JhFS0/tTW/zAWNMyqLBToggbkhaT7UfJybIlE/U7Ei141VU6L\nlijMC8ZVAgMBAAECggEAMtsy4Cr1BAo7bZfBDq4Ipf/c9+MKTSl7Ohtd/pj0FLF0\nsQhYrH5N12uAJqgiQwmi8W8TselDsi1BKhCdHXxB+XjOzxOGeWLgMvKOqNxdpGRI\nFbinzuysLNaarlQufnWjh1QyX/yxyxENmzZs1WiUd8oHP3Up+32sUK18U1VldApT\nLqSuoaQ3w7L0kM7qHWcMuns5+Iv0wfbQre8Qyr4ZzEKWWZB4XhnIxzWco6MXQ56a\ns064ZbN5WyCtHu6DOTDLGTWnABMjduSWom7+rN40tRKVOQN5pOyO6mn4Cc17QVmk\n5dbpfFW/SIoStgNCWOrRqch9YTdl4lYazMsiBLsc5wKBgQD5e4kSnoIi4JGxpeFI\nqg8mC/6eoBIvX5xTEZjy19XKM2yPMUD+BuJdrCeD/z7XS3uYHpo5bSkuqhmJpSG2\nHWaSn25Svi2pX6UoGECiiqjU30JY+5A6BPEx3vOxBlLKKS1WVrvQBpSpAq8Qq0z/\nzw2/eHXFixKIp8RsIvJSt6XtpwKBgQDgZ4gMJRjVEV1N08UFlLbVG0EIMKS6fWSG\nfEZyjyZQWh9w9fyBcC4sqeAeJ6UxYGlN2UzeoQ0eDRetIAGhJN8rTAnqcWyzsPG3\nEnTSHnAwn8gucgEhtO9jyruBJSFS0l1zuyPi1Q546abAyl8pCrRreMIsP2niAz+V\nPCuNuA+DowKBgFlqpnFO8HORq4ZRXtJNaUqIqASweHQUP5IiT4BSTWTAU5tq2tFx\nJDbQmgUcOaiufCjEZyBH+Kep/acw0UlVdkr862yqjvESv74EGz5mliZdsojz+Phi\nhxQJxavgCVI9ueslAQGJKkT9GkPOMbXJvzKt+QAJXWYvQx5C1DlDaywnAoGBAMvd\n4uA9t5CihOSWtpB6aZuzdeJN5umxz2jKcGnVGRa4uYWzRGIHmztiXUSn+dCg6Sob\nd1VudO9PL6pNwI04ZTL9kqiVwQ6CeyY5sz3M/1l9X6yqT9LigPVlEfGi3OJUUSg5\n5MFHlC1O//p4H/m2SvC0NZtjRPtaviIDFwJaLGYHAoGBAL3Q6EFcmWeXb+MMM05V\nBhb0E9xHmcpRh8pQd+aNfnTT3n4hby/VulbY7uxRO5QQS0Caj6kU2vCKizUpxBSA\nDyaTPXDj7X8N8dom1qFJuz3lFcGmf3U2wLYjy7uy8cB2BVygy3V76zs+iuO6yz57\nZiBXjnYq7ZjxqlNWi9CT7TIP\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-6at0z@newproject-7ad97.iam.gserviceaccount.com",
  "client_id": "115858408144336071349",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-6at0z%40newproject-7ad97.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
)
firebase_admin.initialize_app(cred, {
    'storageBucket': 'newproject-7ad97.appspot.com'
})

def verify_firebase_token(id_token):
    """
    Verifies the Firebase ID token sent by the client.
    Raises exceptions if the token is invalid or expired.
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except auth.ExpiredIdTokenError:
        raise exceptions.AuthenticationFailed('Token has expired. Please log in again.')
    except auth.InvalidIdTokenError:
        raise exceptions.AuthenticationFailed('Invalid token. Please log in again.')
    except Exception as e:
        raise exceptions.AuthenticationFailed('Token authentication failed.')

def login_firebase_user(email, password):
    """
    Simulates a Firebase login using REST API.
    """
    import requests
    import json

    FIREBASE_WEB_API_KEY = settings.FIREBASE_WEB_API_KEY
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    
    payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
    })
    
    response = requests.post(url, data=payload)
    data = response.json()

    if response.status_code == 200:
        return data  # contains token and user info
    else:
        raise exceptions.AuthenticationFailed(data.get("error", {}).get("message", "Authentication failed"))

def logout_firebase_user(uid):
    """
    Revokes refresh tokens for the user, effectively logging them out.
    """
    auth.revoke_refresh_tokens(uid)

def create_firebase_user(email, password, display_name):
    """
    Creates a new Firebase user with email and password.
    """
    try:
        user = auth.create_user(email=email, password=password, display_name=display_name) 
        return user
    except Exception as e:
        raise exceptions.APIException(f'Error creating user: {str(e)}')
    
def update_user_display_name(uid, new_display_name):
    """
    Function to update Firebase user's displayName.
    """
    user = auth.update_user(
        uid,
        display_name=new_display_name  # Updating displayName
    )
    return user

import mimetypes

from firebase_admin import storage

def upload_file_to_firebase(file, path):
    # Assuming you've already initialized Firebase Storage
    bucket = firebase_admin.storage.bucket()

    # Create a blob for the file
    blob = bucket.blob(path)

    # Upload the file and set the content type
    blob.upload_from_file(file, content_type=mimetypes.guess_type(file.name)[0])

    # Optionally, make the file public or set permissions
    blob.make_public()

    return blob.public_url

def upload_app_file(file, app_name):
    """Upload file to Firebase storage under the specific app's folder."""
    path = f'{app_name}/uploads/{file.name}'
    return upload_file_to_firebase(file, path)
