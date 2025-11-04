import { useState, useEffect, useRef, useCallback } from 'react'
import { FiBookmark, FiFolder, FiX, FiPlus, FiTrash2, FiRefreshCw, FiLoader, FiChevronUp, FiChevronDown } from 'react-icons/fi'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

const CARD_TYPES = ['fun_fact', 'mnemonic', 'key_concept', 'quote', 'summary', 'tip', 'question', 'definition']

const CARD_COLORS = [
  { bg: 'linear-gradient(180deg, rgba(18, 18, 18, 1) 0%, rgba(12, 12, 12, 1) 100%)', name: 'Default' },
  { bg: 'linear-gradient(180deg, rgba(22, 18, 18, 1) 0%, rgba(15, 12, 12, 1) 100%)', name: 'Warm' },
  { bg: 'linear-gradient(180deg, rgba(18, 18, 22, 1) 0%, rgba(12, 12, 15, 1) 100%)', name: 'Cool' },
  { bg: 'linear-gradient(180deg, rgba(18, 20, 18, 1) 0%, rgba(12, 14, 12, 1) 100%)', name: 'Green' },
  { bg: 'linear-gradient(180deg, rgba(20, 18, 18, 1) 0%, rgba(14, 12, 12, 1) 100%)', name: 'Rose' },
  { bg: 'linear-gradient(180deg, rgba(18, 19, 20, 1) 0%, rgba(12, 13, 14, 1) 100%)', name: 'Slate' },
  { bg: 'linear-gradient(180deg, rgba(19, 18, 20, 1) 0%, rgba(13, 12, 14, 1) 100%)', name: 'Purple' },
  { bg: 'linear-gradient(180deg, rgba(18, 20, 20, 1) 0%, rgba(12, 14, 14, 1) 100%)', name: 'Cyan' }
]

