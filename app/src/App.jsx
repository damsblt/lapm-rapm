import { useState, useMemo, useEffect } from 'react'
import './App.css'
import Flashcard from './components/Flashcard'
import Navigation from './components/Navigation'
import TreeView from './components/TreeView'
import ModeSelector from './components/ModeSelector'
import dataCourse from './data.json'
import dataComplete from './data-complete.json'

function App() {
  const [mode, setMode] = useState(null) // null, 'course', ou 'complete'
  const [currentLaw, setCurrentLaw] = useState('LAPM')
  const [currentArticleIndex, setCurrentArticleIndex] = useState(0)
  const [viewMode, setViewMode] = useState('flashcard') // 'flashcard' ou 'tree'
  const [searchQuery, setSearchQuery] = useState('')
  const [darkMode, setDarkMode] = useState(false)

  // Sélectionne les données selon le mode
  const data = mode === 'complete' ? dataComplete : dataCourse

  // Fonction pour filtrer les articles selon la recherche
  const filterArticles = (articles, query) => {
    if (!query.trim()) return articles
    
    const lowerQuery = query.toLowerCase()
    return articles.filter(article => {
      // Recherche dans le numéro, le titre et les détails
      const matchesNumber = article.number.toLowerCase().includes(lowerQuery)
      const matchesTitle = article.title.toLowerCase().includes(lowerQuery)
      const matchesDetails = article.details.some(detail => 
        detail.toLowerCase().includes(lowerQuery)
      )
      return matchesNumber || matchesTitle || matchesDetails
    })
  }

  // Articles filtrés pour la loi actuelle
  const filteredArticles = useMemo(() => {
    return filterArticles(data[currentLaw].articles, searchQuery)
  }, [data, currentLaw, searchQuery])

  // Réinitialiser l'index si nécessaire après filtrage
  useEffect(() => {
    if (currentArticleIndex >= filteredArticles.length && filteredArticles.length > 0) {
      setCurrentArticleIndex(0)
    } else if (filteredArticles.length === 0 && currentArticleIndex > 0) {
      setCurrentArticleIndex(0)
    }
  }, [filteredArticles.length, currentArticleIndex])

  const currentArticles = filteredArticles
  const currentArticle = currentArticles.length > 0 
    ? currentArticles[Math.min(currentArticleIndex, currentArticles.length - 1)]
    : null

  const handleModeSelect = (selectedMode) => {
    setMode(selectedMode)
    setCurrentLaw('LAPM')
    setCurrentArticleIndex(0)
  }

  const handleNext = () => {
    if (currentArticleIndex < currentArticles.length - 1) {
      setCurrentArticleIndex(currentArticleIndex + 1)
    } else {
      setCurrentArticleIndex(0) // Retour au début
    }
  }

  const handlePrevious = () => {
    if (currentArticleIndex > 0) {
      setCurrentArticleIndex(currentArticleIndex - 1)
    } else {
      setCurrentArticleIndex(currentArticles.length - 1) // Aller à la fin
    }
  }

  const handleLawChange = (law) => {
    setCurrentLaw(law)
    setCurrentArticleIndex(0) // Réinitialiser l'index lors du changement de loi
    setSearchQuery('') // Réinitialiser la recherche lors du changement de loi
  }

  const handleModeChange = () => {
    // Change de mode (course <-> complete)
    const newMode = mode === 'course' ? 'complete' : 'course'
    setMode(newMode)
    setCurrentLaw('LAPM')
    setCurrentArticleIndex(0)
  }

  const handleBackToModeSelector = () => {
    setMode(null)
    setCurrentLaw('LAPM')
    setCurrentArticleIndex(0)
  }

  // Affiche le sélecteur de mode si aucun mode n'est sélectionné
  if (mode === null) {
    return (
      <ModeSelector 
        onModeSelect={handleModeSelect} 
        darkMode={darkMode}
        onDarkModeToggle={() => setDarkMode(!darkMode)}
      />
    )
  }

  // Affiche le mode examen
  if (mode === 'exam') {
    return (
      <div className={`app ${darkMode ? 'dark-mode' : ''}`}>
        <header className="app-header">
          <div className="mode-controls">
            <button 
              onClick={handleBackToModeSelector}
              className="mode-selector-button"
              title="Retour au sélecteur de mode"
            >
              ⚙️
            </button>
            <button 
              onClick={() => setDarkMode(!darkMode)}
              className="dark-mode-toggle"
              title={darkMode ? 'Mode clair' : 'Mode sombre'}
            >
              {darkMode ? '☀️' : '🌙'}
            </button>
          </div>
        </header>
        <Exam 
          data={dataComplete} 
          darkMode={darkMode}
        />
      </div>
    )
  }

  return (
    <div className={`app ${darkMode ? 'dark-mode' : ''}`}>
      <header className="app-header">
        <h1>Révision LAPM / RAPM</h1>
        <div className="mode-controls">
          <button 
            onClick={handleModeChange}
            className="mode-switch-button"
            title="Changer de mode"
          >
            {mode === 'course' ? '📚 Selon PDF du cours' : '📖 Tous les articles'}
            <span className="mode-switch-icon">🔄</span>
          </button>
          <button 
            onClick={handleBackToModeSelector}
            className="mode-selector-button"
            title="Retour au sélecteur de mode"
          >
            ⚙️
          </button>
          <button 
            onClick={() => setDarkMode(!darkMode)}
            className="dark-mode-toggle"
            title={darkMode ? 'Mode clair' : 'Mode sombre'}
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
        <div className="search-container">
          <input
            type="text"
            placeholder="Rechercher un article..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value)
              setCurrentArticleIndex(0)
            }}
            className="search-input"
          />
          {searchQuery && (
            <button
              onClick={() => {
                setSearchQuery('')
                setCurrentArticleIndex(0)
              }}
              className="search-clear"
              title="Effacer la recherche"
            >
              ✕
            </button>
          )}
        </div>
        {searchQuery && (
          <div className="search-results-info">
            {currentArticles.length} article{currentArticles.length > 1 ? 's' : ''} trouvé{currentArticles.length > 1 ? 's' : ''}
          </div>
        )}
        <Navigation 
          currentLaw={currentLaw} 
          onLawChange={handleLawChange}
          currentIndex={currentArticleIndex}
          totalArticles={currentArticles.length}
        />
        <div className="view-toggle">
          <button
            onClick={() => setViewMode('flashcard')}
            className={`view-button ${viewMode === 'flashcard' ? 'active' : ''}`}
          >
            📇 Cartes
          </button>
          <button
            onClick={() => setViewMode('tree')}
            className={`view-button ${viewMode === 'tree' ? 'active' : ''}`}
          >
            🌳 Arborescence
          </button>
        </div>
      </header>
      
      <main className="app-main">
        {viewMode === 'flashcard' ? (
          <>
            {currentArticle ? (
              <>
                <div className="flashcard-container">
                  <Flashcard 
                    article={currentArticle}
                    lawTitle={data[currentLaw].title}
                  />
                </div>
                
                <div className="navigation-controls">
                  <button 
                    onClick={handlePrevious}
                    className="nav-button prev-button"
                    aria-label="Article précédent"
                    disabled={currentArticles.length === 0}
                  >
                    ← Précédent
                  </button>
                  
                  <span className="article-counter">
                    {currentArticleIndex + 1} / {currentArticles.length}
                  </span>
                  
                  <button 
                    onClick={handleNext}
                    className="nav-button next-button"
                    aria-label="Article suivant"
                    disabled={currentArticles.length === 0}
                  >
                    Suivant →
                  </button>
                </div>
              </>
            ) : (
              <div className="no-results">
                <p>Aucun article trouvé pour "{searchQuery}"</p>
                <button 
                  onClick={() => setSearchQuery('')}
                  className="clear-search-button"
                >
                  Effacer la recherche
                </button>
              </div>
            )}
          </>
        ) : (
          <TreeView data={data} currentLaw={currentLaw} searchQuery={searchQuery} />
        )}
      </main>
    </div>
  )
}

export default App
