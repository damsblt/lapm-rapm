import { useState } from 'react'
import './Flashcard.css'

function Flashcard({ article, lawTitle }) {
  const [isFlipped, setIsFlipped] = useState(false)

  const handleFlip = () => {
    setIsFlipped(!isFlipped)
  }

  // Fonction pour convertir le markdown en HTML
  const formatText = (text) => {
    if (!text) return ''
    // Convertit **texte** en <strong>texte</strong> (gère plusieurs occurrences)
    // Utilise une regex pour capturer chaque occurrence, même avec des caractères spéciaux
    let formatted = text.replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>')
    // Convertit les sauts de ligne en <br>
    formatted = formatted.split('\n').join('<br/>')
    return formatted
  }

  return (
    <div 
      className={`flashcard ${isFlipped ? 'flipped' : ''}`}
      onClick={handleFlip}
    >
      <div className="flashcard-inner">
        {/* Recto */}
        <div className="flashcard-front">
          <div className="flashcard-content">
            <div className="article-number">Art. {article.number}</div>
            <div className="article-title">{article.title}</div>
          </div>
        </div>

        {/* Verso */}
        <div className="flashcard-back">
          <div className="flashcard-content">
            <div className="article-number">Art. {article.number}</div>
            <div className="article-title">{article.title}</div>
            <div className="article-details">
              <ul>
                {article.details.map((detail, index) => (
                  <li 
                    key={index} 
                    dangerouslySetInnerHTML={{ __html: formatText(detail) }}
                  />
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Flashcard

