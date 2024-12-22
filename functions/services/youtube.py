import os
import firebase_admin
from firebase_admin import storage
from pytube import YouTube
from pymongo.collection import Collection
import yt_dlp
from datetime import datetime

def get_audio_from_youtube(url: str, storage_bucket: storage.bucket, videos_collection: Collection, folder_path: str="audio") -> None:
    audio_file_path = ""
    metadata = {}
    print(f"Downloading audio from {url} type: {type(url)}")

    try:
        yt_dlp_opts = {
            'format': 'worstaudio/wors',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',  # Convert to WAV format
            }],
            'outtmpl': folder_path + '/%(id)s',
        }
        with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
            youtube_info = ydl.extract_info(url, download=True)
            metadata = {
                "id": youtube_info["id"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "title": youtube_info["title"],
                "description": youtube_info["description"],
                "duration": youtube_info["duration"],
                "webpage_url": youtube_info["webpage_url"]
            }
            print("METADATA:\n"+str(metadata))
        audio_file_path = f"{folder_path}/{metadata['id']}.wav"
        videos_collection.insert_one(metadata)
    except Exception as e:
        print(f"Failed to download audio from YouTube: {e}")
        raise e
     
    try:        
        # Upload to Firebase Storage
        print("Uploading audio to Firebase Storage")
        bucket = storage_bucket
        print(f"Bucket: {bucket}")
        blob = bucket.blob(f"{folder_path}/{metadata["id"]}.wav")
        blob.metadata = metadata
        print(f"Blob: {blob}")
        print(f"Uploading audio to Firebase Storage: {audio_file_path}")
        blob.upload_from_filename(audio_file_path)
        print(f"Audio uploaded to Firebase Storage: {folder_path}/{metadata["id"]}.wav")

        # Optionally, you can delete the local file after uploading
        os.remove(audio_file_path)
        print(f"Audio file deleted: {audio_file_path}")

        print(f"Audio downloaded and uploaded to Firebase Storage: {blob.public_url}")
        videos_collection.update_one({"youtube_url": url}, {"$set": {"audio_url": blob.public_url}})
        print(f"Audio URL updated in the database")
    except Exception as e:
        print(f"Failed to upload audio to firebase: {e}")
        raise e