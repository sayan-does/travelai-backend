import logging
from ..config import settings
import torch
from transformers import AutoTokenizer, AutoModelForVision2Seq
import os

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        logger.info(f"Initializing LLM Service with model: {settings.MODEL_NAME}")
        self.model_name = settings.MODEL_NAME
        
        # Set Hugging Face token from settings
        os.environ["HUGGING_FACE_HUB_TOKEN"] = settings.HUGGING_FACE_HUB_TOKEN
        if not settings.HUGGING_FACE_HUB_TOKEN:
            logger.warning("HUGGING_FACE_HUB_TOKEN not set in settings")
        
        # Initialize the model and tokenizer with retry and resume capability
        self.tokenizer = AutoTokenizer.from_pretrained(
            settings.MODEL_NAME,
            trust_remote_code=True,
            use_auth_token=settings.HUGGING_FACE_HUB_TOKEN,  # Add auth token
            resume_download=True  # Enable resume capability
        )
        self.model = AutoModelForVision2Seq.from_pretrained(
            settings.MODEL_NAME,
            device_map="auto" if torch.cuda.is_available() else "cpu",
            trust_remote_code=True,
            low_cpu_mem_usage=True,
            use_auth_token=settings.HUGGING_FACE_HUB_TOKEN,  # Add auth token
            resume_download=True,  # Enable resume capability
            offload_folder="offload"  # Add offload folder for large models
        ).eval()
        
        # System prompt optimized for Qwen2-VL-2B-Instruct
        self.system_prompt = """You are an expert AI travel assistant. Your role is to:
1. Create detailed, personalized travel itineraries
2. Provide accurate local information and recommendations
3. Consider budget constraints and preferences
4. Give practical travel tips and cultural insights
5. Maintain a friendly, professional tone

When generating itineraries:
- Include specific times for activities
- Provide realistic cost estimates in USD
- Consider local operating hours and seasonal factors
- Balance tourist attractions with local experiences
- Account for travel time between locations

-Important
    .Give response in  a {
    destination: "India",
    days: [
        {
        activities: "Day 1 activities description..."
        },
        {
        activities: "Day 2 activities description..."
        }
        // ... more days
    ]
} format with location, time, cost, and description.
    .The response should be under 500 words.

Keep responses clear, concise, and well-structured."""

        logger.info("LLM Service initialized successfully")

    def _create_prompt(self, user_input: str, context: str = "") -> str:
        """Create a complete prompt with system context and user input"""
        return f"{self.system_prompt}\n\nContext: {context}\n\nUser: {user_input}\n\nAssistant:"

    async def generate_itinerary(self, destination, start_date, end_date, budget_level):
        try:
            logger.info(f"Generating itinerary for {destination}")
            
            # Create the itinerary prompt
            prompt = self._create_prompt(
                f"Create a travel itinerary for {destination} from {start_date} to {end_date} with a {budget_level} budget.",
                f"Destination: {destination}\nDates: {start_date} to {end_date}\nBudget: {budget_level}"
            )
            
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=1024,
                    temperature=0.7,
                    top_p=0.9,
                    repetition_penalty=1.1
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return self._parse_response(response)
            
        except Exception as e:
            logger.error(f"Error in generate_itinerary: {str(e)}")
            raise

    def _parse_response(self, response):
        try:
            from ..utils.text_parser import extract_time, extract_cost
            
            # Remove the prompt and system message from the response
            itinerary_text = response.split("Assistant:")[-1].strip()
            
            # Split into days
            days = itinerary_text.split("Day")
            parsed_days = []
            
            for day in days[1:]:  # Skip the first empty split
                activities = []
                day_content = day.strip()
                
                # Split into activities
                activity_lines = [line.strip() 
                                for line in day_content.split('\n') 
                                if line.strip()]
                
                current_activity = None
                for line in activity_lines[1:]:  # Skip the "X:" line
                    if line.startswith('-'):
                        # New activity
                        if current_activity:
                            activities.append(current_activity)
                        
                        activity_text = line[1:].strip()
                        current_activity = {
                            "title": activity_text.split('-')[0].strip(),
                            "description": "",
                            "time": extract_time(activity_text),
                            "cost_estimate": extract_cost(activity_text)
                        }
                    elif current_activity:
                        # Description line
                        current_activity["description"] += line + " "
                
                if current_activity:
                    activities.append(current_activity)
                
                if activities:
                    parsed_days.append(activities)
            
            return parsed_days
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {str(e)}")
            raise

    async def generate_chat_response(self, message: str):
        try:
            logger.info("Generating chat response")
            
            # Create the chat prompt
            prompt = self._create_prompt(
                message,
                "Previous conversation: None"  # You could add conversation history here
            )
            
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=512,
                    temperature=0.7,
                    top_p=0.9,
                    repetition_penalty=1.1
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Remove the system prompt and user message from the response
            response = response.split("Assistant:")[-1].strip()
            return response
                
        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            raise