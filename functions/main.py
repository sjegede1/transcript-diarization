# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn, options
from firebase_admin import initialize_app, credentials, storage
from firebase_functions.params import StringParam, SecretParam
from flask import jsonify
import os
from services.database import initialize_db
from services.youtube import get_audio_from_youtube

print(f"Current working directory: {os.getcwd()}")

# Initialize Firebase Admin SDK
cred = credentials.Certificate("service-account.json")

initialize_app(cred, {"storageBucket": "transcription-e1dc2.firebasestorage.app"})
storage_bucket = storage.bucket()


# Initialize MongoDB
MONGODB_URI = StringParam("MONGODB_URI")
db = initialize_db(mongodb_uri=MONGODB_URI.value)

@https_fn.on_request()
def download_audio_from_youtube(req: https_fn.Request) -> https_fn.Response:
    print("REQUEST BODY:")
    print(req.get_json())
    url = req.get_json().get("url")
    print(f"Downloading audio from {url}")
    get_audio_from_youtube(url=url, storage_bucket=storage_bucket, videos_collection=db["videos"])
    return https_fn.Response(f"Downloaded audio from {url}")