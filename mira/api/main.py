import io
import os
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
os.makedirs("generated_sketches", exist_ok=True)
app.mount("/generated_sketches", StaticFiles(directory="generated_sketches"), name="sketches")

# ✅ Allow frontend (Next.js) to call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    drive_service = load_drive_service(SERVICE_ACCOUNT)
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

    # ✅ Fetch or initialize session memory
    if session_id not in session_store:
        print(f"[MIRA] New session started: {session_id}")
        session_store[session_id] = {"context": {}}

    session_context = session_store[session_id]["context"]

    # ✅ Detect intent
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
