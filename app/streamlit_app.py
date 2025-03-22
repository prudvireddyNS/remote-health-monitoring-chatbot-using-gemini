import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our custom modules
from app.database import Database
from app.ai_service import AIService
from app.speech import SpeechService

# Set page configuration
st.set_page_config(
    page_title="Health Monitoring System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def init_services():
    services = {'db': None, 'ai': None, 'speech': None}
    
    # Initialize critical services first (database and AI)
    try:
        services['db'] = Database()
        st.success("✓ Database service initialized successfully")
    except Exception as e:
        st.error(f"Failed to initialize database service: {e}")
        return None, None, None

    try:
        services['ai'] = AIService()
        st.success("✓ AI service initialized successfully")
    except Exception as e:
        st.error(f"Failed to initialize AI service: {e}")
        return None, None, None

    # Initialize optional speech service
    try:
        services['speech'] = SpeechService()
        if services['speech'].speech_available and services['speech'].tts_available:
            st.success("✓ Speech service initialized successfully")
        else:
            st.warning("⚠ Speech service initialized with limited functionality")
            if not services['speech'].speech_available:
                st.info("ℹ Voice input is not available")
            if not services['speech'].tts_available:
                st.info("ℹ Text-to-speech is not available")
    except Exception as e:
        st.warning(f"⚠ Speech service not available: {e}")
        services['speech'] = None

    # Continue if critical services are available
    if services['db'] and services['ai']:
        return services['db'], services['ai'], services['speech']
    return None, None, None

services = init_services()
if not services[0] or not services[1]:  # Check only critical services (db and ai)
    st.error("Failed to initialize critical services. Please check your system configuration.")
    st.stop()

db, ai, speech = services

# Verify all services are properly initialized
if not all([db, ai, speech]):
    st.error("One or more services failed to initialize properly.")
    st.stop()

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "New Patient", "Returning Patient", "Patient Records", "About"])

# Home page
if page == "Home":
    st.title("Remote Health Monitoring System")
    st.subheader("Powered by Gemini AI")
    
    st.markdown("""
    ### Welcome to the Remote Health Monitoring System
    
    This application helps you monitor your health remotely and get AI-powered diagnosis suggestions.
    
    #### Features:
    - Register as a new patient
    - Get diagnosis based on your symptoms
    - Track your medical history
    - Receive personalized health advice
    
    **Note:** This system is for informational purposes only and is not a substitute for professional medical advice.
    """)
    
    st.image("https://img.freepik.com/free-vector/telemedicine-abstract-concept-illustration_335657-3875.jpg", width=600)

# New Patient Registration
elif page == "New Patient":
    st.title("New Patient Registration")
    
    # Voice input section - only show if speech recognition is available
    if speech and speech.speech_available:
        col1, col2 = st.columns(2)
        with col1:
            use_voice = st.checkbox("Use voice input for symptoms")
        
        if use_voice:
            with col2:
                if st.button("Start Voice Input", key="new_patient_voice_input"):
                    st.info("Listening... Please speak clearly.")
                    voice_text = speech.listen()
                    if voice_text and not voice_text.startswith("Sorry") and not voice_text.startswith("Could not") and not voice_text.startswith("Error"):
                        st.session_state['voice_symptoms'] = voice_text
                        st.success(f"Recorded: {voice_text}")
                    else:
                        st.error(f"Error: {voice_text}")
    
    with st.form("new_patient_form"):
        name = st.text_input("Full Name")
        
        # If voice input was used, pre-fill the symptoms text area
        if 'voice_symptoms' in st.session_state:
            symptoms = st.text_area("Please describe your symptoms in detail", value=st.session_state['voice_symptoms'])
        else:
            symptoms = st.text_area("Please describe your symptoms in detail")
        
        # Only show text-to-speech option if available
        read_aloud = st.checkbox("Read diagnosis aloud") if speech and speech.tts_available else False
        submit_button = st.form_submit_button("Register & Get Diagnosis")
    
    if submit_button and name and symptoms:
        with st.spinner("Processing your information..."):
            # Add patient to database
            patient_id = db.add_patient(name, symptoms)
            
            if patient_id:
                # Get diagnosis
                diagnosis = ai.get_diagnosis(symptoms)
                
                # Update diagnosis in database
                db.update_diagnosis(patient_id, diagnosis)
                
                # Display results
                st.success(f"✓ Registration successful! Your patient ID is: {patient_id}")
                st.info("Please save your patient ID for future visits.")
                
                # Display and optionally read diagnosis
                st.write("### AI Diagnosis Suggestion:")
                st.write(diagnosis)
                
                if read_aloud:
                    with st.spinner("Converting diagnosis to speech..."):
                        if speech.speak(diagnosis):
                            st.success("✓ Diagnosis read aloud successfully")
                        else:
                            st.error("❌ Failed to read diagnosis aloud")
    
                # Optional: Speak the diagnosis
                if st.button("Listen to Diagnosis"):
                    speech.speak(diagnosis)
                
                # Export updated records to CSV
                db.export_to_csv()
            else:
                st.error("Error registering patient. Please try again.")
    elif submit_button:
        st.warning("Please fill in all required fields.")

