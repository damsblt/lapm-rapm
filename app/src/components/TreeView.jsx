import { useState, useMemo, useEffect } from 'react'
import './TreeView.css'

function TreeView({ data, currentLaw, searchQuery = '' }) {
  const [expandedArticles, setExpandedArticles] = useState({})

  // Fonction pour convertir le markdown en HTML
  const formatText = (text) => {
    if (!text) return ''
    // Convertit **texte** en <strong>texte</strong> (gère plusieurs occurrences)
    // Utilise une regex non-greedy pour capturer chaque occurrence
    let formatted = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    // Convertit les sauts de ligne en <br>
    formatted = formatted.split('\n').join('<br/>')
    return formatted
  }

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

  // Vérifier si tous les articles sont déployés
  const allExpanded = useMemo(() => {
    if (articles.length === 0) return false
    return articles.every(article => expandedArticles[article.number] === true)
  }, [articles, expandedArticles])

  // Fonction pour déployer/réduire tous les articles
  const toggleAllArticles = () => {
    const newExpandedState = {}
    const shouldExpand = !allExpanded
    
    articles.forEach(article => {
      newExpandedState[article.number] = shouldExpand
    })
    
    setExpandedArticles(newExpandedState)
  }

  // Réinitialiser l'état quand les articles changent (changement de loi ou recherche)
  useEffect(() => {
    setExpandedArticles({})
  }, [currentLaw, searchQuery])

  return (
    <div className="tree-view">
      <div className="tree-view-header">
        <h2>{data[currentLaw].title}</h2>
        <button 
          onClick={toggleAllArticles}
          className="expand-all-button"
          title={allExpanded ? 'Réduire tous les articles' : 'Déployer tous les articles'}
        >
          {allExpanded ? '🔽 Tout réduire' : '▶️ Tout déployer'}
        </button>
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
                    <li 
                      key={detailIndex} 
                      dangerouslySetInnerHTML={{ __html: formatText(detail) }}
                    />
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


