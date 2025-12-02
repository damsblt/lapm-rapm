import { useState } from 'react'
import './App.css'
import Flashcard from './components/Flashcard'
import Navigation from './components/Navigation'
import data from './data.json'

function App() {
  const [currentLaw, setCurrentLaw] = useState('LAPM')
  const [currentArticleIndex, setCurrentArticleIndex] = useState(0)

  const currentArticles = data[currentLaw].articles
  const currentArticle = currentArticles[currentArticleIndex]

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

  return (
    <div className="app">
      <header className="app-header">
        <h1>Révision LAPM / RAPM</h1>
        <Navigation 
          currentLaw={currentLaw} 
          onLawChange={handleLawChange}
          currentIndex={currentArticleIndex}
          totalArticles={currentArticles.length}
        />
      </header>
      
      <main className="app-main">
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
      </main>
    </div>
  )
}

export default App
