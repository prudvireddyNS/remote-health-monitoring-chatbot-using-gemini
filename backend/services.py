import os
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from google import genai
import PIL.Image
from base64 import b64encode
from io import BytesIO
from typing import Optional

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our custom modules
from backend.models import Patient
from backend.ai_service import AIService

class PatientService:
    """Service for patient-related operations"""
    
    def add_patient(self, db: Session, patient_data):
        """Add a new patient to the database"""
        try:
            # Check if patient already exists
            existing_patient = db.query(Patient).filter(
                Patient.patient_name == patient_data.patient_name
            ).first()
            
            if existing_patient:
                return self.handle_returning_patient(db, existing_patient, patient_data.symptoms, patient_data.image_url)
            
            # Add new patient
            date = datetime.today().date()
            new_patient = Patient(
                patient_name=patient_data.patient_name,
                joining_date=date,
                symptoms=patient_data.symptoms,
                image_url=patient_data.image_url
            )
            
            db.add(new_patient)
            db.commit()
            db.refresh(new_patient)
            return new_patient
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            db.rollback()
            return None

    def handle_returning_patient(self, db: Session, patient: Patient, new_symptoms: str, image_url: str = None):
        """Handle returning patient logic"""
        try:
            if patient.latest_diagnosis:
                patient.prev_diagnosis = patient.latest_diagnosis
            patient.symptoms = new_symptoms
            patient.latest_diagnosis = None  # Reset latest diagnosis
            if image_url:
                patient.image_url = image_url
            db.commit()
            db.refresh(patient)
            return patient
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            db.rollback()
            return None
    
    def update_patient(self, db: Session, patient_id: int, new_symptoms: str, image_url: str = None):
        """Update patient symptoms and move current diagnosis to previous"""
        try:
            # Get patient by ID
            patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
            
            if patient:
                # Move current diagnosis to previous if it exists
                if patient.latest_diagnosis:
                    patient.prev_diagnosis = patient.latest_diagnosis
                
                # Update new symptoms and image if provided
                patient.new_symptoms = new_symptoms
                if image_url:
                    patient.image_url = image_url
                db.commit()
                db.refresh(patient)
                return True
            return False
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            db.rollback()
            return False
    
    def get_patient_by_id(self, db: Session, patient_id: int):
        """Get patient information by ID"""
        try:
            return db.query(Patient).filter(Patient.patient_id == patient_id).first()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
    
    def update_diagnosis(self, db: Session, patient_id: int, diagnosis_text: str, medicine_suggestions_text: Optional[str] = None):
        """Update the latest diagnosis for a patient"""
        try:
            patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
            if patient:
                patient.latest_diagnosis = diagnosis_text
                if medicine_suggestions_text:
                    patient.medicine_suggestions = medicine_suggestions_text
                db.commit()
                db.refresh(patient)
                return True
            return False
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            db.rollback()
            return False
    
    def get_all_patients(self, db: Session):
        """Get all patients from the database"""
        try:
            return db.query(Patient).all()
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return []

class AIService:
    """Service for AI-related operations"""
    
    def __init__(self):
        # genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        api_key = os.getenv('GEMINI_API_KEY', '')
        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-2.0-flash-lite"

    def _prepare_image(self, image_path):
        """Convert image to PIL Image for Gemini API"""
        try:
            if not image_path:
                return None
            
            # Open and convert image using PIL
            image = PIL.Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (20MB limit)
            max_size = (1024, 1024)
            image.thumbnail(max_size, PIL.Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            print(f"Error preparing image: {e}")
            return None

    def get_diagnosis(self, symptoms, prev_diagnosis=None, image_path=None):
        try:
            # Prepare the prompt
            prompt = f"""You are a knowledgeable medical assistant. Analyze the following symptoms: {symptoms}. Provide a diagnosis and suggest potential medicines. Respond in a direct and professional tone, without any disclaimers about not being a real doctor. Structure your response clearly, perhaps with 'Diagnosis:' and 'Medicine Suggestions:' sections."""
            if prev_diagnosis:
                prompt += f"\nPrevious diagnosis: {prev_diagnosis}"
            
            # Prepare contents list for generate_content
            contents = [prompt]
            
            # Add image if provided
            if image_path:
                image = self._prepare_image(image_path)
                if image:
                    contents.append(image)
            
            # Generate response using the client
            # print(contents)
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents
            )
            # print(response)
            # Assuming the response.text contains both diagnosis and medicine suggestions
            # We'll need to parse this. For now, let's assume a simple split or a structured response from AI.
            # For this example, let's assume the AI will return a JSON string like: {"diagnosis": "...", "medicine_suggestions": "..."}
            # This part will heavily depend on how you instruct the Gemini API and how it formats its response.
            # For a more robust solution, you'd parse a structured JSON response.
            # For now, we'll just return the raw text and handle parsing/splitting in the main.py or expect a specific format.
            return response.text # Placeholder: This needs to be updated to return structured data or parse it here.
            
        except Exception as e:
            print(f"Error in diagnosis generation: {e}")
            return "{\"diagnosis\": \"Unable to generate diagnosis at this time. Please try again later.\", \"medicine_suggestions\": \"No medicine suggestions available.\"}" # Return a JSON string

    def get_health_advice(self, condition: str):
        """Get general health advice for a specific condition
        
        Args:
            condition: The medical condition to provide advice for
        """
        return self.ai_service.get_health_advice(condition)
    
    def analyze_medical_history(self, symptoms: str, previous_conditions: str):
        """Analyze patient's medical history and provide insights
        
        Args:
            symptoms: Current symptoms reported by the patient
            previous_conditions: Patient's medical history and previous conditions
        """
        return self.ai_service.analyze_medical_history(symptoms, previous_conditions)