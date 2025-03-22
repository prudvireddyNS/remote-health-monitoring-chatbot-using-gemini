from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from sqlalchemy import Column, Integer, String, Date, Text
from backend.database import Base

# SQLAlchemy Models
class Patient(Base):
    """SQLAlchemy model for patients table"""
    __tablename__ = 'patients'
    
    patient_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_name = Column(String(30))
    joining_date = Column(Date)
    discharge_date = Column(Date, nullable=True)
    symptoms = Column(String(150))
    prev_diagnosis = Column(Text, nullable=True)
    new_symptoms = Column(String(150), nullable=True)
    latest_diagnosis = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Patient(id={self.patient_id}, name='{self.patient_name}')"

# Pydantic Models for API
class PatientBase(BaseModel):
    """Base Pydantic model for patient data"""
    patient_name: str
    symptoms: str

class PatientCreate(PatientBase):
    """Pydantic model for creating a new patient"""
    pass

class PatientUpdate(BaseModel):
    """Pydantic model for updating patient symptoms"""
    new_symptoms: str

class PatientResponse(PatientBase):
    """Pydantic model for patient response"""
    patient_id: int
    joining_date: date
    discharge_date: Optional[date] = None
    prev_diagnosis: Optional[str] = None
    new_symptoms: Optional[str] = None
    latest_diagnosis: Optional[str] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

class DiagnosisResponse(BaseModel):
    """Pydantic model for diagnosis response"""
    text: str