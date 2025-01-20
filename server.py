from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from monad_gpt import MonadAssistant

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Log all requests middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Incoming request: {request.method} {request.url}")
    logger.debug(f"Headers: {request.headers}")
    response = await call_next(request)
    logger.debug(f"Response status: {response.status_code}")
    logger.debug(f"Response headers: {response.headers}")
    return response

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.monaddirectory.xyz"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Explicit OPTIONS handler
@app.options("/chat")
async def options_handler():
    return JSONResponse(
        content={"status": "ok"},
        headers={
            "Access-Control-Allow-Origin": "https://www.monaddirectory.xyz",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )

# Test endpoint
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
        return {
            "message": response
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
