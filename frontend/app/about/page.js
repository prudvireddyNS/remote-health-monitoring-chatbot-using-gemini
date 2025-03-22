import Link from 'next/link';

export default function About() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <Link href="/" className="text-blue-600 hover:underline mb-4 inline-block">
          &larr; Back to Home
        </Link>
        
        <h1 className="text-3xl font-bold mb-6">About the Remote Health Monitoring System</h1>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Project Overview</h2>
          <p className="mb-4">
            This application is a remote health monitoring system powered by Google's Gemini AI. 
            It allows patients to register, input their symptoms, and receive AI-generated diagnosis 
            suggestions and health advice. The system maintains patient records and tracks medical 
            history to provide more personalized health recommendations.
          </p>
          
          <h2 className="text-xl font-semibold mb-4 mt-6">Features</h2>
          <ul className="list-disc pl-6 space-y-2">
            <li>Patient registration and identification</li>
            <li>Symptom input via text</li>
            <li>AI-powered diagnosis suggestions</li>
            <li>Medical history tracking</li>
            <li>Health advice based on symptoms and medical history</li>
            <li>Admin dashboard for viewing patient records</li>
          </ul>
          
          <h2 className="text-xl font-semibold mb-4 mt-6">Technology Stack</h2>
          <ul className="list-disc pl-6 space-y-2">
            <li><strong>Frontend:</strong> Next.js, React, Tailwind CSS</li>
            <li><strong>Backend:</strong> FastAPI, SQLAlchemy</li>
            <li><strong>AI:</strong> Google's Gemini AI</li>
            <li><strong>Database:</strong> SQLite (development), can be configured for production databases</li>
          </ul>
          
          <h2 className="text-xl font-semibold mb-4 mt-6">Important Disclaimer</h2>
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md">
            <p>
              This system is for educational and informational purposes only. It is not intended to be a 
              substitute for professional medical advice, diagnosis, or treatment. Always seek the advice 
              of your physician or other qualified health provider with any questions you may have regarding 
              a medical condition.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}