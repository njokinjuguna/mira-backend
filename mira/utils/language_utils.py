import requests

def translate_text(text, source_lang="auto", target_lang="en"):
    print(f"🔁 Translating to {target_lang}: {text}")
    url = "https://translate.argosopentech.com/translate"
    payload = {
        "q": text,
        "source": source_lang,
        "target": target_lang,
        "format": "text"
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["translatedText"]
    except Exception as e:
        print("Translation error:", e)
        return text


import requests


def detect_language(text):
    url = "https://translate.argosopentech.com/detect"
    payload = {"q": text}
    headers = {"Content-Type": "application/json"}

    try:
        print("🔍 Detecting language for:", text)
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        detections = response.json()

        # ✅ Validate response structure before accessing data
        if isinstance(detections, list) and len(detections) > 0 and "language" in detections[0]:
            return detections[0]['language']

        print("❌ Unexpected response format:", detections)
        return "en"

    except requests.exceptions.RequestException as e:
        print("🚨 Language detection error:", e)
        return "en"



