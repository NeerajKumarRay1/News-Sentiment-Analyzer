import React from 'react';

const ControlPanel = ({ onStartAnalysis, isAnalyzing, progress }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4">Analysis Control</h2>
      
      <div className="space-y-4">
        {/* Start Analysis Button */}
        <div className="flex items-center space-x-4">
          <button
            onClick={onStartAnalysis}
            disabled={isAnalyzing}
            className={`px-6 py-3 rounded-lg font-semibold text-white transition-colors ${
              isAnalyzing 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-yellow-600 hover:bg-yellow-700'
            }`}
          >
            {isAnalyzing ? (
              <div className="flex items-center space-x-2">
                <div className="loading-spinner"></div>
                <span>Analyzing...</span>
              </div>
            ) : (
              'Start Analysis'
            )}
          </button>
          
          {isAnalyzing && (
            <div className="text-sm text-gray-600">
              Progress: {progress}%
            </div>
          )}
        </div>

        {/* Progress Bar */}
        {isAnalyzing && (
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-yellow-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        )}

        {/* Configuration Info */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">Analysis Configuration</h3>
          <div className="text-sm text-gray-600 space-y-1">
            <div>• Searches multiple gold-related news sources</div>
            <div>• Uses AI models: VADER + FinBERT</div>
            <div>• Provides real-time market sentiment</div>
            <div>• Generates actionable trading signals</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ControlPanel;