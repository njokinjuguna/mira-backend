import io
from googleapiclient.discovery import build
from google.oauth2 import service_account
from PIL import Image

def load_drive_service(service_account_file):
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
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
