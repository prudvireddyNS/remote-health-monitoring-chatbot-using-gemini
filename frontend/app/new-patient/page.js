'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import VoiceInput from '../../components/VoiceInput';
import TextToSpeech from '../../components/TextToSpeech';

export default function NewPatient() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    patient_name: '',
    symptoms: ''
  });
  const [diagnosis, setDiagnosis] = useState(null);
  const [patientId, setPatientId] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleVoiceInput = (transcript) => {
    setFormData(prev => ({
      ...prev,
      symptoms: transcript
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/patients/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to register patient');
      }

      const data = await response.json();
      setPatientId(data.patient_id);
      setDiagnosis(data.latest_diagnosis);
    } catch (err) {
      console.error('Error:', err);
      setError(err.message || 'An error occurred while registering');
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
        
        <h1 className="text-3xl font-bold mb-6">New Patient Registration</h1>
        
        {!diagnosis ? (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label htmlFor="patient_name" className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  id="patient_name"
                  name="patient_name"
                  value={formData.patient_name}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div className="mb-6">
                <label htmlFor="symptoms" className="block text-sm font-medium text-gray-700 mb-1">
                  Please describe your symptoms in detail
                </label>
                <textarea
                  id="symptoms"
                  name="symptoms"
                  value={formData.symptoms}
                  onChange={handleChange}
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
              
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors disabled:bg-blue-300"
              >
                {isLoading ? 'Processing...' : 'Register & Get Diagnosis'}
              </button>
            </form>
          </div>
        ) : (
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="mb-4 p-3 bg-green-100 text-green-700 rounded-md">
              Registration successful! Your patient ID is: <strong>{patientId}</strong>
            </div>
            <p className="mb-4 text-sm text-gray-500">
              Please save your patient ID for future visits.
            </p>
            
            <h2 className="text-xl font-semibold mb-2">AI Diagnosis Suggestion:</h2>
            <div className="p-4 border border-gray-200 rounded-md bg-gray-50 whitespace-pre-line">
              {diagnosis}
            </div>
            <TextToSpeech text={diagnosis} />
            
            <div className="mt-6 flex justify-between">
              <Link href="/">
                <button className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-100 transition-colors">
                  Back to Home
                </button>
              </Link>
              <Link href="/returning-patient">
                <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
                  Update Symptoms
                </button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}