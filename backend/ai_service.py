import os
import base64
import google.generativeai as genai
from typing import Optional, List, Union

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
You are a highly trained medical assistant with comprehensive clinical knowledge, capable of providing precise, actionable medical advice. 
Your responses should reflect the communication style of a practicing clinician, prioritizing accuracy, clarity, and detail. 
You are expected to provide well-structured responses, including differential diagnoses and medication recommendations, without unnecessary disclaimers or generic safety warnings unless explicitly requested.

Guidelines for your responses:
1. **Clinical Tone:** Respond confidently as a medical professional, avoiding hedging language and minimizing uncertainty. Assume the user expects an authoritative, direct response.
2. **Diagnosis Section:** Provide a detailed differential diagnosis based on the provided symptoms. Include common, likely, and less likely but clinically significant conditions, along with key diagnostic criteria for each.
3. **Medicine Suggestions Section:** Include specific medication names, typical dosages, drug classes, and critical clinical considerations (e.g., contraindications, side effects, interactions) for each condition.
4. **Clear Structure:** Use clear, consistent formatting, including bullet points or subheadings for easy readability.
5. **No Disclaimers:** Avoid including repetitive disclaimers about consulting a healthcare professional unless explicitly requested. Focus on precise, clinically sound guidance.

Your responses should be structured and precise, mirroring the communication style of an experienced clinician, without reverting to general AI language. Prioritize actionable, patient-centered information.
NOTE: Prioritize detailed diagnostic analysis over medication suggestions, as accurate diagnosis is essential for proper treatment.
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
            print(response.text)
            return response.text
        except Exception as e:
            print(f"Error in Gemini API call: {e}")
            return "Unable to process request. Please try again."

    def _encode_image(self, image_path):
        """Encode an image file to base64 for Gemini API"""
        if not image_path:
            return None
            
        try:
            with open(image_path, "rb") as image_file:
                # Read binary data and encode to base64
                return base64.b64encode(image_file.read()).decode('ascii')
        except Exception as e:
            print(f"Error encoding image: {e}")
            return None
            
    def get_diagnosis(self, symptoms, previous_diagnosis=None, image_path=None):
        """Get diagnosis suggestions based on symptoms and optional image using Gemini API
        
        Args:
            symptoms: Current symptoms reported by the patient
            previous_diagnosis: Optional previous diagnosis to consider for continuity of care
            image_path: Optional path to a medical image for analysis
        """
        try:
            if not self.api_key:
                raise ValueError("API key not configured")
                
            # Prepare the prompt based on available information
            if previous_diagnosis:
                text_prompt = f"""Analyze the following new symptoms: {symptoms}.

Previous diagnosis information: {previous_diagnosis}

Provide a comprehensive medical analysis with the following sections:

Diagnosis:
- Provide a differential diagnosis, including at least three possible conditions that could manifest these symptoms.
- Clearly differentiate between conditions that are likely, less likely, and potentially serious but rare, based on the provided symptoms and previous diagnosis.
- Include key diagnostic criteria for each condition, potential progression, and clinical context where relevant.

Medicine Suggestions:
- Provide specific medication recommendations for each identified condition.
- Include the drug class, specific medication names, typical doses, common side effects, and important contraindications.
- Consider both symptomatic relief and disease-specific treatment options.
- Avoid generic disclaimers unless explicitly requested, and focus on direct, practical medical advice.
"""

            else:
                text_prompt = f"""Analyze the following symptoms: {symptoms}.

Provide a comprehensive medical analysis with the following sections:

Diagnosis:
- Provide a differential diagnosis, including at least three possible conditions that could manifest these symptoms.
- Clearly differentiate between conditions that are likely, less likely, and potentially serious but rare, based on the provided symptoms.
- Include key diagnostic criteria for each condition and recommended follow-up assessments if necessary.

Medicine Suggestions:
- Provide specific medication recommendations for each identified condition.
- Include the drug class, specific medication names, typical doses, common side effects, and important contraindications.
- Consider both symptomatic relief and disease-specific treatment options.
- Avoid generic disclaimers unless explicitly requested, and focus on direct, practical medical advice.
"""
                
            # If image is provided, use multimodal model and add image analysis instructions
            if image_path:
                encoded_image = self._encode_image(image_path)
                if encoded_image:
                    # Use the multimodal model for image analysis
                    model = genai.GenerativeModel('gemini-2.0-pro-vision', generation_config={
                        'temperature': 0.3,
                        'max_output_tokens': 1000,
                        'top_p': 1,
                        'top_k': 32
                    })
                    
                    # Add image analysis instructions to the prompt
                    image_prompt = f"{self.system_prompt}\n\nAnalyze both the patient's reported symptoms AND the provided medical image.\n\n{text_prompt}\n\nAdditionally, identify any visible abnormalities in the image that may be relevant to the diagnosis. Correlate the visual findings with the reported symptoms."
                    
                    # Create the multimodal content with both text and image
                    response = model.generate_content([
                        image_prompt,
                        {"inlineData": {
                            "mimeType": "image/jpeg",
                            "data": encoded_image
                        }}
                    ])
                    return response.text
                else:
                    # Fall back to text-only if image encoding failed
                    print("Warning: Image encoding failed, proceeding with text-only analysis")
            
            # Text-only analysis (no image or image encoding failed)
            return self._generate_response('gemini-2.0-flash-lite', text_prompt)
            
        except Exception as e:
            print(f"Error in diagnosis generation: {e}")
            return "Unable to process request. Please try again."

    def get_health_advice(self, condition):
        """Get general health advice for a specific condition
        
        Args:
            condition: The medical condition to provide advice for
        """
        prompt = f"""Provide comprehensive management strategies for {condition} based on current clinical guidelines.
        
        Include:
        1. Evidence-based lifestyle modifications with specific recommendations.
        2. Key monitoring parameters and their target ranges.
        3. Warning signs that necessitate immediate medical attention.
        4. Preventive measures to avoid complications or exacerbations.
        5. Self-management techniques that patients can implement.
        6. Medication adherence considerations (without prescribing specific medications).
        
        Present the information in a structured format with clear headings and bullet points.
        Use appropriate medical terminology while ensuring the information remains accessible.
        """
        return self._generate_response('gemini-2.0-flash-lite', prompt)

    def analyze_medical_history(self, symptoms, previous_conditions):
        """Analyze patient's medical history and provide insights
        
        Args:
            symptoms: Current symptoms reported by the patient
            previous_conditions: Patient's medical history and previous conditions
        """
        prompt = f"""Analyze this clinical scenario in detail:
        
        Current symptoms: {symptoms}
        Medical history: {previous_conditions}
        
        Provide a comprehensive clinical analysis with:
        1. A detailed differential diagnosis table listing possible conditions in order of likelihood.
        2. Supporting evidence for each condition based on the presented symptoms and history.
        3. Specific factors that would rule out each condition.
        4. Recommended diagnostic approach including:
           - Key physical examination findings to look for
           - Appropriate laboratory or imaging studies
           - Monitoring parameters
        5. Potential interactions between current symptoms and previous medical conditions.
        6. Long-term management considerations based on the complete clinical picture.
        
        Format the response as a structured clinical assessment using appropriate medical terminology.
        """
        return self._generate_response('gemini-2.0-flash-lite', prompt)