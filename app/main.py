# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from pydantic import BaseModel
from datetime import date, timedelta
from typing import Optional, List
from enum import Enum
import logging
from .config import settings
from .services.llm_service import LLMService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, version=settings.API_VERSION)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM service
llm_service = LLMService()

# Models
class BudgetLevel(str, Enum):
    BUDGET = "budget"
    MODERATE = "moderate"
    LUXURY = "luxury"

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

# Endpoints
@app.get("/")
async def health_check():
    return {"status": "healthy"}

@app.post("/get-itinerary-prompt")
async def get_itinerary_prompt(
    destination: str,
    start_date: date,
    end_date: date,
    budget_level: BudgetLevel
):
    try:
        logger.info(f"Creating itinerary prompt for {destination}")
        
        # Create the prompt using the LLM service
        prompt = llm_service.create_itinerary_prompt(
            destination,
            start_date,
            end_date,
            budget_level
        )
        
        return {"prompt": prompt}
    except Exception as e:
        logger.error(f"Error creating itinerary prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-itinerary")
async def get_itinerary(
    destination: str,
    start_date: date,
    end_date: date,
    budget_level: BudgetLevel,
    prompt: Optional[str] = None
):
    try:
        logger.info(f"Generating itinerary for {destination}")
        
        # If no prompt is provided, create one
        if not prompt:
            prompt = llm_service.create_itinerary_prompt(
                destination,
                start_date,
                end_date,
                budget_level
            )
        
        # Generate response using LLM service
        daily_activities = await llm_service.generate_from_prompt(prompt)
        
        # Convert the activities into DayPlan objects
        daily_plans = []
        current_date = start_date

        for day_activities in daily_activities:
            activities = [Activity(**activity) for activity in day_activities]
            daily_plans.append(DayPlan(
                date=current_date,
                activities=activities
            ))
            current_date += timedelta(days=1)

        total_cost = sum(
            activity.cost_estimate
            for day in daily_plans
            for activity in day.activities
        )

        return TripItinerary(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            budget_level=budget_level,
            daily_plans=daily_plans,
            total_cost_estimate=total_cost
        )
    except Exception as e:
        logger.error(f"Error generating itinerary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))