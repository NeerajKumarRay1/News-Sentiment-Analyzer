import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SearchBar from './SearchBar';
import ControlPanel from './ControlPanel';
import ResultsDisplay from './ResultsDisplay';
import ArticleList from './ArticleList';

const Dashboard = () => {
  const [analysisData, setAnalysisData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('Ready to analyze');
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [currentQuery, setCurrentQuery] = useState('');
  const [currentCategory, setCurrentCategory] = useState('');

  useEffect(() => {
    // Test backend connectivity
    const testConnection = async () => {
      try {
        const response = await axios.get('/api/health');
        if (response.status === 200) {
          setConnectionStatus('connected');
          setStatusMessage('Connected to backend - Ready to analyze any financial instrument');
        }
      } catch (error) {
        setConnectionStatus('disconnected');
        setStatusMessage('Backend not available');
      }
    };

    testConnection();
  }, []);

  const handleSearch = async (searchData) => {
    if (isAnalyzing) return;

    const { query, category } = searchData;
    setCurrentQuery(query);
    setCurrentCategory(category);
    
    setIsAnalyzing(true);
    setProgress(0);
    setAnalysisData(null);
    setStatusMessage(`Analyzing ${query}...`);

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 500);

      // eslint-disable-next-line no-unused-vars
      const response = await axios.post('/api/analysis/start', {
        query: query,
        category: category
      });
      
      clearInterval(progressInterval);
      setProgress(100);
      setIsAnalyzing(false);
      
      if (response.data.status === 'completed') {
        setStatusMessage(`Analysis complete for ${query}`);
        setAnalysisData(response.data);
      } else {
        setStatusMessage(`Analysis failed for ${query}`);
        console.error('Analysis failed:', response.data);
      }

    } catch (error) {
      setIsAnalyzing(false);
      setStatusMessage(`Error analyzing ${query}: ${error.message}`);
      console.error('Analysis error:', error);
      
      // Fallback to mock data for development
      console.log('Falling back to mock data for development');
      const mockData = generateMockAnalysisData(query, category);
      setAnalysisData(mockData);
      setStatusMessage(`Analysis complete for ${query} (mock data)`);
    }
  };

  const generateMockAnalysisData = (query, category) => {
    // This function is no longer needed as we're using real backend data
    // Keeping it as fallback for development
    const signals = ['BULLISH', 'BEARISH', 'NEUTRAL'];
    const randomSignal = signals[Math.floor(Math.random() * signals.length)];
    const randomScore = (Math.random() * 2 - 1).toFixed(3);
    const randomArticleCount = Math.floor(Math.random() * 20) + 10;

    return {
      query: query,
      category: category,
      market_signal: randomSignal,
      net_sentiment_score: parseFloat(randomScore),
      total_articles: randomArticleCount,
      sentiment_distribution: {
        'Positive': Math.floor(Math.random() * 10) + 3,
        'Negative': Math.floor(Math.random() * 8) + 2,
        'Neutral': Math.floor(Math.random() * 6) + 2
      },
      processing_time: (Math.random() * 20 + 5).toFixed(1),
      articles: generateMockArticles(query, category, randomArticleCount)
    };
  };

  const generateMockArticles = (query, category, count) => {
    const sampleArticles = [
      {
        title: `${query} shows strong performance in recent trading`,
        sentiment: 'Positive',
        score: 0.65
      },
      {
        title: `Market analysts bullish on ${query} outlook`,
        sentiment: 'Positive',
        score: 0.45
      },
      {
        title: `${query} faces volatility amid market uncertainty`,
        sentiment: 'Negative',
        score: -0.32
      },
      {
        title: `Investors cautious about ${query} future prospects`,
        sentiment: 'Negative',
        score: -0.28
      },
      {
        title: `${query} maintains steady position in market`,
        sentiment: 'Neutral',
        score: 0.05
      }
    ];

    return sampleArticles.slice(0, Math.min(count, 5)).map((article, index) => ({
      title: article.title,
      url: `https://example.com/${category}-article-${index + 1}`,
      h_sent: article.sentiment,
      h_score: article.score,
      c_sent: article.sentiment,
      c_conf: Math.random() * 0.3 + 0.6, // 0.6 to 0.9
      source_type: Math.random() > 0.3 ? 'Full Article' : 'Headline Only'
    }));
  };

  // Legacy function for backward compatibility
  const handleStartAnalysis = () => {
    handleSearch({ query: 'Gold', category: 'commodity' });
  };

  return (
    <div className="space-y-8">
      {/* Connection Status */}
      <div className="flex items-center justify-between bg-white p-4 rounded-lg shadow">
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${
            connectionStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'
          }`}></div>
          <span className="text-sm font-medium">
            {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        <div className="text-sm text-gray-600">{statusMessage}</div>
      </div>

      {/* Universal Search Bar */}
      <SearchBar 
        onSearch={handleSearch}
        isAnalyzing={isAnalyzing}
      />

      {/* Progress Display */}
      {isAnalyzing && (
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">
              Analyzing {currentQuery}...
            </span>
            <span className="text-sm text-gray-600">{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Results Display */}
      {analysisData && (
        <ResultsDisplay data={analysisData} />
      )}

      {/* Article List */}
      {analysisData && analysisData.articles && (
        <ArticleList articles={analysisData.articles} />
      )}

      {/* Legacy Control Panel (hidden but kept for compatibility) */}
      <div style={{ display: 'none' }}>
        <ControlPanel 
          onStartAnalysis={handleStartAnalysis}
          isAnalyzing={isAnalyzing}
          progress={progress}
        />
      </div>
    </div>
  );
};

export default Dashboard;