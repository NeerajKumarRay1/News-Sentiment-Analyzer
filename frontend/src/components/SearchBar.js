import React, { useState } from 'react';

const SearchBar = ({ onSearch, isAnalyzing }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { value: 'all', label: 'All Markets', icon: '🌐' },
    { value: 'stock', label: 'Stocks', icon: '📈' },
    { value: 'crypto', label: 'Cryptocurrency', icon: '₿' },
    { value: 'commodity', label: 'Commodities', icon: '🥇' },
    { value: 'real_estate', label: 'Real Estate', icon: '🏠' },
    { value: 'exchange', label: 'Exchanges', icon: '🏛️' }
  ];

  const popularSearches = [
    { query: 'Bitcoin', category: 'crypto' },
    { query: 'Apple Stock', category: 'stock' },
    { query: 'Gold', category: 'commodity' },
    { query: 'Tesla', category: 'stock' },
    { query: 'Ethereum', category: 'crypto' },
    { query: 'Real Estate Market', category: 'real_estate' },
    { query: 'Oil Prices', category: 'commodity' },
    { query: 'NASDAQ', category: 'exchange' }
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim() && !isAnalyzing) {
      onSearch({
        query: searchQuery.trim(),
        category: selectedCategory
      });
    }
  };

  const handlePopularSearch = (search) => {
    setSearchQuery(search.query);
    setSelectedCategory(search.category);
    if (!isAnalyzing) {
      onSearch({
        query: search.query,
        category: search.category
      });
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4">Universal Market Sentiment Analysis</h2>
      
      {/* Search Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Category Selector */}
          <div className="md:w-1/4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isAnalyzing}
            >
              {categories.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.icon} {cat.label}
                </option>
              ))}
            </select>
          </div>

          {/* Search Input */}
          <div className="md:w-2/4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Query
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Enter stock, crypto, commodity, real estate, or exchange..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isAnalyzing}
            />
          </div>

          {/* Search Button */}
          <div className="md:w-1/4 flex items-end">
            <button
              type="submit"
              disabled={isAnalyzing || !searchQuery.trim()}
              className={`w-full px-6 py-2 rounded-lg font-semibold text-white transition-colors ${
                isAnalyzing || !searchQuery.trim()
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {isAnalyzing ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="loading-spinner"></div>
                  <span>Analyzing...</span>
                </div>
              ) : (
                '🔍 Analyze'
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Popular Searches */}
      <div className="mt-6">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Popular Searches:</h3>
        <div className="flex flex-wrap gap-2">
          {popularSearches.map((search, index) => (
            <button
              key={index}
              onClick={() => handlePopularSearch(search)}
              disabled={isAnalyzing}
              className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                isAnalyzing
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-100 text-gray-700 hover:bg-blue-100 hover:text-blue-700 hover:border-blue-300'
              }`}
            >
              {search.query}
            </button>
          ))}
        </div>
      </div>

      {/* Search Tips */}
      <div className="mt-4 bg-blue-50 p-4 rounded-lg">
        <h4 className="text-sm font-semibold text-blue-800 mb-2">💡 Search Tips:</h4>
        <div className="text-xs text-blue-700 space-y-1">
          <div>• <strong>Stocks:</strong> "Apple", "AAPL", "Tesla stock", "Microsoft shares"</div>
          <div>• <strong>Crypto:</strong> "Bitcoin", "BTC", "Ethereum price", "Dogecoin"</div>
          <div>• <strong>Commodities:</strong> "Gold prices", "Oil market", "Silver futures"</div>
          <div>• <strong>Real Estate:</strong> "Housing market", "Real estate trends", "REIT"</div>
          <div>• <strong>Exchanges:</strong> "NASDAQ", "NYSE", "Binance", "Coinbase"</div>
        </div>
      </div>
    </div>
  );
};

export default SearchBar;