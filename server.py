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

# Updated CORS middleware with explicit settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.monaddirectory.xyz",
        "https://monaddirectory.xyz",
        "http://localhost:3000",
        "http://localhost:5000"
    ],
    allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
    allow_headers=["Content-Type", "Authorization", "Origin"],
    allow_credentials=False,
    max_age=3600,
)

# Add OPTIONS endpoint for CORS preflight
@app.options("/{path:path}")
async def options_route(request: Request):
    return JSONResponse(
        content="OK",
        headers={
            "Access-Control-Allow-Origin": "https://www.monaddirectory.xyz",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Origin",
        }
    )

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Incoming request: {request.method} {request.url}")
    logger.debug(f"Headers: {request.headers}")
    response = await call_next(request)
    logger.debug(f"Response status: {response.status_code}")
    return response

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
        return JSONResponse(
            content={"message": response},
            headers={
                "Access-Control-Allow-Origin": "https://www.monaddirectory.xyz",
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
