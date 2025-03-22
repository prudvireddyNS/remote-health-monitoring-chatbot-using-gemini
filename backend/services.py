import os
import sys
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our custom modules
from backend.models import Patient
from app.ai_service import AIService as AppAIService

class PatientService:
    """Service for patient-related operations"""
    
    def add_patient(self, db: Session, patient_data):
        """Add a new patient to the database"""
        try:
            date = datetime.today().date()
            new_patient = Patient(
                patient_name=patient_data.patient_name,
                joining_date=date,
                symptoms=patient_data.symptoms
            )
            
            db.add(new_patient)
            db.commit()
            db.refresh(new_patient)
            return new_patient
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            db.rollback()
            return None
    
    def update_patient(self, db: Session, patient_id: int, new_symptoms: str):
        """Update patient symptoms and move current diagnosis to previous"""
        try:
            # Get patient by ID
            patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
            
            if patient:
                # Move current diagnosis to previous if it exists
                if patient.latest_diagnosis:
                    patient.prev_diagnosis = patient.latest_diagnosis
                
                # Update new symptoms
                patient.new_symptoms = new_symptoms
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
    
    def update_diagnosis(self, db: Session, patient_id: int, diagnosis: str):
        """Update the latest diagnosis for a patient"""
        try:
            patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
            if patient:
                patient.latest_diagnosis = diagnosis
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
        """Initialize the AI service by using the existing AIService from the app module"""
        self.ai_service = AppAIService()
    
    def get_diagnosis(self, symptoms: str):
        """Get diagnosis suggestions based on symptoms using Gemini API"""
        return self.ai_service.get_diagnosis(symptoms)
    
    def get_health_advice(self, condition: str):
        """Get general health advice for a specific condition"""
        return self.ai_service.get_health_advice(condition)
    
    def analyze_medical_history(self, symptoms: str, previous_conditions: str):
        """Analyze patient's medical history and provide insights"""
        return self.ai_service.analyze_medical_history(symptoms, previous_conditions)