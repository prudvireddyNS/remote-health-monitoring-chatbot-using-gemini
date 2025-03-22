import Link from 'next/link';
import Image from 'next/image';
import styles from './page.module.css';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800">
      {/* Hero Section */}
      <div className="h-screen flex items-center justify-center">
        <div className="relative w-full h-full">
          <Image
            src="/image.webp"
            alt="Health Monitoring"
            fill
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 bg-black/50" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-white px-4">
              <h1 className="text-5xl md:text-6xl font-bold mb-6">Remote Health Monitoring System</h1>
              <p className="text-xl mb-8">AI-powered health monitoring with voice interaction</p>
              <Link href="/user-select">
                <button className="bg-blue-600 text-white py-3 px-8 rounded-lg text-lg hover:bg-blue-700 transition-colors">
                  Get Started
                </button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
