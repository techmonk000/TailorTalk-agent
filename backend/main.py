from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from agent import langgraph_response

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
    return {"response": reply}
