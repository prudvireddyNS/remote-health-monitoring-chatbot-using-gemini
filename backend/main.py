from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import sys
import shutil
from typing import Optional
import time
import aiofiles

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our custom modules
from backend.database import get_db, engine
from backend.models import PatientCreate, PatientResponse, PatientUpdate, DiagnosisResponse, Base, ReturningPatientRequest
import json # Added for parsing AI response
from backend.services import PatientService, AIService

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Health Monitoring API",
    description="API for Remote Health Monitoring System powered by Gemini AI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
patient_service = PatientService()
ai_service = AIService()

# Helper function to save uploaded file
async def save_upload_file(upload_file: UploadFile) -> str:
    """Save an uploaded file and return the file path"""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate a unique filename using timestamp
        timestamp = int(time.time())
        # Ensure extension is .jpg for consistency
        file_ext = ".jpg"
        safe_filename = f"upload_{timestamp}{file_ext}"
        file_location = os.path.join(upload_dir, safe_filename)
        
        # Save the file
        content = await upload_file.read()
        async with aiofiles.open(file_location, "wb") as file_object:
            await file_object.write(content)
        
        return file_location
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

@app.get("/")
async def root():
    return {"message": "Welcome to the Health Monitoring API"}

@app.post("/api/diagnosis/new", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_new_patient(
    patient_name: str = Form(...),
    symptoms: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Register a new patient and get initial diagnosis with optional image support"""
    print(f"Received new patient data: {patient_name}, {symptoms}, {image}")
    try:
        # Handle image upload if provided
        image_url = None
        if image and image.filename:
            image_url = await save_upload_file(image)
            if not image_url:
                raise HTTPException(status_code=400, detail="Failed to save image")
        
        # Create patient data object
        patient_data = PatientCreate(
            patient_name=patient_name,
            symptoms=symptoms,
            image_url=image_url
        )
        
        # Add patient to database
        db_patient = patient_service.add_patient(db, patient_data)
        if not db_patient:
            raise HTTPException(status_code=400, detail="Failed to create patient")
        
        # Get diagnosis if symptoms are provided
        if symptoms:
            ai_response_str = ai_service.get_diagnosis(symptoms, None, image_url)
            diagnosis = "Could not retrieve diagnosis."
            medicine_suggestions = "Could not retrieve medicine suggestions."

            if "Medicine Suggestions:" in ai_response_str and "Diagnosis:" in ai_response_str:
                parts = ai_response_str.split("Medicine Suggestions:")
                if len(parts) > 1:
                    medicine_suggestions = parts[1].strip().strip('**')
                    diag_part = parts[0].split("Diagnosis:")
                    if len(diag_part) > 1:
                        diagnosis = diag_part[1].strip().strip('**')
                    else:
                        diagnosis = diag_part[0].strip().strip('**') # Case where Diagnosis: might be at the start
                else: # Fallback if split doesn't work as expected
                    diagnosis = ai_response_str
            elif "Diagnosis:" in ai_response_str: # Only diagnosis found
                diag_parts = ai_response_str.split("Diagnosis:").strip().strip('**')
                if len(diag_parts) > 1:
                    diagnosis = diag_parts[1].strip()
                else:
                    diagnosis = ai_response_str # Fallback
            else: # No clear delimiters
                diagnosis = ai_response_str

            patient_service.update_diagnosis(db, db_patient.patient_id, diagnosis, medicine_suggestions)
            db_patient.latest_diagnosis = diagnosis
            db_patient.medicine_suggestions = medicine_suggestions
        
        return db_patient
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/diagnosis/returning", response_model=PatientResponse)
async def handle_returning_patient(
    patient_id: int = Form(...),
    symptoms: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Handle returning patient with new symptoms - simplified API endpoint"""
    # Check if patient exists
    existing_patient = patient_service.get_patient_by_id(db, patient_id)
    if not existing_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Handle image upload if provided
    image_url = None
    if image:
        image_url = await save_upload_file(image)
    
    # Update patient with new symptoms and image if provided
    updated_patient = patient_service.handle_returning_patient(db, existing_patient, symptoms, image_url)
    if not updated_patient:
        raise HTTPException(status_code=400, detail="Failed to update patient")
    
    # Get new diagnosis based on old diagnosis and new symptoms
    ai_response_str = ai_service.get_diagnosis(symptoms, updated_patient.prev_diagnosis, image_url)
    diagnosis = "Could not retrieve diagnosis."
    medicine_suggestions = "Could not retrieve medicine suggestions."

    if "Medicine Suggestions:" in ai_response_str and "Diagnosis:" in ai_response_str:
        parts = ai_response_str.split("Medicine Suggestions:")
        if len(parts) > 1:
            medicine_suggestions = parts[1].strip()
            diag_part = parts[0].split("Diagnosis:")
            if len(diag_part) > 1:
                diagnosis = diag_part[1].strip()
            else:
                diagnosis = diag_part[0].strip()
        else:
            diagnosis = ai_response_str
    elif "Diagnosis:" in ai_response_str:
        diag_parts = ai_response_str.split("Diagnosis:")
        if len(diag_parts) > 1:
            diagnosis = diag_parts[1].strip()
        else:
            diagnosis = ai_response_str
    else:
        diagnosis = ai_response_str

    patient_service.update_diagnosis(db, patient_id, diagnosis, medicine_suggestions)
    updated_patient.latest_diagnosis = diagnosis
    updated_patient.medicine_suggestions = medicine_suggestions
    
    return updated_patient

# Keeping only the get patient endpoint for internal use
@app.get("/api/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Get patient information by ID"""
    patient = patient_service.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.get("/health-advice/{condition}", response_model=DiagnosisResponse)
async def get_health_advice(condition: str):
    """Get general health advice for a specific condition
    
    This endpoint provides comprehensive management strategies for a given medical condition
    based on current clinical guidelines, including lifestyle modifications, monitoring parameters,
    warning signs, preventive measures, and self-management techniques.
    """
    # Get health advice
    advice = ai_service.get_health_advice(condition)
    return {"text": advice}

@app.get("/patients/", response_model=list[PatientResponse])
async def get_all_patients(db: Session = Depends(get_db)):
    """Get all patients"""
    patients = patient_service.get_all_patients(db)
    return patients

# Removed unnecessary endpoints to simplify the API structure

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


