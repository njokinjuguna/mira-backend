
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import pickle
from tqdm import tqdm
from PIL import Image
from mira.utils.drive_utils import load_drive_service, download_image
from mira.utils.model_loader import load_openclip, load_blip, generate_embedding, generate_caption
from dotenv import load_dotenv

load_dotenv()

# Load ENV
SERVICE_ACCOUNT = os.getenv("SERVICE_ACCOUNT_JSON")
FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
CACHE_PATH = "mira/data/embeddings_cache.pkl"
MAX_RETRIES = 3
SKIPPED_LOG_PATH = "skipped_images.log"

def test_permissions(service, folder_id):
    """Test if the service account can access all files and folders."""
    items = service.files().list(q=f"'{folder_id}' in parents and trashed = false").execute().get('files', [])
    for item in items:
        print(f"Item Name: {item['name']}, MIME Type: {item['mimeType']}")
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            test_permissions(service, item['id'])  # Recursively check subfolders

def get_all_images_recursively(service, folder_id):
    """Recursively fetch all images from the folder and subfolders with pagination."""
    images = []
    page_token = None

    # 🏷️ Get the name of the current folder to use as category
    folder = service.files().get(fileId=folder_id, fields='name').execute()
    category = folder.get('name', 'Unknown').lower()

    while True:
        response = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            pageSize=100,
            pageToken=page_token
        ).execute()
        items = response.get('files', [])
        for item in items:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                images.extend(get_all_images_recursively(service, item['id']))
            elif item['mimeType'].startswith('image/'):
                images.append({
                    "id": item['id'],
                    "name": item['name'],
                    "category": category  # 🌟 Smart folder category here
                })

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

    return images


def preprocess_images():
    print("🔐 Connecting to Google Drive...")
    drive_service = load_drive_service(SERVICE_ACCOUNT)

    print("📁 Fetching image list...")
    images = get_all_images_recursively(drive_service, FOLDER_ID)
    print(f"✅ Found {len(images)} images.")

    print("🧠 Loading models...")
    model, preprocess, tokenizer = load_openclip()
    caption_model, caption_processor = load_blip()

    all_data = []
    skipped_images = []

    for img in tqdm(images, desc="🧠 Embedding images"):
        retries = 0
        while retries < MAX_RETRIES:
            try:
                print(f"Processing image: {img['name']} (ID: {img['id']})")  # Debugging log
                pil_img = download_image(drive_service, img["id"])
                embed = generate_embedding(pil_img, model, preprocess)
                caption = generate_caption(pil_img, caption_model, caption_processor)

                all_data.append({
                    "id": img["id"],
                    "name": img["name"],
                    "category": img["category"],
                    "embedding": embed.tolist(),
                    "caption": caption
                })
                break  # Success, exit retry loop
            except Exception as e:
                retries += 1
                if retries == MAX_RETRIES:
                    print(f"❌ Failed to embed image {img['name']} after {MAX_RETRIES} retries: {e}")
                    skipped_images.append({"id": img["id"], "name": img["name"], "error": str(e)})

    with open(CACHE_PATH, "wb") as f:
        pickle.dump(all_data, f)
    print(f"✅ Saved embeddings to {CACHE_PATH}")

    if skipped_images:
        print(f"❌ Writing skipped images log to {SKIPPED_LOG_PATH}")
        with open(SKIPPED_LOG_PATH, "w") as log_file:
            for img in skipped_images:
                log_file.write(f"ID: {img['id']}, Name: {img['name']}, Error: {img['error']}\n")

if __name__ == "__main__":
    print("Testing permissions...")
    drive_service = load_drive_service(SERVICE_ACCOUNT)
    test_permissions(drive_service, FOLDER_ID)  # Optionally test permissions

    preprocess_images()
