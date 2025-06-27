from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.agent import langgraph_response
from fastapi.responses import JSONResponse
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_handler(req: Request):
    data = await req.json()
    message = data.get("message", "")
    reply = langgraph_response(message)
    return JSONResponse(content={"response": reply})
