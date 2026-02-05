import React from 'react';
import './App.css';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <div className="App min-h-screen bg-gray-100">
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold">Universal Market Sentiment Analysis</h1>
          <p className="text-blue-100 mt-2">AI-powered sentiment analysis for stocks, crypto, commodities, real estate & exchanges</p>
        </div>
      </header>
      
      <main className="container mx-auto px-4 py-8">
        <Dashboard />
      </main>
      
      <footer className="bg-gray-800 text-white text-center py-4 mt-12">
        <p>&copy; 2024 Universal Market Sentiment Analysis. Powered by AI.</p>
      </footer>
    </div>
  );
}

export default App;