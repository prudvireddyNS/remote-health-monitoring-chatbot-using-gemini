'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import VoiceInput from '../../components/VoiceInput';
import TextToSpeech from '../../components/TextToSpeech';

export default function ReturningPatient() {
  const router = useRouter();
  const [step, setStep] = useState('login'); // login, update, result
  const [isLoading, setIsLoading] = useState(false);
  const [patientId, setPatientId] = useState('');
  const [patientData, setPatientData] = useState(null);
  const [newSymptoms, setNewSymptoms] = useState('');
  const [error, setError] = useState(null);
  const [diagnosis, setDiagnosis] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/patients/${patientId}`);
      
      if (!response.ok) {
        throw new Error('Patient not found. Please check your ID.');
      }

      const data = await response.json();
      setPatientData(data);
      setStep('update');
    } catch (err) {
      console.error('Error:', err);
      setError(err.message || 'An error occurred while retrieving patient data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateSymptoms = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/patients/${patientId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ new_symptoms: newSymptoms }),
      });

      if (!response.ok) {
        throw new Error('Failed to update symptoms');
      }

      const data = await response.json();
      setPatientData(data);
      setStep('result');
    } catch (err) {
      console.error('Error:', err);
      setError(err.message || 'An error occurred while updating symptoms');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceInput = (transcript) => {
    setNewSymptoms(transcript);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    // API call implementation here
    const mockDiagnosis = "Based on your updated symptoms, continue with the prescribed medication.";
    setDiagnosis(mockDiagnosis);
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
            <div className="p-4 border border-gray-200 rounded-md bg-gray-50 whitespace-pre-line mb-6">
              {patientData.latest_diagnosis}
            </div>
            
            <TextToSpeech text={patientData.latest_diagnosis} />
            
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