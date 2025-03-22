from sqlalchemy import Column, Integer, String, Date, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# Create base class for declarative models
Base = declarative_base()

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

def get_engine(database='health_monitoring.db'):
    """Create and return a SQLAlchemy engine for SQLite"""
    # Create the database directory if it doesn't exist
    db_dir = os.path.dirname(os.path.abspath(database))
    if not os.path.exists(db_dir) and db_dir:
        os.makedirs(db_dir)
    
    # SQLite connection string
    connection_string = f"sqlite:///{database}"
    return create_engine(connection_string)

def get_session(engine):
    """Create and return a SQLAlchemy session"""
    Session = sessionmaker(bind=engine)
    return Session()

def init_db(engine):
    """Initialize database tables"""
    Base.metadata.create_all(engine)