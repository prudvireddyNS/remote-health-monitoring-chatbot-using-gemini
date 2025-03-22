import Link from 'next/link';

export default function UserSelect() {
  return (
    <div className="container mx-auto px-4 py-16">
      <div className="flex flex-col items-center justify-center space-y-8">
        <h2 className="text-3xl font-bold mb-8">Choose Your Path</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl w-full">
          <div className="border rounded-lg p-8 shadow-lg hover:shadow-xl transition-shadow">
            <h3 className="text-2xl font-semibold mb-4">New Patient</h3>
            <p className="mb-6">First time here? Register and get started with your AI-powered health monitoring journey.</p>
            <Link href="/new-patient">
              <button className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors">
                Register Now
              </button>
            </Link>
          </div>

          <div className="border rounded-lg p-8 shadow-lg hover:shadow-xl transition-shadow">
            <h3 className="text-2xl font-semibold mb-4">Returning Patient</h3>
            <p className="mb-6">Welcome back! Continue your health monitoring journey.</p>
            <Link href="/returning-patient">
              <button className="w-full border-2 border-blue-600 text-blue-600 py-3 rounded-lg hover:bg-blue-50 transition-colors">
                Login
              </button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
