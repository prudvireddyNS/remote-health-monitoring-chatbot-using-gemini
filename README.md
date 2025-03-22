# Remote Health Monitoring System

## Project Overview
This application is a remote health monitoring system powered by Google's Gemini AI. It allows patients to register, input their symptoms, and receive AI-generated diagnosis suggestions and health advice. The system maintains patient records and tracks medical history to provide more personalized health recommendations.

## Features
- Patient registration and identification
- Symptom input via text or voice
- AI-powered diagnosis suggestions
- Medical history tracking
- Health advice based on symptoms and medical history
- Admin dashboard for viewing patient records
- Voice output for diagnosis (text-to-speech)

## Project Structure
```
├── app/                      # Application modules
│   ├── __init__.py           # Package initializer
│   ├── ai_service.py         # AI service for Gemini API interactions
│   ├── database.py           # Database operations
│   ├── speech.py             # Speech recognition and text-to-speech
│   └── streamlit_app.py      # Main Streamlit application
├── config.py                 # Configuration settings
├── requirements.txt          # Project dependencies
├── run_app.py               # Application launcher
└── README.md                # Project documentation
```

## Installation

1. Clone the repository:
```
git clone <repository-url>
cd Chatbot-for-Remote-HealthMonitoring-using-GEMINI
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Set up the MySQL database:
   - Create a database named 'victims'
   - Create a table with the following structure:
   ```sql
   CREATE TABLE patients(
     patient_id INT PRIMARY KEY AUTO_INCREMENT,
     patient_name VARCHAR(30),
     joining_date DATE,
     discharge_date DATE,
     symptoms VARCHAR(150),
     prev_diagnosis VARCHAR(300),
     new_symptoms VARCHAR(150),
     latest_diagnosis VARCHAR(300)
   );
   ```

4. Set your Gemini API key:
   - Get an API key from Google AI Studio (https://makersuite.google.com/)
   - Set it as an environment variable: `GEMINI_API_KEY=your_api_key_here`

## Running the Application

1. Start the application:
```
python run_app.py
```

2. Open your web browser and navigate to:
```
http://localhost:8501
```

## Usage

### New Patient
1. Navigate to the "New Patient" page
2. Enter your name and symptoms
3. Optionally use voice input for symptoms
4. Submit to receive a diagnosis
5. Save your patient ID for future visits

### Returning Patient
1. Navigate to the "Returning Patient" page
2. Enter your patient ID
3. Update your symptoms
4. Receive a new diagnosis and analysis based on your medical history

### Admin Access
1. Navigate to the "Patient Records" page
2. Enter the admin password (default: admin123)
3. View and export patient records

## Disclaimer
This system is for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.

## License
This project is licensed under the MIT License - see the LICENSE file for details.