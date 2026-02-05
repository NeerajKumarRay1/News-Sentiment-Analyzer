import React, { useState } from 'react';

const ArticleList = ({ articles }) => {
  const [expandedArticle, setExpandedArticle] = useState(null);

  if (!articles || articles.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold mb-4">Articles</h2>
        <p className="text-gray-600">No articles to display</p>
      </div>
    );
  }

  const getSentimentIcon = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive': return '🟢';
      case 'negative': return '🔴';
      default: return '⚪';
    }
  };

  const getSentimentClass = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive': return 'sentiment-positive';
      case 'negative': return 'sentiment-negative';
      default: return 'sentiment-neutral';
    }
  };

  const toggleExpanded = (index) => {
    setExpandedArticle(expandedArticle === index ? null : index);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6">Article Analysis ({articles.length})</h2>
      
      <div className="space-y-4">
        {articles.map((article, index) => (
          <div key={index} className="article-card border border-gray-200 rounded-lg p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-semibold text-lg mb-2 line-clamp-2">
                  {article.article?.title || article.title || 'Untitled Article'}
                </h3>
                
                <div className="flex items-center space-x-4 mb-2">
                  {/* Headline Sentiment */}
                  <div className="flex items-center space-x-1">
                    <span className="text-sm text-gray-600">Headline:</span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      getSentimentClass(article.headline_sentiment?.label || article.h_sent)
                    }`}>
                      {getSentimentIcon(article.headline_sentiment?.label || article.h_sent)}
                      {article.headline_sentiment?.label || article.h_sent || 'Unknown'}
                    </span>
                  </div>
                  
                  {/* Content Sentiment */}
                  <div className="flex items-center space-x-1">
                    <span className="text-sm text-gray-600">Content:</span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      getSentimentClass(article.content_sentiment?.label || article.c_sent)
                    }`}>
                      {getSentimentIcon(article.content_sentiment?.label || article.c_sent)}
                      {article.content_sentiment?.label || article.c_sent || 'Unknown'}
                    </span>
                    {(article.content_sentiment?.confidence || article.c_conf) && (
                      <span className="text-xs text-gray-500">
                        ({((article.content_sentiment?.confidence || article.c_conf) * 100).toFixed(1)}%)
                      </span>
                    )}
                  </div>
                </div>

                {/* Source Type */}
                {article.source_type && (
                  <div className="text-xs text-gray-500 mb-2">
                    Source: {article.source_type}
                  </div>
                )}
              </div>
              
              <button
                onClick={() => toggleExpanded(index)}
                className="ml-4 px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded transition-colors"
              >
                {expandedArticle === index ? 'Less' : 'More'}
              </button>
            </div>

            {/* Expanded Details */}
            {expandedArticle === index && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="space-y-2">
                  {/* URL */}
                  <div>
                    <span className="text-sm font-medium text-gray-700">URL: </span>
                    <a 
                      href={article.article?.url || article.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:text-blue-800 break-all"
                    >
                      {article.article?.url || article.url || 'No URL available'}
                    </a>
                  </div>
                  
                  {/* Published Date */}
                  {(article.article?.published || article.published) && (
                    <div>
                      <span className="text-sm font-medium text-gray-700">Published: </span>
                      <span className="text-sm text-gray-600">
                        {article.article?.published || article.published}
                      </span>
                    </div>
                  )}
                  
                  {/* Confidence Scores */}
                  <div className="grid grid-cols-2 gap-4 mt-3">
                    <div className="bg-gray-50 p-2 rounded">
                      <div className="text-xs font-medium text-gray-700">Headline Score</div>
                      <div className="text-sm">
                        {(article.headline_sentiment?.score || article.h_score || 0).toFixed(3)}
                      </div>
                    </div>
                    <div className="bg-gray-50 p-2 rounded">
                      <div className="text-xs font-medium text-gray-700">Content Confidence</div>
                      <div className="text-sm">
                        {((article.content_sentiment?.confidence || article.c_conf || 0) * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ArticleList;