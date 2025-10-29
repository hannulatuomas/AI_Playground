import React from 'react';

const Landing: React.FC = () => (
  <main className="flex items-center justify-center min-h-screen bg-gray-50 px-2">
    <div className="bg-white p-8 rounded shadow w-full max-w-md flex flex-col items-center gap-4">
      <h1 className="text-3xl font-bold text-center">Welcome to Your SaaS App</h1>
      <p className="text-gray-700 text-center">A modern, extensible SaaS template with authentication, subscriptions, and more. Get started by registering or logging in.</p>
      <div className="flex gap-4 mt-2">
        <a href="/register" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition">Register</a>
        <a href="/login" className="bg-gray-200 text-gray-800 px-4 py-2 rounded hover:bg-gray-300 transition">Login</a>
      </div>
    </div>
  </main>
);

export default Landing;
