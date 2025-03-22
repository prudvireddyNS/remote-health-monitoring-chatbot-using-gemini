from datetime import datetime
import csv
import os
from app.models import Patient, get_engine, get_session, init_db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, text

class Database:
    def __init__(self, database='health_monitoring.db'):
        """Initialize database connection using SQLAlchemy"""
        try:
            self.engine = get_engine(database)
            self.session = get_session(self.engine)
            # Initialize database tables if they don't exist
            init_db(self.engine)
            # Initialize column_names attribute
            self.column_names = None
            print("Successfully connected to database")
        except SQLAlchemyError as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def add_patient(self, name, symptoms):
        """Add a new patient to the database"""
        try:
            date = datetime.today().date()
            new_patient = Patient(
                patient_name=name,
                joining_date=date,
                symptoms=symptoms
            )
            
            self.session.add(new_patient)
            self.session.commit()
            return new_patient.patient_id
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            self.session.rollback()
            return None
    
    def update_patient(self, patient_id, new_symptoms):
        """Update patient symptoms and move current diagnosis to previous"""
        try:
            # Ensure patient_id is an integer
            try:
                patient_id = int(patient_id)
            except (ValueError, TypeError):
                print(f"Invalid patient ID format: {patient_id}")
                return False
                
            # Get patient by ID
            patient = self.session.query(Patient).filter(Patient.patient_id == patient_id).first()
            
            if patient:
                # Move current diagnosis to previous if it exists
                if patient.latest_diagnosis:
                    patient.prev_diagnosis = patient.latest_diagnosis
                
                # Update new symptoms
                patient.new_symptoms = new_symptoms
                self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            self.session.rollback()
            return False
    
    def get_patient_by_id(self, patient_id):
        """Get patient information by ID"""
        try:
            # Ensure patient_id is an integer
            try:
                patient_id = int(patient_id)
            except (ValueError, TypeError):
                print(f"Invalid patient ID format: {patient_id}")
                return None
                
            patient = self.session.query(Patient).filter(Patient.patient_id == patient_id).first()
            if patient:
                # Convert SQLAlchemy object to tuple to maintain compatibility with existing code
                return (
                    patient.patient_id,
                    patient.patient_name,
                    patient.joining_date,
                    patient.discharge_date,
                    patient.symptoms,
                    patient.prev_diagnosis,
                    patient.new_symptoms,
                    patient.latest_diagnosis
                )
            return None
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
    
    def get_patient_name(self, patient_id):
        """Get patient name by ID"""
        try:
            # Ensure patient_id is an integer
            try:
                patient_id = int(patient_id)
            except (ValueError, TypeError):
                print(f"Invalid patient ID format: {patient_id}")
                return None
                
            patient = self.session.query(Patient).filter(Patient.patient_id == patient_id).first()
            return patient.patient_name if patient else None
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
    
    def update_diagnosis(self, patient_id, diagnosis):
        """Update the latest diagnosis for a patient"""
        try:
            patient = self.session.query(Patient).filter(Patient.patient_id == patient_id).first()
            if patient:
                patient.latest_diagnosis = diagnosis
                self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            self.session.rollback()
            return False
    
    def get_all_patients(self):
        """Get all patients from the database"""
        try:
            patients = self.session.query(Patient).all()
            # Convert SQLAlchemy objects to tuples to maintain compatibility
            return [
                (
                    p.patient_id,
                    p.patient_name,
                    p.joining_date,
                    p.discharge_date,
                    p.symptoms,
                    p.prev_diagnosis,
                    p.new_symptoms,
                    p.latest_diagnosis
                ) for p in patients
            ]
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None
    
    def export_to_csv(self, filename='data.csv'):
        """Export all patient data to CSV"""
        try:
            patients = self.get_all_patients()
            if not patients:
                return False
                
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                
                # Write header
                writer.writerow([
                    'patient_id', 'patient_name', 'joining_date', 'discharge_date',
                    'symptoms', 'prev_diagnosis', 'new_symptoms', 'latest_diagnosis'
                ])
                
                # Write data rows
                writer.writerows(patients)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def fetch_all(self, query):
        """Execute a custom SQL query and fetch all results"""
        try:
            # In SQLAlchemy 2.0, we need to use connect() and then execute
            with self.engine.connect() as connection:
                # Execute the raw SQL query using the imported text function
                result = connection.execute(text(query))
                # Store column names using keys() method
                self.column_names = list(result.keys())
                # Fetch all results
                return result.fetchall()
        except SQLAlchemyError as e:
            print(f"Database error in fetch_all: {e}")
            self.column_names = None
            return None
    
    def close(self):
        """Close the database connection"""
        if hasattr(self, 'session') and self.session:
            self.session.close()