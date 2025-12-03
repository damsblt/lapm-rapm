import './Navigation.css'

function Navigation({ currentLaw, onLawChange, currentIndex, totalArticles }) {
  return (
    <nav className="main-navigation">
      <div className="law-selector">
        <button
          className={`law-button ${currentLaw === 'LAPM' ? 'active' : ''}`}
          onClick={() => onLawChange('LAPM')}
        >
          LAPM
        </button>
        <button
          className={`law-button ${currentLaw === 'RAPM' ? 'active' : ''}`}
          onClick={() => onLawChange('RAPM')}
        >
          RAPM
        </button>
      </div>
      <div className="progress-info">
        Article {currentIndex + 1} sur {totalArticles}
      </div>
    </nav>
  )
}

export default Navigation