# Returning Patient
elif page == "Returning Patient":
    st.title("Returning Patient")
    
    # Input method selection
    input_method = st.radio("Identify yourself by:", ["Patient ID", "Name"])
    
    if input_method == "Patient ID":
        patient_id = st.text_input("Enter your Patient ID")
        if patient_id and patient_id.isdigit():
            patient_name = db.get_patient_name(patient_id)
            if patient_name:
                st.success(f"Welcome back, {patient_name}!")
                st.session_state['current_patient_id'] = patient_id
                st.session_state['current_patient_name'] = patient_name
            elif patient_id:
                st.error("Patient ID not found. Please check and try again.")
    else:  # By Name
        patient_name = st.text_input("Enter your full name")
        if patient_name:
            # This would need a new method in the Database class to search by name
            # For now, we'll just show a message
            st.warning("Searching by name is not fully implemented. Please use your Patient ID if possible.")
    
    # If patient is identified
    if 'current_patient_id' in st.session_state:
        st.subheader("Update Your Symptoms")
        
        # Voice input section - moved outside the form
        use_voice = st.checkbox("Use voice input")
        
        if use_voice:
            if st.button("Start Voice Input"):
                st.info("Listening... Please speak clearly.")
                voice_text = speech.listen()
                if voice_text and not voice_text.startswith("Sorry") and not voice_text.startswith("Could not") and not voice_text.startswith("Error"):
                    st.session_state['voice_new_symptoms'] = voice_text
                    st.success(f"Recorded: {voice_text}")
                else:
                    st.error(f"Error: {voice_text}")
        
        with st.form("update_symptoms_form"):
            # If voice input was used, pre-fill the symptoms text area
            if 'voice_new_symptoms' in st.session_state:
                new_symptoms = st.text_area("Please describe your current symptoms", value=st.session_state['voice_new_symptoms'])
            else:
                new_symptoms = st.text_area("Please describe your current symptoms")
            
            submit_button = st.form_submit_button("Update & Get New Diagnosis")
        
        if submit_button and new_symptoms:
            with st.spinner("Processing your information..."):
                # Get patient info to retrieve previous diagnosis
                patient_info = db.get_patient_by_id(st.session_state['current_patient_id'])
                
                # Update patient symptoms
                if db.update_patient(st.session_state['current_patient_id'], new_symptoms):
                    # Get new diagnosis
                    diagnosis = ai.get_diagnosis(new_symptoms)
                    
                    # Update diagnosis in database
                    db.update_diagnosis(st.session_state['current_patient_id'], diagnosis)
                    
                    # Display results
                    st.subheader("Your New Diagnosis")
                    st.write(diagnosis)
                    
                    # If we have previous conditions, show analysis
                    if patient_info and patient_info[5]:  # Index 5 should be prev_diagnosis
                        st.subheader("Analysis Based on Medical History")
                        analysis = ai.analyze_medical_history(new_symptoms, patient_info[5])
                        st.write(analysis)
                    
                    # Optional: Speak the diagnosis
                    if st.button("Listen to Diagnosis"):
                        speech.speak(diagnosis)
                    
                    # Export updated records to CSV
                    db.export_to_csv()
                else:
                    st.error("Error updating patient information. Please try again.")
            
        elif submit_button:
            st.warning("Please enter your symptoms.")

# Patient Records
elif page == "Patient Records":
    st.title("Patient Records")
    
    # Admin authentication (simple for demo)
    with st.expander("Admin Authentication"):
        password = st.text_input("Enter admin password", type="password")
        if password == "admin123":  # Simple password for demo
            st.session_state['admin_authenticated'] = True
        elif password:
            st.error("Incorrect password")
    
    if st.session_state.get('admin_authenticated', False):
        # Fetch all patient records
        patients = db.fetch_all("SELECT * FROM patients")
        
        if patients:
            # Convert to DataFrame for easier display
            columns = db.column_names
            df = pd.DataFrame(patients, columns=columns)
            
            st.dataframe(df)
            
            # Export options
            if st.button("Export to CSV"):
                csv_path = f"patient_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(csv_path, index=False)
                st.success(f"Exported to {csv_path}")
        else:
            st.info("No patient records found.")
    else:
        st.info("Please authenticate to view patient records.")

# About page
elif page == "About":
    st.title("About This System")
    
    st.markdown("""
    ### Remote Health Monitoring System
    
    This application was developed to provide remote health monitoring and AI-powered diagnosis suggestions.
    
    #### Technologies Used:
    - Streamlit for the web interface
    - Google's Gemini AI for diagnosis suggestions
    - MySQL for patient data storage
    - Speech recognition for voice input
    
    #### Disclaimer:
    This system is for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
    
    #### Privacy Policy:
    All patient data is stored securely and is only accessible to authorized personnel. Your data will never be shared with third parties without your explicit consent.
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "This application is for demonstration purposes only. "
    "It is not a substitute for professional medical advice."
)

# Close database connection when app is done
def on_shutdown():
    db.close()

# Register the shutdown function
st.cache_resource.clear()