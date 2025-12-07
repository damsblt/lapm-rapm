import { useState, useMemo } from 'react'
import './TreeView.css'

function TreeView({ data, currentLaw, searchQuery = '' }) {
  const [expandedArticles, setExpandedArticles] = useState({})

  const toggleArticle = (articleNumber) => {
    setExpandedArticles(prev => ({
      ...prev,
      [articleNumber]: !prev[articleNumber]
    }))
  }

  // Filtrer les articles selon la recherche
  const filteredArticles = useMemo(() => {
    if (!searchQuery.trim()) return data[currentLaw].articles
    
    const lowerQuery = searchQuery.toLowerCase()
    return data[currentLaw].articles.filter(article => {
      const matchesNumber = article.number.toLowerCase().includes(lowerQuery)
      const matchesTitle = article.title.toLowerCase().includes(lowerQuery)
      const matchesDetails = article.details.some(detail => 
        detail.toLowerCase().includes(lowerQuery)
      )
      return matchesNumber || matchesTitle || matchesDetails
    })
  }, [data, currentLaw, searchQuery])

  const articles = filteredArticles

  return (
    <div className="tree-view">
      <div className="tree-view-header">
        <h2>{data[currentLaw].title}</h2>
      </div>
      <div className="tree-view-content">
        {articles.map((article, index) => (
          <div key={index} className="tree-item">
            <div 
              className="tree-item-header"
              onClick={() => toggleArticle(article.number)}
            >
              <span className="tree-item-icon">
                {expandedArticles[article.number] ? '▼' : '▶'}
              </span>
              <span className="tree-item-number">Art. {article.number}</span>
              <span className="tree-item-title">{article.title}</span>
            </div>
            {expandedArticles[article.number] && (
              <div className="tree-item-details">
                <ul>
                  {article.details.map((detail, detailIndex) => (
                    <li key={detailIndex} style={{ whiteSpace: 'pre-line' }}>
                      {detail}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default TreeView


