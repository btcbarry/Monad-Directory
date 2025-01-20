from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from monad_gpt import MonadAssistant

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add a test endpoint
@app.get("/")
async def root():
    return {"status": "ok", "message": "Monad Chat Backend is running"}

# Initialize Monad Assistant
assistant = MonadAssistant()

class ChatRequest(BaseModel):
    question: str  # Changed from message to question

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = assistant.ask(request.question)  # Changed from message to question
        return {"message": response}  # Keep this as message for frontend compatibility
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
