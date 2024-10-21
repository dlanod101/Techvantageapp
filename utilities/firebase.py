import firebase_admin
from firebase_admin import credentials, auth, storage
from django.conf import settings
from rest_framework import exceptions

# Initialize Firebase App (this should only be done once in your entire project)
cred = credentials.Certificate({
  "type": "service_account",
  "project_id": "newproject-7ad97",
  "private_key_id": "375616695eee81931c663f2440dd600221ed5e03",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCrUFGvfp/I/b+i\nvee7mzJcdtbBYKUWDUksYdLik8SnewF0q350wKgq2ToxRRqICBRe45uuvZU+Y1J5\n0CKG+A5WlS63GxPJsp+MwosOKOgPdHNtgrY2aczVxNu3u2TEDY9uxXnlH5Tgu0OU\n5ofT71B5/WU2cCmfJzxgiuEVHWrZyztkGwgYhq4waO/cHgZOCE0M8SQWjZueVbhm\nNMx3z7LrPuUdk9iNCklWn8PcYet5H2Mt3VGUi38Jt12G/4E7YU8hQ0ZDXBAzghBB\n7ccvJ0/hOzi9m15am43WTOxXoSHqU7yBisifSFuT3nSjcBLqBDOoyYizocVsKuib\n4Jz2/KRhAgMBAAECggEAA21M5QTUb3HcBoZj/1XAcScTbrTfOIy1fQTL8ipgkbUd\nN1dC5VUBSDImPtwSBsyak7db4uf591CHUtZ+ClMl/kdnstQA1lUTaf5uR687zStY\nL8WgnYAKT/BrMMa34lAfIWkj4hh6ovA8Dtt5thygcIBIKQmfW4auZ4P/sqtu+sJU\noLlqKjCYzpgsKDZI7phQ5Kj1Mb/9sPJDWZi2g5VhW3v0lRhxX+Hi7ylYPEEFaajR\n3UQoXWydnZGlPub+R2iS1+2e9QH9Ijin+9UvtO719pRXSN2jmeexhoYPlZGpK0tj\n3LDmkPvQNaXCzi8BtRTf50lHbRK/J00hpAZFl8h/QQKBgQDYfgzY04ch2CwJueZ4\nYs92BCkotmUrMOs5RCuQARpbiW57uJ0E9Unchljf6LJXCizzhGhfrYESdUfa4a0h\nZ3PKCQEcAWPN7LSk71QGfgCAbRV68piqmJxlZC1GiPRIlOjYskh7j/GNfz9URANb\nmviLtwU5qFRg5tWu1ftke34uyQKBgQDKk6SQl3L0MP4R/pdneVSrGmJ4NfF7X/OE\n0r5tBzq5Cz+B/RM+iaQlh8bpG3iUGu9no5gqatovOo9gK9ER1hrGBZ32+VbwBstt\nLg0/ZjuHfRILqmpMvmye7smDHxQyxsK7LW0D2yCtYV5nRFGYPlV4qE8z1S226m1z\nWPOM1CEc2QKBgHzAXhzP/62kCPRt2H4EynHCQgmA2VmDLfjo7IVl7U9UKYNHxcum\noTJfhHU6fRIk/fQxl4eSzq7ZQFfD9eUq3RFOEQKXVnDCdvIYK342O4nF0jvv8cNU\nf8L5cBGWN9ZfYLIGQjhZoSMdcVvYeWrfKVwxUeSAuGbCfd3q1pt3giXpAoGBALjB\nx4mIV3OXa2IGDRh2dF5Jhh2VNVUMwhEWFE9kFI7IT3fC1VZoOqlwGF5qi6Konkir\n0BB/u9bvVeykid32pByO6u9hoYTw7X/6TGLSXuDHlTnGh4TO+EpMBsXsBoP4+4mz\neIXXyQnYkD0m9jQgRdvxxarEdxko3gIh0p9SqZChAoGBALnP237oWfPiGI+hn4kj\niEpAobcdxE71joQFB7xhyty1GYxc/f/GsfTUvu6lEJUQWvvl3G89gPLcGOL6kiA9\nTjk1w5DnOgnAUnmPNsjOL6k5f9RVvFWkAmixl1nWrWcK9ePd1gYYSc+m7+RC1dSw\ngHpKJ55o7aODdg0z2cDuTrY3\n-----END PRIVATE KEY-----\n",
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
