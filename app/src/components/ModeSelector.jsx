import './ModeSelector.css'

function ModeSelector({ onModeSelect }) {
  return (
    <div className="mode-selector">
      <div className="mode-selector-content">
        <h1>Révision LAPM / RAPM</h1>
        <p className="mode-selector-subtitle">Choisissez votre mode de révision :</p>
        
        <div className="mode-options">
          <button
            className="mode-button"
            onClick={() => onModeSelect('course')}
          >
            <div className="mode-icon">📚</div>
            <div className="mode-title">Selon PDF du cours</div>
            <div className="mode-description">
              Accès aux articles sélectionnés du cours
            </div>
          </button>
          
          <button
            className="mode-button"
            onClick={() => onModeSelect('complete')}
          >
            <div className="mode-icon">📖</div>
            <div className="mode-title">Tous les articles</div>
            <div className="mode-description">
              Accès à tous les articles de la LAPM et du RAPM
            </div>
          </button>
        </div>
      </div>
    </div>
  )
}

export default ModeSelector

