from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from monad_gpt import MonadAssistant

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware with more permissive settings
origins = [
    "https://www.monaddirectory.xyz",
    "https://monaddirectory.xyz",
    "http://localhost:3000",
    "http://localhost:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,  # Changed to False since we're not using credentials
    allow_methods=["GET", "POST", "OPTIONS"],  # Explicitly list methods
    allow_headers=["Content-Type", "Accept"],  # Explicitly list headers
)

# Initialize Monad Assistant
try:
    assistant = MonadAssistant()
    logger.info("MonadAssistant initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize MonadAssistant: {str(e)}")
    raise

class ChatRequest(BaseModel):
    question: str

@app.get("/")
async def root():
    logger.debug("Root endpoint called")
    return {"status": "ok", "message": "Monad Chat Backend is running"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Received question: {request.question}")
        response = assistant.ask(request.question)
        logger.info("Successfully generated response")
        return JSONResponse(
            content={"message": response},
            headers={
                "Access-Control-Allow-Origin": "https://www.monaddirectory.xyz"
            }
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
