'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import VoiceInput from '../../components/VoiceInput';
import TextToSpeech from '../../components/TextToSpeech';
import ReactMarkdown from 'react-markdown';

export default function ReturningPatient() {
  const router = useRouter();
  const [step, setStep] = useState('login'); // login, update, result
  const [isLoading, setIsLoading] = useState(false);
  const [patientId, setPatientId] = useState('');
  const [patientData, setPatientData] = useState(null);
  const [newSymptoms, setNewSymptoms] = useState('');
  const [error, setError] = useState(null);
  const [diagnosis, setDiagnosis] = useState('');
  const [medicineSuggestions, setMedicineSuggestions] = useState(''); // Added for medicine suggestions
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/patients/${patientId}`);
      
      if (!response.ok) {
        throw new Error('Patient not found. Please check your ID.');
      }

      const data = await response.json();
      setPatientData({
        ...data,
        previous_diagnosis: data.prev_diagnosis, // Map to match frontend naming
        latest_diagnosis: data.latest_diagnosis,
        medicine_suggestions: data.medicine_suggestions // Added for medicine suggestions
      });
      setStep('update');
    } catch (err) {
      console.error('Error:', err);
      setError(err.message || 'An error occurred while retrieving patient data');
    } finally {
      setIsLoading(false);
    }
  };



  const handleVoiceInput = (transcript) => {
    setNewSymptoms(transcript);
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  // Handle updating symptoms with image support
  const handleUpdateSymptoms = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // Create form data to handle file upload
      const formDataToSend = new FormData();
      formDataToSend.append('patient_id', patientId);
      formDataToSend.append('symptoms', newSymptoms);
      if (imageFile) {
        formDataToSend.append('image', imageFile);
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/diagnosis/returning`, {
        method: 'POST',
        body: formDataToSend,
      });

      if (!response.ok) {
        throw new Error('Failed to update symptoms');
      }

      const data = await response.json();
      setDiagnosis(data.latest_diagnosis);
      setMedicineSuggestions(data.medicine_suggestions || 'No medicine suggestions provided.'); // Added for medicine suggestions
      setStep('result');
    } catch (err) {
      console.error('Error:', err);
      setError(err.message || 'An error occurred while updating symptoms');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <Link href="/" className="text-blue-600 hover:underline mb-4 inline-block">
          &larr; Back to Home
        </Link>
        
        <h1 className="text-3xl font-bold mb-6">Returning Patient</h1>
        
        {step === 'login' && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <form onSubmit={handleLogin}>
              <div className="mb-4">
                <label htmlFor="patient_id" className="block text-sm font-medium text-gray-700 mb-1">
                  Enter your Patient ID
                </label>
                <input
                  type="text"
                  id="patient_id"
                  value={patientId}
                  onChange={(e) => setPatientId(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              {error && (
                <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
                  {error}
                </div>
              )}
              
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors disabled:bg-blue-300"
              >
                {isLoading ? 'Checking...' : 'Continue'}
              </button>
            </form>
          </div>
        )}
        
        {step === 'update' && patientData && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="mb-4 p-3 bg-blue-100 text-blue-700 rounded-md">
              Welcome back, <strong>{patientData.patient_name}</strong>!
            </div>
            
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-2">Previous Information</h2>
              <div className="p-4 border border-gray-200 rounded-md bg-gray-50">
                <p><strong>Original Symptoms:</strong> {patientData.symptoms}</p>
                {patientData.latest_diagnosis && (
                  <div className="mt-2">
                    <p><strong>Previous Diagnosis:</strong></p>
                    <p className="whitespace-pre-line">{patientData.latest_diagnosis}</p>
                  </div>
                )}
                {patientData.medicine_suggestions && (
                  <div className="mt-2">
                    <p><strong>Previous Medicine Suggestions:</strong></p>
                    <p className="whitespace-pre-line">{patientData.medicine_suggestions}</p>
                  </div>
                )}
              </div>
            </div>
            
            <form onSubmit={handleUpdateSymptoms}>
              <div className="mb-6">
                <label htmlFor="new_symptoms" className="block text-sm font-medium text-gray-700 mb-1">
                  Please describe your current symptoms
                </label>
                <textarea
                  id="new_symptoms"
                  value={newSymptoms}
                  onChange={(e) => setNewSymptoms(e.target.value)}
                  required
                  rows="5"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                ></textarea>
                <VoiceInput onTranscriptComplete={handleVoiceInput} />
              </div>
              
              <div className="mb-6">
                <label htmlFor="image" className="block text-sm font-medium text-gray-700 mb-1">
                  Upload a relevant medical image (optional)
                </label>
                <input
                  type="file"
                  id="image"
                  accept="image/*"
                  onChange={handleImageChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {imagePreview && (
                  <div className="mt-2">
                    <p className="text-sm text-gray-500 mb-1">Image preview:</p>
                    <img src={imagePreview} alt="Preview" className="max-w-full h-auto max-h-48 rounded-md" />
                  </div>
                )}
              </div>
              
              {error && (
                <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
                  {error}
                </div>
              )}
              
              <div className="flex justify-between">
                <button
                  type="button"
                  onClick={() => setStep('login')}
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-100 transition-colors"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-blue-300"
                >
                  {isLoading ? 'Processing...' : 'Get Updated Diagnosis'}
                </button>
              </div>
            </form>
          </div>
        )}
        
        {step === 'result' && patientData && (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="mb-4 p-3 bg-green-100 text-green-700 rounded-md">
              Your symptoms have been updated successfully!
            </div>
            
            <h2 className="text-xl font-semibold mb-2">New Diagnosis:</h2>
            <div className="prose max-w-none p-4 border border-gray-200 rounded-md bg-gray-50">
              <ReactMarkdown>{diagnosis}</ReactMarkdown>
            </div>
            <TextToSpeech text={diagnosis.replace(/[#*`]/g, '')} />

            {medicineSuggestions && (
              <div className="mt-6">
                <h2 className="text-xl font-semibold mb-2">Medicine Suggestions:</h2>
                <div className="prose max-w-none p-4 border border-gray-200 rounded-md bg-gray-50">
                  <ReactMarkdown>{medicineSuggestions}</ReactMarkdown>
                </div>
                <TextToSpeech text={medicineSuggestions.replace(/[#*`]/g, '')} />
              </div>
            )}
            
            <div className="flex justify-between mt-6">
              <Link href="/">
                <button className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-100 transition-colors">
                  Back to Home
                </button>
              </Link>
              <button
                onClick={() => setStep('update')}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Update Symptoms Again
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}