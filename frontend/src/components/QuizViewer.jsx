import React, { useState, useMemo } from 'react';
import { FaCheck, FaTimes, FaRedo } from 'react-icons/fa';

const QuizViewer = ({ content }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [answeredQuestions, setAnsweredQuestions] = useState([]);

  // Parse quiz from content
  const questions = useMemo(() => {
    try {
      const data = JSON.parse(content);
      return Array.isArray(data) ? data : [];
    } catch {
      return parseTextQuiz(content);
    }
  }, [content]);

  const currentQuestion = questions[currentIndex];

  const handleAnswerSelect = (index) => {
    if (showResult) return;
    setSelectedAnswer(index);
  };

  const handleSubmitAnswer = () => {
    if (selectedAnswer === null) return;

    setShowResult(true);
    const isCorrect = selectedAnswer === currentQuestion.correctAnswer;

    if (isCorrect && !answeredQuestions.includes(currentIndex)) {
      setScore(score + 1);
      setAnsweredQuestions([...answeredQuestions, currentIndex]);
    }
  };

  const handleNextQuestion = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setSelectedAnswer(null);
      setShowResult(false);
    } else {
      setCompleted(true);
    }
  };

  const handleRestart = () => {
    setCurrentIndex(0);
    setSelectedAnswer(null);
    setShowResult(false);
    setScore(0);
    setCompleted(false);
    setAnsweredQuestions([]);
  };

  if (questions.length === 0) {
    return (
      <div className="quiz-viewer">
        <div className="quiz-empty">No quiz questions available</div>
      </div>
    );
  }

  if (completed) {
    return (
      <div className="quiz-viewer">
        <div className="quiz-completed">
          <h2>Quiz Complete!</h2>
          <div className="quiz-score">
            Your Score: {score} / {questions.length}
          </div>
          <div className="quiz-percentage">
            {Math.round((score / questions.length) * 100)}%
          </div>
          <button onClick={handleRestart} className="quiz-restart-button">
            <FaRedo /> Restart Quiz
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="quiz-viewer">
      <div className="quiz-progress">
        Question {currentIndex + 1} of {questions.length}
        <div className="quiz-progress-bar">
          <div
            className="quiz-progress-fill"
            style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
          ></div>
        </div>
      </div>

      <div className="quiz-question">
        <h3>{currentQuestion.question}</h3>
      </div>

      <div className="quiz-options">
        {currentQuestion.options.map((option, index) => {
          let className = 'quiz-option';
          if (showResult) {
            if (index === currentQuestion.correctAnswer) {
              className += ' correct';
            } else if (index === selectedAnswer && index !== currentQuestion.correctAnswer) {
              className += ' incorrect';
            }
          } else if (index === selectedAnswer) {
            className += ' selected';
          }

          return (
            <button
              key={index}
              onClick={() => handleAnswerSelect(index)}
              className={className}
              disabled={showResult}
            >
              <span className="option-label">{String.fromCharCode(65 + index)}.</span>
              <span className="option-text">{option}</span>
              {showResult && index === currentQuestion.correctAnswer && (
                <FaCheck className="option-icon correct-icon" />
              )}
              {showResult &&
                index === selectedAnswer &&
                index !== currentQuestion.correctAnswer && (
                  <FaTimes className="option-icon incorrect-icon" />
                )}
            </button>
          );
        })}
      </div>

      {showResult && currentQuestion.explanation && (
        <div className="quiz-explanation">
          <strong>Explanation:</strong> {currentQuestion.explanation}
        </div>
      )}

      <div className="quiz-actions">
        {!showResult ? (
          <button
            onClick={handleSubmitAnswer}
            disabled={selectedAnswer === null}
            className="quiz-submit-button"
          >
            Submit Answer
          </button>
        ) : (
          <button onClick={handleNextQuestion} className="quiz-next-button">
            {currentIndex < questions.length - 1 ? 'Next Question' : 'Finish Quiz'}
          </button>
        )}
      </div>

      <div className="quiz-score-display">Current Score: {score}</div>
    </div>
  );
};

// Parse text-based quiz
const parseTextQuiz = (text) => {
  const questions = [];
  const sections = text.split(/\n\s*\n/);

  sections.forEach((section) => {
    const lines = section.split('\n').filter((l) => l.trim());
    if (lines.length < 2) return;

    let question = '';
    let options = [];
    let correctAnswer = -1;
    let explanation = '';

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();

      // Question line
      if (line.match(/^\d+\.|^Q\d*:|^Question/i)) {
        question = line.replace(/^\d+\.|^Q\d*:|^Question\s*\d*:?\s*/i, '');
      }
      // Options (A, B, C, D or a, b, c, d)
      else if (line.match(/^[a-dA-D][\)\.]\s*/)) {
        const optionText = line.replace(/^[a-dA-D][\)\.]\s*/, '');
        // Check if this is the correct answer (marked with * or ✓)
        if (optionText.match(/^\*|^✓|^\[correct\]/i)) {
          correctAnswer = options.length;
          options.push(optionText.replace(/^\*|^✓|^\[correct\]\s*/i, ''));
        } else {
          options.push(optionText);
        }
      }
      // Correct answer marker
      else if (line.match(/^(Answer|Correct):/i)) {
        const answerLetter = line.replace(/^(Answer|Correct):\s*/i, '').charAt(0).toUpperCase();
        correctAnswer = answerLetter.charCodeAt(0) - 65; // A=0, B=1, etc.
      }
      // Explanation
      else if (line.match(/^Explanation:/i)) {
        explanation = line.replace(/^Explanation:\s*/i, '');
      }
    }

    if (question && options.length >= 2) {
      // If no correct answer was marked, default to first option
      if (correctAnswer === -1) correctAnswer = 0;

      questions.push({
        question,
        options,
        correctAnswer,
        explanation,
      });
    }
  });

  return questions.length > 0
    ? questions
    : [
        {
          question: 'Sample Question?',
          options: ['Option A', 'Option B', 'Option C', 'Option D'],
          correctAnswer: 0,
          explanation: 'This is a sample explanation.',
        },
      ];
};

export default QuizViewer;
