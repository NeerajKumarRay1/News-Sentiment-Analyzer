import React from 'react';

const ResultsDisplay = ({ data }) => {
  if (!data) return null;

  const getSignalColor = (signal) => {
    switch (signal?.toLowerCase()) {
      case 'bullish': return 'signal-bullish';
      case 'bearish': return 'signal-bearish';
      default: return 'signal-neutral';
    }
  };

  const getSignalIcon = (signal) => {
    switch (signal?.toLowerCase()) {
      case 'bullish': return '🚀';
      case 'bearish': return '🐻';
      default: return '⚖️';
    }
  };

  const getCategoryIcon = (category) => {
    const icons = {
      stock: '📈',
      crypto: '₿',
      commodity: '🥇',
      real_estate: '🏠',
      exchange: '🏛️',
      all: '🌐',
      general: '📊'
    };
    return icons[category] || '📊';
  };

  const getCategoryLabel = (category) => {
    const labels = {
      stock: 'Stock',
      crypto: 'Cryptocurrency',
      commodity: 'Commodity',
      real_estate: 'Real Estate',
      exchange: 'Exchange',
      all: 'General Market',
      general: 'General'
    };
    return labels[category] || 'General';
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      {/* Header with Query Info */}
      <div className="mb-6 pb-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">
              {data.query || 'Market'} Sentiment Analysis
            </h2>
            {data.category && (
              <div className="flex items-center mt-2 text-sm text-gray-600">
                <span className="mr-2">{getCategoryIcon(data.category)}</span>
                <span className="font-medium">{getCategoryLabel(data.category)}</span>
                <span className="mx-2">•</span>
                <span>{data.total_articles || 0} articles analyzed</span>
              </div>
            )}
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-500">Analysis completed</div>
            <div className="text-xs text-gray-500">
              {data.processing_time && `${data.processing_time}s processing time`}
            </div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Market Signal */}
        <div className="text-center">
          <div className={`inline-block px-6 py-4 rounded-lg ${getSignalColor(data.market_signal)}`}>
            <div className="text-3xl mb-2">{getSignalIcon(data.market_signal)}</div>
            <div className="text-xl font-bold">{data.market_signal || 'NEUTRAL'}</div>
          </div>
          <p className="text-sm text-gray-600 mt-2">Market Signal</p>
        </div>

        {/* Net Sentiment Score */}
        <div className="text-center">
          <div className="text-3xl font-bold text-gray-800">
            {data.net_sentiment_score?.toFixed(3) || '0.000'}
          </div>
          <p className="text-sm text-gray-600">Net Sentiment Score</p>
          <p className="text-xs text-gray-500">(-1.0 to +1.0)</p>
        </div>

        {/* Total Articles */}
        <div className="text-center">
          <div className="text-3xl font-bold text-gray-800">
            {data.total_articles || 0}
          </div>
          <p className="text-sm text-gray-600">Articles Analyzed</p>
        </div>
      </div>

      {/* Sentiment Distribution */}
      {data.sentiment_distribution && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-4">Sentiment Distribution</h3>
          <div className="grid grid-cols-3 gap-4">
            {Object.entries(data.sentiment_distribution).map(([sentiment, count]) => {
              const percentage = data.total_articles ? ((count / data.total_articles) * 100).toFixed(1) : 0;
              return (
                <div key={sentiment} className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className={`text-2xl font-bold sentiment-${sentiment.toLowerCase()}`}>
                    {count}
                  </div>
                  <div className="text-sm text-gray-600">{sentiment}</div>
                  <div className="text-xs text-gray-500">{percentage}%</div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Search Query Display */}
      {data.query && (
        <div className="mt-6 bg-blue-50 p-4 rounded-lg">
          <div className="text-sm">
            <span className="font-medium text-blue-800">Analyzed Query:</span>
            <span className="ml-2 text-blue-700">"{data.query}"</span>
            {data.category && data.category !== 'all' && (
              <span className="ml-2 text-blue-600">
                ({getCategoryLabel(data.category)})
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsDisplay;