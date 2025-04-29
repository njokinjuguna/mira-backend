import pickle
import numpy as np
import torch
from mira.utils.model_loader import load_openclip
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Load image embeddings
with open("mira/data/embeddings_cache.pkl", "rb") as f:
    image_data = pickle.load(f)

# Load models
model, preprocess, tokenizer = load_openclip()
t5_tokenizer = T5Tokenizer.from_pretrained("t5-small")
reranker = T5ForConditionalGeneration.from_pretrained("t5-small")

def detect_room_type(query: str):
    query = query.lower()
    for room in ["kitchen", "bathroom", "bedroom", "library", "garden", "living room", "wardrobe"]:
        if room in query:
            return room
    return None

def clean_caption(caption: str, room_type: str = None):
    vague_starts = ["a drawing of", "a sketch of", "an illustration of"]
    caption = caption.lower()

    for wrong_room in ["kitchen", "bedroom", "library", "garden", "living room"]:
        if room_type and wrong_room in caption and wrong_room != room_type:
            caption = caption.replace(wrong_room, room_type)

    if any(caption.startswith(vs) for vs in vague_starts) and room_type:
        return f"a {room_type} sketch: {caption.split('of')[-1].strip()}"

    return caption

def search_images(query, top_k=5, threshold=0.25):
    with torch.no_grad():
        tokens = tokenizer([query])
        text_features = model.encode_text(tokens).cpu().numpy()[0]

    room_type = detect_room_type(query)
    scores = []

    for img in image_data:
        if room_type and room_type not in img.get("category", "").lower():
            continue

        score = np.dot(text_features, img["embedding"]) / (
            np.linalg.norm(text_features) * np.linalg.norm(img["embedding"])
        )
        scores.append((img, score))

    top = sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]

    filtered_results = [
        {
            "best_match": match["name"],
            "caption": clean_caption(match["caption"], room_type),
            "image_url": f"http://localhost:8000/image/{match['id']}",
            "score": float(score)
        } for match, score in top if score >= threshold
    ]

    return filtered_results if filtered_results else [{
        "message": "❌ No good match found for the given description. Try rephrasing your query."
    }]
