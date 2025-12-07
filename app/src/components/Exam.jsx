import { useState, useMemo, useEffect } from 'react'
import './Exam.css'

function Exam({ data, darkMode }) {
  const [currentLaw, setCurrentLaw] = useState('LAPM')
  const [questions, setQuestions] = useState([])
  const [userAnswers, setUserAnswers] = useState({})
  const [submitted, setSubmitted] = useState(false)
  const [attempt, setAttempt] = useState(1)

  // Génère les questions à partir des articles
  const generateQuestions = useMemo(() => {
    const allQuestions = []
    
    // Parcourir tous les articles de toutes les lois
    Object.keys(data).forEach(lawKey => {
      data[lawKey].articles.forEach(article => {
        // Ne créer une question que si l'article a des détails
        if (article.details && article.details.length > 0) {
          allQuestions.push({
            id: `${lawKey}-${article.number}`,
            law: lawKey,
            articleNumber: article.number,
            articleTitle: article.title,
            correctAnswers: article.details,
            question: `Que pouvez-vous me dire sur l'article ${article.number} qui traite de ${article.title} ?`
          })
        }
      })
    })
    
    return allQuestions
  }, [data])

  // Réinitialise les questions et réponses à chaque tentative
  useEffect(() => {
    // Génère les options pour toutes les questions
    const generateQuestionOptions = (questions) => {
      const allArticles = []
      Object.keys(data).forEach(lawKey => {
        data[lawKey].articles.forEach(article => {
          allArticles.push({
            number: article.number,
            law: lawKey,
            details: article.details || []
          })
        })
      })

      return questions.map(question => {
        const distractors = []
        const usedDetails = new Set()
        
        // Collecter tous les détails des autres articles
        allArticles.forEach(article => {
          if (article.number !== question.articleNumber || article.law !== question.law) {
            article.details?.forEach(detail => {
              if (!usedDetails.has(detail)) {
                distractors.push(detail)
                usedDetails.add(detail)
              }
            })
          }
        })
        
        // Mélanger et prendre un nombre aléatoire de distracteurs
        const shuffled = distractors.sort(() => Math.random() - 0.5)
        const numDistractors = Math.min(
          Math.floor(Math.random() * 3) + 2, // Entre 2 et 4 distracteurs
          shuffled.length
        )
        
        const selectedDistractors = shuffled.slice(0, numDistractors)
        const allOptions = [...question.correctAnswers, ...selectedDistractors]
        
        // Mélanger toutes les options
        return {
          ...question,
          options: allOptions.sort(() => Math.random() - 0.5)
        }
      })
    }

    // Mélange les questions de manière aléatoire
    const shuffled = [...generateQuestions].sort(() => Math.random() - 0.5)
    // Génère les options pour chaque question
    const questionsWithOptions = generateQuestionOptions(shuffled)
    setQuestions(questionsWithOptions)
    setUserAnswers({})
    setSubmitted(false)
  }, [generateQuestions, attempt, data])


  const handleAnswerChange = (questionId, option, isChecked) => {
    setUserAnswers(prev => {
      const current = prev[questionId] || []
      if (isChecked) {
        return { ...prev, [questionId]: [...current, option] }
      } else {
        return { ...prev, [questionId]: current.filter(a => a !== option) }
      }
    })
  }

  const handleSubmit = () => {
    setSubmitted(true)
  }

  const handleNewAttempt = () => {
    setAttempt(prev => prev + 1)
  }

  const isCorrect = (questionId, option) => {
    const question = questions.find(q => q.id === questionId)
    if (!question) return false
    return question.correctAnswers.includes(option)
  }

  const isSelected = (questionId, option) => {
    return userAnswers[questionId]?.includes(option) || false
  }

  const isWrongSelection = (questionId, option) => {
    return isSelected(questionId, option) && !isCorrect(questionId, option)
  }

  const isCorrectSelection = (questionId, option) => {
    return isSelected(questionId, option) && isCorrect(questionId, option)
  }

  const isMissedCorrect = (questionId, option) => {
    return !isSelected(questionId, option) && isCorrect(questionId, option)
  }

  const getScore = () => {
    let totalCorrect = 0
    let totalQuestions = 0
    
    questions.forEach(question => {
      const userSelections = userAnswers[question.id] || []
      const correctCount = question.correctAnswers.filter(answer => 
        userSelections.includes(answer)
      ).length
      const incorrectCount = userSelections.filter(answer => 
        !question.correctAnswers.includes(answer)
      ).length
      
      // Score basé sur les bonnes réponses moins les mauvaises
      const questionScore = Math.max(0, correctCount - incorrectCount)
      totalCorrect += questionScore
      totalQuestions += question.correctAnswers.length
    })
    
    return { correct: totalCorrect, total: totalQuestions }
  }

  const score = submitted ? getScore() : null

  return (
    <div className={`exam-container ${darkMode ? 'dark-mode' : ''}`}>
      <div className="exam-header">
        <h1>Mode Examen</h1>
        <div className="exam-controls">
          <div className="law-selector-exam">
            <button
              className={`law-button-exam ${currentLaw === 'LAPM' ? 'active' : ''}`}
              onClick={() => setCurrentLaw('LAPM')}
            >
              LAPM
            </button>
            <button
              className={`law-button-exam ${currentLaw === 'RAPM' ? 'active' : ''}`}
              onClick={() => setCurrentLaw('RAPM')}
            >
              RAPM
            </button>
            <button
              className={`law-button-exam ${currentLaw === 'ALL' ? 'active' : ''}`}
              onClick={() => setCurrentLaw('ALL')}
            >
              Tous
            </button>
          </div>
          {submitted && (
            <div className="exam-score">
              Score: {score.correct} / {score.total}
            </div>
          )}
        </div>
      </div>

      <div className="exam-content">
        {questions
          .filter(q => currentLaw === 'ALL' || q.law === currentLaw)
          .map((question, index) => {
            const options = question.options || []
            
            return (
              <div key={question.id} className="exam-question">
                <div className="question-header">
                  <h3>Question {index + 1}</h3>
                  <span className="question-law">{question.law}</span>
                </div>
                <p className="question-text">{question.question}</p>
                
                <div className="options-container">
                  {options.map((option, optIndex) => {
                    const optionId = `${question.id}-${optIndex}`
                    const selected = isSelected(question.id, option)
                    let optionClass = 'option'
                    
                    if (submitted) {
                      if (isWrongSelection(question.id, option)) {
                        optionClass += ' wrong'
                      } else if (isCorrectSelection(question.id, option)) {
                        optionClass += ' correct'
                      } else if (isMissedCorrect(question.id, option)) {
                        optionClass += ' missed'
                      } else if (isCorrect(question.id, option)) {
                        optionClass += ' correct-not-selected'
                      }
                    }
                    
                    return (
                      <label key={optIndex} className={optionClass}>
                        <input
                          type="checkbox"
                          checked={selected}
                          onChange={(e) => handleAnswerChange(question.id, option, e.target.checked)}
                          disabled={submitted}
                        />
                        <span className="option-text">{option}</span>
                      </label>
                    )
                  })}
                </div>
              </div>
            )
          })}
      </div>

      <div className="exam-footer">
        {!submitted ? (
          <button 
            className="submit-button"
            onClick={handleSubmit}
            disabled={questions.filter(q => currentLaw === 'ALL' || q.law === currentLaw).length === 0}
          >
            Soumettre les réponses
          </button>
        ) : (
          <button 
            className="new-attempt-button"
            onClick={handleNewAttempt}
          >
            Nouvelle tentative (tentative {attempt + 1})
          </button>
        )}
      </div>
    </div>
  )
}

export default Exam

