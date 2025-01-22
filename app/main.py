from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from pydantic import BaseModel
from datetime import date, timedelta
from typing import Optional, List
from enum import Enum
import logging
import os
from .config import settings
from .services.llm_service import LLMService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, version=settings.API_VERSION)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"Path: {request.url.path} Method: {request.method} Time: {process_time:.2f}s Status: {response.status_code}")
        return response

# Add the middlewares
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RequestLoggingMiddleware)

# Get frontend URLs from environment variable or use defaults
frontend_urls = os.getenv('CORS_ORIGINS', 'https://travel-ai-frontend-877104202725.us-central1.run.app')
allowed_origins = [url.strip() for url in frontend_urls.split(',')]
allowed_origins.extend([
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",  # Next.js default
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000"
])

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

@app.options("/{path:path}")
async def options_handler(path: str):
    return JSONResponse(
        content={"status": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Initialize LLM service
llm_service = LLMService()

# Models


class BudgetLevel(str, Enum):
    BUDGET = "budget"
    MODERATE = "moderate"
    LUXURY = "luxury"


class TripRequest(BaseModel):
    destination: str
    start_date: date
    end_date: date
    budget_level: BudgetLevel


class Activity(BaseModel):
    title: str
    description: str
    time: str
    cost_estimate: float


class DayPlan(BaseModel):
    date: date
    activities: List[Activity]


class TripItinerary(BaseModel):
    destination: str
    start_date: date
    end_date: date
    budget_level: BudgetLevel
    daily_plans: List[DayPlan]
    total_cost_estimate: float


class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str

# Endpoints


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/test")
async def test_endpoint():
    return {
        "status": "success",
        "message": "API is working!",
        "config": {
            "app_name": settings.APP_NAME,
            "version": settings.API_VERSION
        }
    }


@app.post("/generate-itinerary", response_model=TripItinerary)
async def generate_itinerary(trip_request: TripRequest):
    try:
        logger.info(f"Generating itinerary for {trip_request.destination}")

        # Generate itinerary using LLM
        daily_activities = await llm_service.generate_itinerary(
            trip_request.destination,
            trip_request.start_date,
            trip_request.end_date,
            trip_request.budget_level
        )

        # Convert the activities into DayPlan objects
        daily_plans = []
        current_date = trip_request.start_date

        for day_activities in daily_activities:
            activities = [
                Activity(**activity) for activity in day_activities
            ]

            daily_plans.append(DayPlan(
                date=current_date,
                activities=activities
            ))
            current_date += timedelta(days=1)

        # Calculate total cost
        total_cost = sum(
            activity.cost_estimate
            for day in daily_plans
            for activity in day.activities
        )

        return TripItinerary(
            destination=trip_request.destination,
            start_date=trip_request.start_date,
            end_date=trip_request.end_date,
            budget_level=trip_request.budget_level,
            daily_plans=daily_plans,
            total_cost_estimate=total_cost
        )
    except Exception as e:
        logger.error(f"Error generating itinerary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    try:
        logger.info(f"Received chat message: {message.message}")
        
        
        print("hello world")
        response = await llm_service.generate_chat_response(message.message)
        
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
