import os
import io
import json
import base64
from PIL import Image
from google.oauth2 import service_account
from googleapiclient.discovery import build

def load_drive_service():
    encoded_creds = os.getenv("GOOGLE_CREDENTIALS_BASE64")  # ✅ This must match Railway
    if not encoded_creds:
        raise ValueError("Missing GOOGLE_CREDENTIALS_BASE64 in environment")

    creds_dict = json.loads(base64.b64decode(encoded_creds).decode())
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=credentials)

def list_folders(drive_service, parent_folder_id):
    query = f"'{parent_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get("files", [])

def list_images_in_folder(drive_service, folder_id):
    query = f"'{folder_id}' in parents and mimeType contains 'image/'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get("files", [])

def get_all_images_with_categories(drive_service, root_folder_id):
    image_data = []
    folders = list_folders(drive_service, root_folder_id)
    for folder in folders:
        folder_id = folder["id"]
        category = folder["name"]
        images = list_images_in_folder(drive_service, folder_id)
        for img in images:
            image_data.append({
                "id": img["id"],
                "name": img["name"],
                "category": category
            })
    return image_data

def download_image(drive_service, file_id):
    request = drive_service.files().get_media(fileId=file_id)
    image_data = io.BytesIO(request.execute())
    return Image.open(image_data).convert("RGB")
