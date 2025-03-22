import os
import google.generativeai as genai
from vertexai.generative_models import (
    Content,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)

class AIService:
    def __init__(self, api_key=None):
        """Initialize the AI service with the Gemini API key"""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY', '')
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not set. AI features will not work.")
        else:
            genai.configure(api_key=self.api_key)

        # Define the system prompt for the AI's role
        self.system_prompt = """
        You are a medical advisor AI trained to provide general health information and suggestions based on clinical knowledge. 
        Your role is to assist users by offering educational insights, potential diagnoses, and general health advice. 
        Always emphasize that your responses are for informational purposes only and not a substitute for professional medical advice. 
        Provide clear, concise, and factual information based on established medical guidelines.
        """

    def _generate_response(self, model_name, prompt, temperature=0.3, max_tokens=1000):
        """Helper method to generate a response with the system prompt included."""
        try:
            if not self.api_key:
                raise ValueError("API key not configured")

            model = genai.GenerativeModel(model_name, generation_config={
                'temperature': temperature,
                'max_output_tokens': max_tokens,
                'top_p': 1,
                'top_k': 32
            })

            # Combine the system prompt with the user's input
            full_prompt = f"{self.system_prompt}\n\n{prompt}"
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            # print(f"Error in Gemini API call: {e}")
            # return "Unable to process request. Please try again."
            raise

    def get_diagnosis(self, symptoms):
        """Get diagnosis suggestions based on symptoms using Gemini API"""
        prompt = f"""Analyze these symptoms from a medical textbook perspective: {symptoms}. 
        List 3 possible conditions that could manifest these symptoms, followed by 2 common 
        therapeutic approaches for each, using standard medical nomenclature. Format as:
        1. [Condition]:
   - Medication/Treatment 1
   - Medication/Treatment 2
        """
        return self._generate_response('gemini-2.0-flash-lite', prompt)

    def get_health_advice(self, condition):
        """Get general health advice for a specific condition"""
        prompt = f"""Describe general management strategies for {condition} based on 
        published clinical guidelines. Include categories: 
        1. Lifestyle modifications
        2. Monitoring parameters
        3. When to consult healthcare provider
        4. Preventive measures
        Present in bullet points using medical terminology."""
        return self._generate_response('gemini-2.0-flash-lite', prompt)

    def analyze_medical_history(self, symptoms, previous_conditions):
        """Analyze patient's medical history and provide insights"""
        prompt = f"""Analyze this clinical scenario for educational purposes:
        Current symptoms: {symptoms}
        Medical history: {previous_conditions}
        Generate a differential diagnosis table with:
        1. Possible conditions
        2. Supporting factors
        3. Ruling out criteria
        4. Recommended diagnostic steps"""
        return self._generate_response('gemini-2.0-flash-lite', prompt)