function Doomscroll({ documents, notebookId }) {
  const [cards, setCards] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [likedCards, setLikedCards] = useState(new Set())
  const [showGallery, setShowGallery] = useState(false)
  const [savedCards, setSavedCards] = useState([])
  const [folders, setFolders] = useState([])
  const [showFolderModal, setShowFolderModal] = useState(false)
  const [newFolderName, setNewFolderName] = useState('')
  const [selectedFolder, setSelectedFolder] = useState(null)
  const [cardToOrganize, setCardToOrganize] = useState(null)
  const [hasMore, setHasMore] = useState(true)
  const [statusMessage, setStatusMessage] = useState('')

  const containerRef = useRef(null)
  const isGeneratingRef = useRef(false)
  const cardsRef = useRef([])

  useEffect(() => {
    if (notebookId && documents.length > 0) {
      setCards([])
      cardsRef.current = []
      setHasMore(true)
      setStatusMessage('')
      generateCards()
      fetchSavedCards()
      fetchFolders()
    } else {
      setCards([])
      cardsRef.current = []
      setStatusMessage('')
      setHasMore(true)
    }
  }, [notebookId, documents])

  useEffect(() => {
    cardsRef.current = cards
  }, [cards])

  const generateCards = async () => {
    if (isGeneratingRef.current || !hasMore) return

    isGeneratingRef.current = true
    setIsLoading(true)

    try {
      const response = await axios.post(`${API_URL}/doomscroll/generate`, {
        notebook_id: notebookId,
        count: 10
      })

      const responseData = response.data || {}
      const existingCount = cardsRef.current.length
      const newCards = (responseData.cards || []).map((card, idx) => ({
        ...card,
        id: `${Date.now()}-${idx}`,
        color: CARD_COLORS[Math.floor(Math.random() * CARD_COLORS.length)]
      }))

      if (newCards.length < 10) {
        setHasMore(false)
      }

      if (newCards.length === 0) {
        const message = responseData.message || (existingCount === 0
          ? 'No cards available yet. Try uploading documents or regenerating after adding more content.'
          : 'No more cards available from the current documents.')
        setStatusMessage(message)
      } else {
        setStatusMessage('')
        setCards(prev => {
          const updated = [...prev, ...newCards]
          cardsRef.current = updated
          return updated
        })
      }
    } catch (error) {
      console.error('Error generating cards:', error)
      const errorMessage = error.response?.data?.detail || 'Unable to generate cards right now. Please try again.'
      setStatusMessage(errorMessage)
      setHasMore(false)
    } finally {
      setIsLoading(false)
      isGeneratingRef.current = false
    }
  }

  const fetchSavedCards = async () => {
    try {
      const response = await axios.get(`${API_URL}/doomscroll/saved/${notebookId}`)
      setSavedCards(response.data.cards)
      const liked = new Set(response.data.cards.map(c => c.card_id))
      setLikedCards(liked)
    } catch (error) {
      console.error('Error fetching saved cards:', error)
    }
  }

  const fetchFolders = async () => {
    try {
      const response = await axios.get(`${API_URL}/doomscroll/folders/${notebookId}`)
      setFolders(response.data.folders)
    } catch (error) {
      console.error('Error fetching folders:', error)
    }
  }

  const handleScroll = useCallback(() => {
    if (!containerRef.current) return

    const container = containerRef.current
    const scrollTop = container.scrollTop
    const cardHeight = container.clientHeight
    const newIndex = Math.round(scrollTop / cardHeight)

    if (newIndex !== currentIndex) {
      setCurrentIndex(newIndex)
    }

    // Generate more cards when near the end
    if (newIndex >= cards.length - 3 && !isGeneratingRef.current && hasMore) {
      generateCards()
    }
  }, [currentIndex, cards.length, hasMore])

  useEffect(() => {
    const container = containerRef.current
    if (container) {
      container.addEventListener('scroll', handleScroll)
      return () => container.removeEventListener('scroll', handleScroll)
    }
  }, [handleScroll])

  const toggleLike = async (card) => {
    const cardKey = card.id

    if (likedCards.has(cardKey)) {
      // Unlike
      try {
        await axios.delete(`${API_URL}/doomscroll/saved/${notebookId}/${cardKey}`)
        setLikedCards(prev => {
          const newSet = new Set(prev)
          newSet.delete(cardKey)
          return newSet
        })
        await fetchSavedCards()
      } catch (error) {
        console.error('Error unliking card:', error)
      }
    } else {
      // Like
      try {
        await axios.post(`${API_URL}/doomscroll/like`, {
          notebook_id: notebookId,
          card_id: cardKey,
          type: card.type,
          title: card.title,
          content: card.content,
          color: card.color.bg
        })
        setLikedCards(prev => new Set([...prev, cardKey]))
        await fetchSavedCards()
      } catch (error) {
        console.error('Error liking card:', error)
      }
    }
  }

  const createFolder = async () => {
    if (!newFolderName.trim()) return

    try {
      await axios.post(`${API_URL}/doomscroll/folders`, {
        notebook_id: notebookId,
        name: newFolderName
      })
      setNewFolderName('')
      await fetchFolders()
    } catch (error) {
      console.error('Error creating folder:', error)
    }
  }

  const deleteFolder = async (folderId) => {
    if (!window.confirm('Delete this folder? Cards will be moved to uncategorized.')) return

    try {
      await axios.delete(`${API_URL}/doomscroll/folders/${folderId}`)
      await fetchFolders()
      await fetchSavedCards()
    } catch (error) {
      console.error('Error deleting folder:', error)
    }
  }

  const moveCardToFolder = async (cardId, folderId) => {
    try {
      await axios.put(`${API_URL}/doomscroll/card/${cardId}/folder`, {
        folder_id: folderId
      })
      await fetchSavedCards()
      setCardToOrganize(null)
    } catch (error) {
      console.error('Error moving card:', error)
    }
  }

  const regenerateCards = () => {
    setCards([])
    cardsRef.current = []
    setCurrentIndex(0)
    setHasMore(true)
    setStatusMessage('')
    if (containerRef.current) {
      containerRef.current.scrollTop = 0
    }
    generateCards()
  }

  const scrollToNext = () => {
    if (!containerRef.current || currentIndex >= cards.length - 1) return
    const container = containerRef.current
    const nextIndex = currentIndex + 1
    container.scrollTo({
      top: nextIndex * container.clientHeight,
      behavior: 'smooth'
    })
  }

  const scrollToPrevious = () => {
    if (!containerRef.current || currentIndex <= 0) return
    const container = containerRef.current
    const prevIndex = currentIndex - 1
    container.scrollTo({
      top: prevIndex * container.clientHeight,
      behavior: 'smooth'
    })
  }

  const getCardIcon = (type) => {
    const icons = {
      fun_fact: '🎯',
      mnemonic: '🧠',
      key_concept: '💡',
      quote: '💬',
      summary: '📝',
      tip: '✨',
      question: '❓',
      definition: '📖'
    }
    return icons[type] || '📌'
  }

  const getCardTypeLabel = (type) => {
    return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  if (documents.length === 0) {
    return (
      <div className="doomscroll-container">
        <div className="doomscroll-empty">
          <div className="doomscroll-empty-icon">📱</div>
          <h2>No Documents to Scroll</h2>
          <p>Upload some documents first to start doomscrolling through learning cards!</p>
        </div>
      </div>
    )
  }

  return (
    <div className="doomscroll-container">
      {/* Header Controls */}
      <div className="doomscroll-header">
        <button className="doomscroll-header-btn" onClick={regenerateCards} title="Regenerate Cards">
          <FiRefreshCw />
        </button>
        <button
          className="doomscroll-header-btn"
          onClick={() => setShowGallery(true)}
          title="Saved Cards"
        >
          <FiFolder />
          {savedCards.length > 0 && (
            <span className="badge">{savedCards.length}</span>
          )}
        </button>
      </div>

      {/* Fixed Action Buttons (Right Side) */}
      {cards.length > 0 && (
        <div className="doomscroll-card-actions">
          <button
            className="doomscroll-scroll-btn"
            onClick={scrollToPrevious}
            disabled={currentIndex === 0}
            title="Previous Card"
          >
            <FiChevronUp />
          </button>

          <button
            className={`doomscroll-action-btn ${cards[currentIndex] && likedCards.has(cards[currentIndex].id) ? 'liked' : ''}`}
            onClick={() => cards[currentIndex] && toggleLike(cards[currentIndex])}
            title="Save Card"
          >
            <FiBookmark />
          </button>

          <button
            className="doomscroll-scroll-btn"
            onClick={scrollToNext}
            disabled={currentIndex >= cards.length - 1}
            title="Next Card"
          >
            <FiChevronDown />
          </button>
        </div>
      )}

      {/* Progress Indicator */}
      {cards.length > 0 && (
        <div className="doomscroll-card-progress">
          {currentIndex + 1} / {cards.length}
        </div>
      )}

      {/* Cards Scroll Container */}
      <div className="doomscroll-cards" ref={containerRef}>
        {!isLoading && cards.length === 0 && statusMessage && (
          <div className="doomscroll-card doomscroll-empty-card">
            <p>{statusMessage}</p>
            <button className="regenerate-btn" onClick={regenerateCards}>
              <FiRefreshCw /> Try Again
            </button>
          </div>
        )}

        {cards.map((card, index) => (
          <div
            key={card.id}
            className="doomscroll-card"
            style={{ background: card.color.bg }}
          >
            <div className="doomscroll-card-content">
              <div className="doomscroll-card-type">
                <span className="type-icon">{getCardIcon(card.type)}</span>
                <span className="type-label">{getCardTypeLabel(card.type)}</span>
              </div>

              <h3 className="doomscroll-card-title">{card.title}</h3>
              <p className="doomscroll-card-text">{card.content}</p>

              {card.example && (
                <div className="doomscroll-card-example">
                  <strong>Example:</strong> {card.example}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="doomscroll-card doomscroll-loading-card">
            <FiLoader className="spin" size={48} />
            <p>Generating more cards...</p>
          </div>
        )}

        {!hasMore && cards.length > 0 && (
          <div className="doomscroll-card doomscroll-end-card">
            <div className="doomscroll-end-content">
              <span className="end-icon">🎉</span>
              <h2>You've reached the end!</h2>
              <p>That's all the content from your documents.</p>
              <button className="regenerate-btn" onClick={regenerateCards}>
                <FiRefreshCw /> Start Over
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Gallery Modal */}
      {showGallery && (
        <div className="modal-overlay" onClick={() => setShowGallery(false)}>
          <div className="modal doomscroll-gallery-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                <FiFolder /> Saved Cards ({savedCards.length})
              </h2>
              <button onClick={() => setShowGallery(false)} className="close-button">
                <FiX size={20} />
              </button>
            </div>

            <div className="modal-body">
              {/* Folder Management */}
              <div className="folder-section">
                <div className="folder-header">
                  <h3>Folders</h3>
                  <button
                    className="icon-button"
                    onClick={() => setShowFolderModal(true)}
                  >
                    <FiPlus />
                  </button>
                </div>

                <div className="folder-list">
                  <button
                    className={`folder-item ${selectedFolder === null ? 'active' : ''}`}
                    onClick={() => setSelectedFolder(null)}
                  >
                    <FiFolder />
                    <span>All Cards</span>
                    <span className="folder-count">{savedCards.length}</span>
                  </button>

                  {folders.map(folder => (
                    <div key={folder.id} className="folder-item-wrapper">
                      <button
                        className={`folder-item ${selectedFolder === folder.id ? 'active' : ''}`}
                        onClick={() => setSelectedFolder(folder.id)}
                      >
                        <FiFolder />
                        <span>{folder.name}</span>
                        <span className="folder-count">
                          {savedCards.filter(c => c.folder_id === folder.id).length}
                        </span>
                      </button>
                      <button
                        className="folder-delete"
                        onClick={() => deleteFolder(folder.id)}
                      >
                        <FiTrash2 size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Saved Cards Grid */}
              <div className="saved-cards-grid">
                {savedCards
                  .filter(card => selectedFolder === null || card.folder_id === selectedFolder)
                  .map(card => (
                    <div
                      key={card.id}
                      className="saved-card-item"
                      style={{ background: card.color }}
                    >
                      <div className="saved-card-type">
                        {getCardIcon(card.type)} {getCardTypeLabel(card.type)}
                      </div>
                      <h4>{card.title}</h4>
                      <p>{card.content.substring(0, 100)}...</p>
                      <div className="saved-card-actions">
                        <button
                          className="organize-btn"
                          onClick={() => setCardToOrganize(card)}
                        >
                          <FiFolder size={14} /> Organize
                        </button>
                        <button
                          className="delete-btn"
                          onClick={() => toggleLike({ id: card.card_id })}
                        >
                          <FiTrash2 size={14} />
                        </button>
                      </div>
                    </div>
                  ))}

                {savedCards.length === 0 && (
                  <div className="empty-saved-cards">
                    <p>No saved cards yet. Heart cards while scrolling to save them!</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Folder Modal */}
      {showFolderModal && (
        <div className="modal-overlay" onClick={() => setShowFolderModal(false)}>
          <div className="modal small-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create Folder</h2>
              <button onClick={() => setShowFolderModal(false)} className="close-button">
                <FiX size={20} />
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Folder Name</label>
                <input
                  type="text"
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  placeholder="e.g., Important Concepts"
                  autoFocus
                  onKeyDown={(e) => e.key === 'Enter' && createFolder()}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="cancel-button" onClick={() => setShowFolderModal(false)}>
                Cancel
              </button>
              <button className="confirm-button" onClick={() => { createFolder(); setShowFolderModal(false); }}>
                Create
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Organize Card Modal */}
      {cardToOrganize && (
        <div className="modal-overlay" onClick={() => setCardToOrganize(null)}>
          <div className="modal small-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Move to Folder</h2>
              <button onClick={() => setCardToOrganize(null)} className="close-button">
                <FiX size={20} />
              </button>
            </div>
            <div className="modal-body">
              <div className="organize-folder-list">
                <button
                  className="organize-folder-btn"
                  onClick={() => moveCardToFolder(cardToOrganize.id, null)}
                >
                  <FiFolder />
                  <span>Uncategorized</span>
                </button>
                {folders.map(folder => (
                  <button
                    key={folder.id}
                    className="organize-folder-btn"
                    onClick={() => moveCardToFolder(cardToOrganize.id, folder.id)}
                  >
                    <FiFolder />
                    <span>{folder.name}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Doomscroll
