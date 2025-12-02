import { useState } from 'react'
import './Flashcard.css'

function Flashcard({ article, lawTitle }) {
  const [isFlipped, setIsFlipped] = useState(false)

  const handleFlip = () => {
    setIsFlipped(!isFlipped)
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
                  <li key={index} style={{ whiteSpace: 'pre-line' }}>{detail}</li>
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

