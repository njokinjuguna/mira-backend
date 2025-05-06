import io
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from mira.api.router import detect_intent
from mira.api.handlers.general_qa import answer_general_question
from mira.api.handlers.image_search import search_images
from mira.api.handlers.showroom_info import get_showroom_response
from mira.utils.drive_utils import load_drive_service, download_image
from mira.utils.image_preprocessor import SERVICE_ACCOUNT

# ✅ Initialize the session store for managing sessions
session_store = {}

app = FastAPI()
print("✅ Mira backend booting...")

@app.get("/")
def read_root():
    return {"status": "Mira backend is running"}

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

os.makedirs("generated_sketches", exist_ok=True)
app.mount("/generated_sketches", StaticFiles(directory="generated_sketches"), name="sketches")

# ✅ Allow frontend (Next.js) to call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mira-frontend-3tsc-qod7bjgbm-njokinjugunas-projects.vercel.app",
                   "https://miracundointeriordesign.com",  # ✅ optional if you use custom domain
                   "http://localhost:3000"
                   ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/search")
async def search(request: Request):
    data = await request.json()
    query = data.get("query", "").strip()
    print(f"[SEARCH] Received query: {query}")
    if not query:
        return {"error": "Query cannot be empty."}
    result = search_images(query)
    print(f"[SEARCH] Returning {len(result)} results.")
    return {"results": result}

@app.get("/image/{image_id}")
async def serve_drive_image(image_id: str):
    drive_service = load_drive_service()
    img = download_image(drive_service, image_id)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/jpeg")

@app.post("/ask")
async def ask_general_question(request: Request):
    data = await request.json()
    question = data.get("question", "").strip()
    print(f"[ASK] Received question: {question}")
    if not question:
        return {"error": "Question cannot be empty."}
    answer = answer_general_question(question)
    print(f"[ASK] Answer generated.")
    return {"answer": answer}

@app.post("/showroom")
async def showroom(request: Request):
    data = await request.json()
    query = data.get("query", "").strip()
    print(f"[SHOWROOM] Received showroom query: {query}")
    if not query:
        return {"error": "Query cannot be empty."}
    answer = get_showroom_response(query)
    print(f"[SHOWROOM] Answer prepared.")
    return {"answer": answer}

@app.post("/mira")
async def mira_router(request: Request):
    data = await request.json()
    query = data.get("query", "").strip()
    session_id = data.get("session_id")
    print(f"[MIRA] Incoming session_id: {session_id}, query: {query}")

    if not query:
        return {"error": "Query cannot be empty."}

    if session_id not in session_store:
        print(f"[MIRA] New session started: {session_id}")
        session_store[session_id] = {"context": {}}

    session_context = session_store[session_id]["context"]
    intent = detect_intent(query)
    print(f"[MIRA] Detected intent: {intent}")

    if intent == "search":
        results = search_images(query)
        session_context["last_search_results"] = results
        print(f"[MIRA] Found {len(results)} search results.")
        return {
            "type": "search",
            "results": results
        }

    elif intent == "showroom":
        answer = get_showroom_response(query)
        session_context["last_showroom_query"] = query
        print(f"[MIRA] Prepared showroom answer.")
        return {
            "type": "showroom",
            "answer": answer
        }

    elif intent == "follow_up_cost":
        print(f"[MIRA] Handling follow-up cost question.")
        return {
            "type": "cost",
            "answer": "For a detailed quotation, please consult our interior design team. They will help you based on the exact dimensions, finishes, and layout you prefer."
        }

    else:
        answer = answer_general_question(query)
        session_context["last_general_question"] = query
        print(f"[MIRA] Answered general question.")
        return {
            "type": "ask",
            "answer": answer
        }



# ✅ Run the app in production (required by Railway)
if __name__ == "__main__":
    print("✅ Mira backend booting...")  # <-- Add this
    uvicorn.run("mira.api.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=False)

