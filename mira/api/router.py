from mira.utils.query_preprocessor import extract_keywords  # Import updated function

def detect_intent(query: str) -> str:
    keywords = extract_keywords(query)  # Extract cleaned keywords
    print("🔎 Mira detected keywords:", keywords)  # Debugging keywords
    q = " ".join(keywords)  # Reconstruct the cleaned query (optional)

    # 🔍 Price-related keywords
    price_keywords = [
        "price", "cost", "how much", "quote", "budget", "affordable",
        "costo", "prezzo", "quanto", "preventivo", "spesa", "costa"
    ]
    if any(kw in q for kw in price_keywords):  # Check against phrases
        return "follow_up_cost"

    # 🏢 Showroom-related keywords
    showroom_keywords = [
        "showroom", "store", "location", "address", "open", "contact",
        "deliver", "delivery", "shipping", "support", "available", "map", "directions",
        "prodotti", "negozio", "come arrivare"
    ]
    if any(kw in q for kw in showroom_keywords):
        return "showroom"

    # 🎨 Image-related keywords
    image_keywords = [
        "drawing", "sketch", "design", "kitchen", "bathroom", "bedroom",
        "living", "image", "photo", "wardrobe", "sofa", "table",
        "mostrami", "disegni", "progetto", "interni", "cucina", "camera"
    ]
    if any(kw in q for kw in image_keywords):
        return "search"

    # 💬 Default fallback
    print("🔍 Intent not matched. Returning fallback.")  # Debugging fallback
    return "ask"