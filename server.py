from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging
from monad_gpt import MonadAssistant

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS - more permissive for troubleshooting
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily
    allow_credentials=False,  # Changed to False
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Add a test endpoint
@app.get("/")
async def root():
    return {"status": "ok", "message": "Monad Chat Backend is running"}

# Initialize Monad Assistant
try:
    assistant = MonadAssistant()
    logger.info("MonadAssistant initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MonadAssistant: {str(e)}")
    raise

class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Received question: {request.question}")
        response = assistant.ask(request.question)
        logger.info("Successfully generated response")
        return JSONResponse(
            content={"message": response},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
