# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
from typing import Optional, List
from enum import Enum
import logging
from .config import settings
from .services.llm_service import LLMService
import torch
import json

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

class BudgetLevel(str, Enum):
    BUDGET = "budget"
    MODERATE = "moderate"
    LUXURY = "luxury"

@app.post("/get-itinerary-prompt")
async def get_itinerary_prompt(
    destination: str,
    start_date: date,
    end_date: date,
    budget_level: BudgetLevel
):
    try:
        logger.info(f"Creating itinerary prompt for {destination}")
        
        # Create user input for the prompt
        user_input = f"Create a travel itinerary for {destination} from {start_date} to {end_date} with a {budget_level} budget."
        context = f"Destination: {destination}\nDates: {start_date} to {end_date}\nBudget: {budget_level}"
        
        prompt = llm_service._create_prompt(user_input, context)
        
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
            prompt = llm_service._create_prompt(
                f"Create a travel itinerary for {destination} from {start_date} to {end_date} with a {budget_level} budget.",
                f"Destination: {destination}\nDates: {start_date} to {end_date}\nBudget: {budget_level}"
            )
        
        # Generate response from LLM
        inputs = llm_service.tokenizer(prompt, return_tensors="pt").to(llm_service.model.device)
        
        with torch.no_grad():
            try:
                outputs = llm_service.model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    temperature=0.7,
                    top_p=0.9,
                    repetition_penalty=1.1
                )
                
                response = llm_service.tokenizer.decode(outputs[0], skip_special_tokens=True)
                logger.info(f"Generated response: {response}")
                
                try:
                    itinerary_json = json.loads(response)
                    return itinerary_json
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing response as JSON: {response}")
                    raise HTTPException(status_code=500, detail=f"Invalid JSON response: {str(e)}")
                
            except Exception as e:
                logger.error(f"Error in model generation: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Model generation error: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error generating itinerary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))