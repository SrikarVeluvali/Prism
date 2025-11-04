import { useState, useEffect, useRef } from 'react'
import { FiYoutube, FiChevronDown, FiClock, FiMessageSquare, FiPlus, FiX, FiPlay } from 'react-icons/fi'
import axios from 'axios'
import ReactPlayer from 'react-player/youtube'

const API_URL = 'http://localhost:8000'

// Preset annotation colors
const ANNOTATION_COLORS = [
  { name: 'Yellow', value: '#ffeb3b' },
  { name: 'Green', value: '#4caf50' },
  { name: 'Blue', value: '#2196f3' },
  { name: 'Pink', value: '#e91e63' },
  { name: 'Purple', value: '#9c27b0' },
  { name: 'Orange', value: '#ff9800' },
  { name: 'Red', value: '#f44336' },
  { name: 'Cyan', value: '#00bcd4' }
]

function YouTubeViewer({ documents, notebookId, selectedDoc, onDocChange, metadata }) {
  const [videoData, setVideoData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [showDocList, setShowDocList] = useState(false)
  const [playing, setPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)

  // Annotation state
  const [annotations, setAnnotations] = useState([])
  const [showAnnotationForm, setShowAnnotationForm] = useState(false)
  const [annotationNote, setAnnotationNote] = useState('')
  const [annotationColor, setAnnotationColor] = useState('#ffeb3b')
  const [selectedText, setSelectedText] = useState(null)

  const playerRef = useRef(null)
  const transcriptRef = useRef(null)

  useEffect(() => {
    if (selectedDoc && notebookId) {
      fetchVideoData()
      loadAnnotations()
    }
  }, [selectedDoc, notebookId])

  // Auto-scroll transcript to match video time
  useEffect(() => {
    if (transcriptRef.current && videoData?.transcript) {
      const activeEntry = videoData.transcript.find((entry, index) => {
        const nextEntry = videoData.transcript[index + 1]
        return currentTime >= entry.start && (!nextEntry || currentTime < nextEntry.start)
      })

      if (activeEntry) {
        const element = document.getElementById(`transcript-${activeEntry.start}`)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }
    }
  }, [currentTime, videoData])

  const fetchVideoData = async () => {
    setIsLoading(true)
    try {
      const response = await axios.get(
        `${API_URL}/documents/${notebookId}/${selectedDoc.id}/content`
      )
      setVideoData(response.data)
      setDuration(response.data.duration || 0)
    } catch (error) {
      console.error('Error fetching video data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadAnnotations = async () => {
    try {
      const response = await axios.get(
        `${API_URL}/annotations/${notebookId}?document_id=${selectedDoc.id}`
      )
      setAnnotations(response.data.annotations)
    } catch (error) {
      console.error('Error loading annotations:', error)
    }
  }

  const formatTime = (seconds) => {
    const hrs = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)
    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const seekTo = (seconds) => {
    if (playerRef.current) {
      playerRef.current.seekTo(seconds, 'seconds')
      setPlaying(true)
    }
  }

  const handleTranscriptSelection = () => {
    const selection = window.getSelection()
    const selectedText = selection.toString().trim()

    if (selectedText.length > 0) {
      setSelectedText(selectedText)
      setShowAnnotationForm(true)
    }
  }

  const handleTimestampAnnotation = () => {
    setSelectedText(null)
    setShowAnnotationForm(true)
  }

  const createAnnotation = async () => {
    if (!annotationNote.trim() && !selectedText) return

    try {
      const annotationData = {
        notebook_id: notebookId,
        document_id: selectedDoc.id,
        annotation_type: selectedText ? 'both' : 'timestamp',
        color: annotationColor,
        note: annotationNote || null,
        timestamp_start: currentTime,
        timestamp_end: null
      }

      if (selectedText) {
        annotationData.highlighted_text = selectedText
      }

      await axios.post(`${API_URL}/annotations`, annotationData)

      setShowAnnotationForm(false)
      setAnnotationNote('')
      setSelectedText(null)
      loadAnnotations()
    } catch (error) {
      console.error('Error creating annotation:', error)
      alert('Failed to create annotation. Please try again.')
    }
  }

  const deleteAnnotation = async (annotationId) => {
    try {
      await axios.delete(`${API_URL}/annotations/${annotationId}`)
      loadAnnotations()
    } catch (error) {
      console.error('Error deleting annotation:', error)
    }
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{
        padding: '16px 24px',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: 'var(--bg-secondary)',
        gap: '16px'
      }}>
        {/* Back Button */}
        <button
          onClick={() => onDocChange?.(null)}
          style={{
            padding: '8px 12px',
            backgroundColor: 'var(--bg-primary)',
            border: '1px solid var(--border)',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            color: 'var(--text-primary)'
          }}
        >
          ← Back
        </button>

        <div style={{ position: 'relative', flex: 1 }}>
          <button
            onClick={() => setShowDocList(!showDocList)}
            style={{
              padding: '10px 16px',
              backgroundColor: 'var(--bg-primary)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              fontSize: '14px',
              fontWeight: '500',
              width: '100%',
              maxWidth: '500px',
              color: 'var(--text-primary)'
            }}
          >
            <FiYoutube style={{ fontSize: '18px', color: '#ff0000' }} />
            <span style={{ flex: 1, textAlign: 'left' }}>
              {selectedDoc?.filename || 'Select Video'}
            </span>
            <FiChevronDown style={{
              fontSize: '16px',
              transform: showDocList ? 'rotate(180deg)' : 'rotate(0deg)',
              transition: 'transform 0.2s'
            }} />
          </button>

          {showDocList && (
            <div style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              marginTop: '8px',
              maxWidth: '500px',
              backgroundColor: 'var(--bg-primary)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              maxHeight: '300px',
              overflowY: 'auto',
              zIndex: 1000,
              
            }}>
              {documents.map(doc => (
                <button
                  key={doc.id}
                  onClick={() => {
                    onDocChange?.(doc)
                    setShowDocList(false)
                  }}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    backgroundColor: selectedDoc?.id === doc.id ? 'var(--bg-secondary)' : 'transparent',
                    border: 'none',
                    borderBottom: '1px solid var(--border)',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '14px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    color: 'var(--text-primary)'
                  }}
                >
                  <FiYoutube />
                  {doc.filename}
                </button>
              ))}
            </div>
          )}
        </div>

        <button
          onClick={handleTimestampAnnotation}
          style={{
            padding: '8px 16px',
            backgroundColor: 'var(--primary)',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '13px'
          }}
        >
          <FiPlus /> Mark Timestamp
        </button>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {isLoading ? (
          <div style={{
            flex: 1,
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            color: 'var(--text-secondary)'
          }}>
            Loading video...
          </div>
        ) : videoData ? (
          <>
            {/* Left: Video Player */}
            <div style={{
              flex: '0 0 60%',
              display: 'flex',
              flexDirection: 'column',
              padding: '20px',
              backgroundColor: 'var(--bg-primary)'
            }}>
              <div style={{
                position: 'relative',
                paddingTop: '56.25%', // 16:9 aspect ratio
                backgroundColor: '#000',
                borderRadius: '8px',
                overflow: 'hidden'
              }}>
                <ReactPlayer
                  ref={playerRef}
                  url={videoData.source_url}
                  playing={playing}
                  controls
                  width="100%"
                  height="100%"
                  style={{ position: 'absolute', top: 0, left: 0 }}
                  onProgress={({ playedSeconds }) => setCurrentTime(playedSeconds)}
                  onPlay={() => setPlaying(true)}
                  onPause={() => setPlaying(false)}
                  onDuration={setDuration}
                />
              </div>

              {/* Video Info */}
              <div style={{ marginTop: '16px' }}>
                <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px' }}>
                  {videoData.filename}
                </h3>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                  Duration: {formatTime(duration)}
                </p>
              </div>

              {/* Timestamp Annotations */}
              {annotations.filter(ann => ann.annotation_type === 'timestamp' || ann.annotation_type === 'both').length > 0 && (
                <div style={{ marginTop: '24px' }}>
                  <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px' }}>
                    <FiClock style={{ display: 'inline', marginRight: '6px' }} />
                    Bookmarked Moments
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {annotations
                      .filter(ann => ann.annotation_type === 'timestamp' || ann.annotation_type === 'both')
                      .map(ann => (
                        <div
                          key={ann._id}
                          style={{
                            padding: '12px',
                            backgroundColor: 'var(--bg-secondary)',
                            borderRadius: '8px',
                            borderLeft: `4px solid ${ann.color}`,
                            cursor: 'pointer'
                          }}
                          onClick={() => seekTo(ann.timestamp_start)}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                            <div style={{ flex: 1 }}>
                              <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--primary)', marginBottom: '4px' }}>
                                <FiPlay style={{ display: 'inline', marginRight: '4px', fontSize: '12px' }} />
                                {formatTime(ann.timestamp_start)}
                              </div>
                              {ann.note && (
                                <p style={{ fontSize: '13px', margin: 0 }}>{ann.note}</p>
                              )}
                            </div>
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                deleteAnnotation(ann._id)
                              }}
                              style={{
                                background: 'none',
                                border: 'none',
                                cursor: 'pointer',
                                color: 'var(--text-secondary)',
                                padding: '4px'
                              }}
                            >
                              <FiX />
                            </button>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right: Transcript */}
            <div style={{
              flex: '0 0 40%',
              display: 'flex',
              flexDirection: 'column',
              borderLeft: '1px solid var(--border)',
              backgroundColor: 'var(--bg-secondary)'
            }}>
              <div style={{
                padding: '16px 20px',
                borderBottom: '1px solid var(--border)',
                fontWeight: '600',
                fontSize: '14px'
              }}>
                <FiMessageSquare style={{ display: 'inline', marginRight: '8px' }} />
                Transcript
              </div>

              <div
                ref={transcriptRef}
                style={{
                  flex: 1,
                  overflow: 'auto',
                  padding: '16px 20px'
                }}
                onMouseUp={handleTranscriptSelection}
              >
                {videoData.transcript && videoData.transcript.length > 0 ? (
                  videoData.transcript.map((entry, index) => {
                    const isActive = currentTime >= entry.start &&
                      (index === videoData.transcript.length - 1 || currentTime < videoData.transcript[index + 1].start)

                    return (
                      <div
                        key={index}
                        id={`transcript-${entry.start}`}
                        style={{
                          marginBottom: '2px',
                          padding: '12px',
                          borderRadius: '6px',
                          backgroundColor: isActive ? 'var(--primary-alpha)' : 'transparent',
                          cursor: 'pointer',
                          transition: 'background-color 0.2s'
                        }}
                        onClick={() => seekTo(entry.start)}
                      >
                        <div style={{
                          fontSize: '11px',
                          color: 'var(--primary)',
                          fontWeight: '600',
                          marginBottom: '4px'
                        }}>
                          {formatTime(entry.start)}
                        </div>
                        <div style={{ fontSize: '13px', lineHeight: '1.5' }}>
                          {entry.text}
                        </div>
                      </div>
                    )
                  })
                ) : (
                  <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '40px 20px' }}>
                    No transcript available for this video
                  </div>
                )}
              </div>
            </div>
          </>
        ) : null}
      </div>

      {/* Annotation Form Modal */}
      {showAnnotationForm && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 2000
          }}
          onClick={() => setShowAnnotationForm(false)}
        >
          <div
            style={{
              backgroundColor: 'var(--bg-primary)',
              padding: '24px',
              borderRadius: '12px',
              width: '90%',
              maxWidth: '500px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px' }}>
              {selectedText ? 'Annotate Transcript' : 'Add Timestamp Note'}
            </h3>

            {selectedText && (
              <div style={{
                padding: '12px',
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: '8px',
                marginBottom: '16px',
                fontSize: '13px',
                fontStyle: 'italic'
              }}>
                "{selectedText}"
              </div>
            )}

            <div style={{ marginBottom: '16px' }}>
              <label style={{ fontSize: '13px', fontWeight: '500', marginBottom: '8px', display: 'block' }}>
                Timestamp: {formatTime(currentTime)}
              </label>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ fontSize: '13px', fontWeight: '500', marginBottom: '8px', display: 'block' }}>
                Note (optional)
              </label>
              <textarea
                value={annotationNote}
                onChange={(e) => setAnnotationNote(e.target.value)}
                placeholder="Add a note about this moment..."
                style={{
                  width: '100%',
                  minHeight: '80px',
                  padding: '10px',
                  borderRadius: '6px',
                  border: '1px solid var(--border)',
                  backgroundColor: 'var(--bg-secondary)',
                  fontSize: '14px',
                  resize: 'vertical',
                  outline: 'none',
                  color: 'var(--text-primary)'
                }}
              />
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ fontSize: '13px', fontWeight: '500', marginBottom: '8px', display: 'block' }}>
                Color
              </label>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {ANNOTATION_COLORS.map(({ name, value }) => (
                  <button
                    key={value}
                    onClick={() => setAnnotationColor(value)}
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '50%',
                      backgroundColor: value,
                      border: annotationColor === value ? '3px solid var(--text-primary)' : '2px solid var(--border)',
                      cursor: 'pointer',
                      padding: 0
                    }}
                    title={name}
                  />
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setShowAnnotationForm(false)}
                style={{
                  padding: '10px 20px',
                  backgroundColor: 'var(--error)',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                Cancel
              </button>
              <button
                onClick={createAnnotation}
                style={{
                  padding: '10px 20px',
                  backgroundColor: 'var(--primary)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                Save Annotation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default YouTubeViewer
