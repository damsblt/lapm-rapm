import { useState } from 'react'
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

  // Sélectionne les données selon le mode
  const data = mode === 'complete' ? dataComplete : dataCourse

  const currentArticles = data[currentLaw].articles
  const currentArticle = currentArticles[currentArticleIndex]

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
    return <ModeSelector onModeSelect={handleModeSelect} />
  }

  return (
    <div className="app">
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
        </div>
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
              >
                Suivant →
              </button>
            </div>
          </>
        ) : (
          <TreeView data={data} currentLaw={currentLaw} />
        )}
      </main>
    </div>
  )
}

export default App
