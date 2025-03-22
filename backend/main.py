from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our custom modules
from backend.database import get_db, engine
from backend.models import PatientCreate, PatientResponse, PatientUpdate, DiagnosisResponse, Base
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

@app.get("/")
async def root():
    return {"message": "Welcome to the Health Monitoring API"}

@app.post("/patients/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Register a new patient and get initial diagnosis"""
    # Add patient to database
    print(patient)
    db_patient = patient_service.add_patient(db, patient)
    if not db_patient:
        raise HTTPException(status_code=400, detail="Failed to create patient")
    
    # Get diagnosis if symptoms are provided
    if patient.symptoms:
        diagnosis = ai_service.get_diagnosis(patient.symptoms)
        patient_service.update_diagnosis(db, db_patient.patient_id, diagnosis)
        db_patient.latest_diagnosis = diagnosis
    
    return db_patient

@app.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Get patient information by ID"""
    patient = patient_service.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.put("/patients/{patient_id}", response_model=PatientResponse)
async def update_patient_symptoms(patient_id: int, patient_update: PatientUpdate, db: Session = Depends(get_db)):
    """Update patient symptoms and get new diagnosis"""
    # Check if patient exists
    existing_patient = patient_service.get_patient_by_id(db, patient_id)
    if not existing_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Update patient symptoms
    updated = patient_service.update_patient(db, patient_id, patient_update.new_symptoms)
    if not updated:
        raise HTTPException(status_code=400, detail="Failed to update patient")
    
    # Get new diagnosis if symptoms are provided
    if patient_update.new_symptoms:
        diagnosis = ai_service.get_diagnosis(patient_update.new_symptoms)
        patient_service.update_diagnosis(db, patient_id, diagnosis)
    
    # Return updated patient
    return patient_service.get_patient_by_id(db, patient_id)

@app.get("/patients/{patient_id}/advice/{condition}", response_model=DiagnosisResponse)
async def get_health_advice(patient_id: int, condition: str, db: Session = Depends(get_db)):
    """Get health advice for a specific condition"""
    # Check if patient exists
    patient = patient_service.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get health advice
    advice = ai_service.get_health_advice(condition)
    return {"text": advice}

@app.get("/patients/", response_model=list[PatientResponse])
async def get_all_patients(db: Session = Depends(get_db)):
    """Get all patients"""
    patients = patient_service.get_all_patients(db)
    return patients

@app.post("/speech-to-text/")
async def convert_speech_to_text(audio_file: UploadFile = File(...)):
    """Convert speech audio to text using speech recognition"""
    try:
        # Implementation depends on your chosen speech recognition service
        # This is a placeholder for the actual implementation
        return {"text": "Transcribed text would appear here"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)