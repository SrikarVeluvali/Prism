import { useState, useEffect, useMemo } from 'react';
import {
  FiPlus,
  FiEdit2,
  FiTrash2,
  FiX,
  FiStar,
  FiGrid,
  FiList,
  FiEye,
  FiSearch,
  FiFilter,
  FiTag,
  FiDownload,
  FiSave,
  FiArrowLeft,
} from 'react-icons/fi';
import { FaRobot } from 'react-icons/fa';
import axios from 'axios';
import NotificationModal from './NotificationModal';
import LoadingSpinner from './LoadingSpinner';
import { useNotification } from '../hooks/useNotification';
import RichTextEditor from './RichTextEditor';
import EnhancedDrawing from './EnhancedDrawing';
import MindMapViewer from './MindMapViewer';
import FlashcardsViewer from './FlashcardsViewer';
import QuizViewer from './QuizViewer';
import TimelineViewer from './TimelineViewer';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { saveAs } from 'file-saver';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
const API_URL = 'http://localhost:8000';

const NOTE_COLORS = [
  { value: '#ffffff', label: 'White' },
  { value: '#fef3c7', label: 'Amber' },
  { value: '#dbeafe', label: 'Blue' },
  { value: '#dcfce7', label: 'Green' },
  { value: '#fce7f3', label: 'Pink' },
  { value: '#f3e8ff', label: 'Purple' },
  { value: '#fed7aa', label: 'Orange' },
  { value: '#cffafe', label: 'Cyan' },
];

const AI_NOTE_TYPES = [
  { value: 'summary', label: 'Summary' },
  { value: 'key_points', label: 'Key Points' },
  { value: 'mind_map', label: 'Mind Map' },
  { value: 'flashcards', label: 'Flashcards' },
  { value: 'quiz', label: 'Quiz' },
  { value: 'timeline', label: 'Timeline' },
  { value: 'comparison_table', label: 'Comparison Table' },
];

function Notes({ documents, selectedDocIds, notebookId }) {
  // Core state
  const [notes, setNotes] = useState([]);
  const [viewMode, setViewMode] = useState('grid');
  const [isLoading, setIsLoading] = useState(false);

  // Editor state - full screen mode
  const [isEditing, setIsEditing] = useState(false);
  const [currentNote, setCurrentNote] = useState(null);
  const [noteTitle, setNoteTitle] = useState('');
  const [noteContent, setNoteContent] = useState('');
  const [noteType, setNoteType] = useState('rich_text');
  const [noteColor, setNoteColor] = useState('#ffffff');
  const [noteTags, setNoteTags] = useState([]);
  const [tagInput, setTagInput] = useState('');

  // Modal states
  const [showNamePrompt, setShowNamePrompt] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [viewingNote, setViewingNote] = useState(null);

  // AI generation state
  const [genTopic, setGenTopic] = useState('');
  const [genType, setGenType] = useState('summary');

  // Notification modal
  const {
    notification,
    closeNotification,
    showError,
    showSuccess,
    showWarning,
    showConfirm
  } = useNotification();

  // Search and filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterTags, setFilterTags] = useState([]);
  const [sortBy, setSortBy] = useState('date_desc');

  useEffect(() => {
    if (notebookId) {
      fetchNotes();
    }
  }, [notebookId]);

  const allTags = useMemo(() => {
    const tagSet = new Set();
    notes.forEach((note) => {
      if (note.tags) {
        note.tags.forEach((tag) => tagSet.add(tag));
      }
    });
    return Array.from(tagSet);
  }, [notes]);

  const filteredNotes = useMemo(() => {
    let filtered = notes;

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (note) =>
          note.title.toLowerCase().includes(query) ||
          note.content.toLowerCase().includes(query) ||
          (note.tags && note.tags.some((tag) => tag.toLowerCase().includes(query)))
      );
    }

    if (filterType !== 'all') {
      if (filterType === 'user') {
        filtered = filtered.filter((note) => !note.note_type.startsWith('ai_'));
      } else if (filterType === 'ai') {
        filtered = filtered.filter((note) => note.note_type.startsWith('ai_'));
      } else {
        filtered = filtered.filter((note) => note.note_type === filterType);
      }
    }

    if (filterTags.length > 0) {
      filtered = filtered.filter(
        (note) => note.tags && filterTags.every((tag) => note.tags.includes(tag))
      );
    }

    filtered = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'date_desc':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'date_asc':
          return new Date(a.created_at) - new Date(b.created_at);
        case 'title_asc':
          return a.title.localeCompare(b.title);
        case 'title_desc':
          return b.title.localeCompare(a.title);
        default:
          return 0;
      }
    });

    return filtered;
  }, [notes, searchQuery, filterType, filterTags, sortBy]);

  const fetchNotes = async () => {
    try {
      const response = await axios.get(`${API_URL}/notes/${notebookId}`);
      setNotes(response.data.notes);
    } catch (error) {
      console.error('Error fetching notes:', error);
    }
  };

  const openNamePrompt = () => {
    setNoteTitle('');
    setNoteType('rich_text');
    setShowNamePrompt(true);
  };

  const startNewNote = () => {
    if (!noteTitle.trim()) {
      showWarning('Validation Error', 'Please enter a note title');
      return;
    }

    setShowNamePrompt(false);
    setCurrentNote(null);
    setNoteContent('');
    setNoteColor('#ffffff');
    setNoteTags([]);
    setIsEditing(true);
  };

  const openEditorForNote = (note) => {
    setCurrentNote(note);
    setNoteTitle(note.title);
    setNoteContent(note.content);
    setNoteType(note.note_type);
    setNoteColor(note.color);
    setNoteTags(note.tags || []);
    setIsEditing(true);
  };

  const closeEditor = () => {
    setIsEditing(false);
    setCurrentNote(null);
    setNoteTitle('');
    setNoteContent('');
    setNoteType('rich_text');
    setNoteColor('#ffffff');
    setNoteTags([]);
    setTagInput('');
  };

  const saveNote = async () => {
    if (!noteTitle.trim()) {
      showWarning('Validation Error', 'Please enter a note title');
      return;
    }

    setIsLoading(true);
    try {
      if (currentNote) {
        await axios.put(`${API_URL}/notes/${currentNote.id}`, {
          title: noteTitle,
          content: noteContent,
          color: noteColor,
          tags: noteTags,
        });
      } else {
        await axios.post(`${API_URL}/notes`, {
          notebook_id: notebookId,
          title: noteTitle,
          content: noteContent,
          note_type: noteType,
          color: noteColor,
          tags: noteTags,
        });
      }

      await fetchNotes();
      closeEditor();
    } catch (error) {
      console.error('Error saving note:', error);
      showError('Error', 'Failed to save note. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const deleteNote = async (noteId) => {
    showConfirm(
      'Delete Note',
      'Are you sure you want to delete this note? This action cannot be undone.',
      async () => {
        try {
          await axios.delete(`${API_URL}/notes/${noteId}`);
          await fetchNotes();
          closeNotification();
          showSuccess('Success', 'Note deleted successfully!');
        } catch (error) {
          console.error('Error deleting note:', error);
          closeNotification();
          showError('Error', 'Failed to delete note. Please try again.');
        }
      }
    );
  };

  const generateAINotes = async () => {
    if (!genType) {
      showWarning('Validation Error', 'Please select a note type');
      return;
    }

    setIsLoading(true);
    try {
      await axios.post(`${API_URL}/notes/generate`, {
        notebook_id: notebookId,
        document_ids: selectedDocIds.length > 0 ? selectedDocIds : null,
        topic: genTopic.trim() || null,
        note_type: genType,
      });

      await fetchNotes();
      setShowGenerateModal(false);
      setGenTopic('');
      setGenType('summary');
    } catch (error) {
      console.error('Error generating notes:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Unknown error';
      showError('Error', `Failed to generate notes: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  const viewNote = (note) => {
    setViewingNote(note);
    setShowViewModal(true);
  };

  const closeViewModal = () => {
    setShowViewModal(false);
    setViewingNote(null);
  };

  const handleRichTextChange = (html) => {
    setNoteContent(html);
  };

  const handleDrawingChange = (dataUrl) => {
    setNoteContent(dataUrl);
  };

  const addTag = () => {
    const tag = tagInput.trim();
    if (tag && !noteTags.includes(tag)) {
      setNoteTags([...noteTags, tag]);
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove) => {
    setNoteTags(noteTags.filter((tag) => tag !== tagToRemove));
  };

  const toggleFilterTag = (tag) => {
    if (filterTags.includes(tag)) {
      setFilterTags(filterTags.filter((t) => t !== tag));
    } else {
      setFilterTags([...filterTags, tag]);
    }
  };

  const exportNoteToPDF = async (note) => {
    const pdf = new jsPDF();
    pdf.setFontSize(16);
    pdf.text(note.title, 10, 10);
    pdf.setFontSize(12);
    const splitContent = pdf.splitTextToSize(note.content.replace(/<[^>]*>/g, ''), 180);
    pdf.text(splitContent, 10, 20);
    pdf.save(`${note.title}.pdf`);
  };

  const exportNoteToMarkdown = (note) => {
    const markdown = `# ${note.title}\n\n${note.content.replace(/<[^>]*>/g, '')}`;
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
    saveAs(blob, `${note.title}.md`);
  };

  const renderNoteContent = (note, isPreview = true) => {
    const content = note.content;

    switch (note.note_type) {
      case 'ai_mindmap':
        return isPreview ? (
          <div className="note-preview">Mind Map (click to view)</div>
        ) : (
          <MindMapViewer content={content} />
        );

      case 'ai_flashcards':
        return isPreview ? (
          <div className="note-preview">Flashcards (click to view)</div>
        ) : (
          <FlashcardsViewer content={content} />
        );

      case 'ai_quiz':
        return isPreview ? (
          <div className="note-preview">Quiz (click to view)</div>
        ) : (
          <QuizViewer content={content} />
        );

      case 'ai_timeline':
        return isPreview ? (
          <div className="note-preview">Timeline (click to view)</div>
        ) : (
          <TimelineViewer content={content} />
        );

      case 'drawing':
        return <img src={content} alt="Drawing" className="note-drawing" />;

      case 'rich_text':
        return isPreview ? (
          <div
            className="note-preview"
            dangerouslySetInnerHTML={{
              __html: content.length > 200 ? content.substring(0, 200) + '...' : content,
            }}
          />
        ) : (
          <div className="note-rich-content">
            <ReactMarkdown rehypePlugins={[rehypeRaw]}>
              {content}
            </ReactMarkdown>
          </div>
        );

      case 'text':
      default:
        return isPreview ? (
          <div className="note-preview">
            {content.length > 200 ? content.substring(0, 200) + '...' : content}
          </div>
        ) : (
          <div className="note-rich-content">
            <ReactMarkdown rehypePlugins={[rehypeRaw]}>
              {content}
            </ReactMarkdown>
          </div>
        ); 
    }
  };

  const getNoteTypeIcon = (noteType) => {
    if (noteType.startsWith('ai_')) {
      return <FaRobot className="note-type-icon ai" />;
    }
    return null;
  };

  const getNoteTypeLabel = (noteType) => {
    const labels = {
      text: 'Text',
      rich_text: 'Rich Text',
      drawing: 'Drawing',
      ai_mindmap: 'Mind Map',
      ai_flashcards: 'Flashcards',
      ai_quiz: 'Quiz',
      ai_timeline: 'Timeline',
    };
    return labels[noteType] || noteType;
  };

  // Full-screen editor view
  if (isEditing) {
    return (
      <div className="notes-fullscreen-editor">
        {/* Top Bar */}
        <div className="editor-top-bar">
          <div className="editor-top-left">
            <button onClick={closeEditor} className="back-button">
              <FiArrowLeft /> Back to Notes
            </button>
            <input
              type="text"
              value={noteTitle}
              onChange={(e) => setNoteTitle(e.target.value)}
              placeholder="Note title..."
              className="editor-title-input"
            />
          </div>
          <div className="editor-top-right">
            <button onClick={saveNote} disabled={isLoading} className="save-button">
              <FiSave /> {isLoading ? 'Saving...' : 'Save Note'}
            </button>
          </div>
        </div>

        {/* Sidebar */}
        <div className="editor-layout">
          <div className="editor-sidebar">
            <div className="sidebar-section">
              <label>Note Type</label>
              {!currentNote && (
                <div className="type-buttons">
                  <button
                    onClick={() => setNoteType('rich_text')}
                    className={noteType === 'rich_text' ? 'type-btn active' : 'type-btn'}
                  >
                    Rich Text
                  </button>
                  <button
                    onClick={() => setNoteType('drawing')}
                    className={noteType === 'drawing' ? 'type-btn active' : 'type-btn'}
                  >
                    Drawing
                  </button>
                </div>
              )}
              {currentNote && <div className="type-display">{getNoteTypeLabel(noteType)}</div>}
            </div>

            <div className="sidebar-section">
              <label>Background Color</label>
              <div className="color-picker-grid">
                {NOTE_COLORS.map((c) => (
                  <button
                    key={c.value}
                    onClick={() => setNoteColor(c.value)}
                    className={`color-btn ${noteColor === c.value ? 'active' : ''}`}
                    style={{ backgroundColor: c.value }}
                    title={c.label}
                  />
                ))}
              </div>
            </div>

            <div className="sidebar-section">
              <label>Tags</label>
              <div className="tags-container">
                {noteTags.length!=0 ? noteTags.map((tag, idx) => (
                  <span key={idx} className="tag-item">
                    {tag}
                    <button onClick={() => removeTag(tag)} className="tag-remove-btn">
                      <FiX />
                    </button>
                  </span>
                )):`No Tags`}
              </div>
              <div className="tag-input-row">
                <input
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addTag();
                    }
                  }}
                  placeholder="Add tag..."
                  className="tag-input-field"
                />
                <button onClick={addTag} className="tag-add-btn">
                  Add
                </button>
              </div>
            </div>
          </div>

          {/* Main Editor Area */}
          <div className="editor-main" style={{ backgroundColor: noteColor }}>
            {noteType === 'rich_text' || currentNote?.note_type === 'rich_text' ? (
              <RichTextEditor content={noteContent} onChange={handleRichTextChange} />
            ) : noteType === 'drawing' || currentNote?.note_type === 'drawing' ? (
              <EnhancedDrawing initialData={noteContent} onChange={handleDrawingChange} />
            ) : (
              <textarea
                value={noteContent}
                onChange={(e) => setNoteContent(e.target.value)}
                placeholder="Start typing..."
                className="plain-textarea"
              />
            )}
          </div>
        </div>
      </div>
    );
  }

  // Normal notes list view
  return (
    <div className="notes-container">
      <div className="notes-header">
        <div className="notes-header-left">
          <h2>Notes</h2>
          <span className="notes-count">({filteredNotes.length})</span>
        </div>
        <div className="notes-header-right">
          <div className="notes-search">
            <FiSearch className="search-icon" />
            <input
              type="text"
              placeholder="Search notes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>

          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`icon-button ${showFilters ? 'active' : ''}`}
            title="Filters"
          >
            <FiFilter />
          </button>

          <div className="view-toggle">
            <button
              onClick={() => setViewMode('grid')}
              className={viewMode === 'grid' ? 'active' : ''}
              title="Grid View"
            >
              <FiGrid />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={viewMode === 'list' ? 'active' : ''}
              title="List View"
            >
              <FiList />
            </button>
          </div>

          <button onClick={openNamePrompt} className="action-button primary">
            <FiPlus /> New Note
          </button>
          <button onClick={() => setShowGenerateModal(true)} className="action-button ai-generate">
            <FaRobot /> AI Notes
          </button>
        </div>
      </div>

      {showFilters && (
        <div className="notes-filters">
          <div className="filter-group">
            <label>Type:</label>
            <select value={filterType} onChange={(e) => setFilterType(e.target.value)}>
              <option value="all">All Types</option>
              <option value="user">User Notes</option>
              <option value="ai">AI Notes</option>
              <option value="text">Text</option>
              <option value="rich_text">Rich Text</option>
              <option value="drawing">Drawing</option>
              <option value="ai_mindmap">Mind Map</option>
              <option value="ai_flashcards">Flashcards</option>
              <option value="ai_quiz">Quiz</option>
              <option value="ai_timeline">Timeline</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Sort:</label>
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="date_desc">Newest First</option>
              <option value="date_asc">Oldest First</option>
              <option value="title_asc">Title (A-Z)</option>
              <option value="title_desc">Title (Z-A)</option>
            </select>
          </div>

          {allTags.length > 0 && (
            <div className="filter-group">
              <label>Tags:</label>
              <div className="filter-tags">
                {allTags.map((tag) => (
                  <button
                    key={tag}
                    onClick={() => toggleFilterTag(tag)}
                    className={`tag-filter ${filterTags.includes(tag) ? 'active' : ''}`}
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>
          )}

          {filterTags.length > 0 && (
            <button onClick={() => setFilterTags([])} className="clear-filters">
              Clear Tag Filters
            </button>
          )}
        </div>
      )}

      <div className={`notes-${viewMode}`}>
        {filteredNotes.length === 0 ? (
          <div className="notes-empty">
            <p>No notes yet. Create your first note or generate AI notes from your documents!</p>
          </div>
        ) : (
          filteredNotes.map((note) => (
            <div
              key={note.id}
              className="note-card"
              style={{ backgroundColor: note.color }}
              onClick={() => viewNote(note)}
            >
              <div className="note-card-header">
                <h3>{note.title}</h3>
                <div className="note-card-actions">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      openEditorForNote(note);
                    }}
                    className="icon-button"
                    title="Edit"
                  >
                    <FiEdit2 />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteNote(note.id);
                    }}
                    className="icon-button"
                    title="Delete"
                  >
                    <FiTrash2 />
                  </button>
                </div>
              </div>

              <div className="note-card-content">{renderNoteContent(note, true)}</div>

              <div className="note-card-footer">
                <div className="note-type-badge">
                  {getNoteTypeIcon(note.note_type)}
                  {getNoteTypeLabel(note.note_type)}
                </div>
                {note.tags && note.tags.length > 0 && (
                  <div className="note-tags-preview">
                    {note.tags.slice(0, 2).map((tag, idx) => (
                      <span key={idx} className="note-tag-small">
                        {tag}
                      </span>
                    ))}
                    {note.tags.length > 2 && (
                      <span className="note-tag-more">+{note.tags.length - 2}</span>
                    )}
                  </div>
                )}
                <div className="note-date">{new Date(note.created_at).toLocaleDateString()}</div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Name Prompt Modal - Simple */}
      {showNamePrompt && (
        <div className="modal-overlay" onClick={() => setShowNamePrompt(false)}>
          <div className="modal name-prompt-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create New Note</h2>
              <button onClick={() => setShowNamePrompt(false)} className="icon-button">
                <FiX />
              </button>
            </div>
            <div className="modal-body">
              <label>Note Title</label>
              <input
                type="text"
                value={noteTitle}
                onChange={(e) => setNoteTitle(e.target.value)}
                placeholder="Enter note title..."
                className="form-input"
                autoFocus
                onKeyPress={(e) => {
                  if (e.key === 'Enter') startNewNote();
                }}
              />
              <div className="type-selector-inline">
                <label>Type:</label>
                <button
                  onClick={() => setNoteType('rich_text')}
                  className={noteType === 'rich_text' ? 'type-btn-inline active' : 'type-btn-inline'}
                >
                  Rich Text
                </button>
                <button
                  onClick={() => setNoteType('drawing')}
                  className={noteType === 'drawing' ? 'type-btn-inline active' : 'type-btn-inline'}
                >
                  Drawing
                </button>
              </div>
            </div>
            <div className="modal-footer">
              <button onClick={() => setShowNamePrompt(false)} className="action-button">
                Cancel
              </button>
              <button onClick={startNewNote} className="action-button primary">
                Continue
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Generate AI Notes Modal */}
      {showGenerateModal && (
        <div className="modal-overlay" onClick={() => setShowGenerateModal(false)}>
          <div className="modal generate-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Generate AI Notes</h2>
              <button onClick={() => setShowGenerateModal(false)} className="icon-button">
                <FiX />
              </button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label>Note Type</label>
                <select
                  value={genType}
                  onChange={(e) => setGenType(e.target.value)}
                  className="form-select"
                >
                  {AI_NOTE_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Topic (Optional)</label>
                <input
                  type="text"
                  value={genTopic}
                  onChange={(e) => setGenTopic(e.target.value)}
                  placeholder="e.g., Machine Learning Basics"
                  className="form-input"
                />
                <small>Leave empty to generate from all content</small>
              </div>

              <div className="ai-generate-info">
                <p>
                  AI will analyze your uploaded documents and generate {genType.replace('_', ' ')}{' '}
                  notes
                  {genTopic && ` focused on "${genTopic}"`}.
                </p>
              </div>
            </div>

            <div className="modal-footer">
              <button onClick={() => setShowGenerateModal(false)} className="action-button">
                Cancel
              </button>
              <button onClick={generateAINotes} disabled={isLoading} className="action-button primary">
                {isLoading ? 'Generating...' : 'Generate Notes'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* View Note Modal */}
      {showViewModal && viewingNote && (
        <div className="modal-overlay" onClick={closeViewModal}>
          <div
            className="modal note-view-modal"
            style={{ backgroundColor: viewingNote.color }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <div className="note-view-title">
                <h2>{viewingNote.title}</h2>
                <div className="note-type-badge">
                  {getNoteTypeIcon(viewingNote.note_type)}
                  {getNoteTypeLabel(viewingNote.note_type)}
                </div>
              </div>
              <div className="note-view-actions">
                <button
                  onClick={() => exportNoteToPDF(viewingNote)}
                  className="icon-button"
                  title="Export as PDF"
                >
                  <FiDownload />
                </button>
                <button
                  onClick={() => {
                    closeViewModal();
                    openEditorForNote(viewingNote);
                  }}
                  className="icon-button"
                  title="Edit"
                >
                  <FiEdit2 />
                </button>
                <button onClick={closeViewModal} className="icon-button">
                  <FiX />
                </button>
              </div>
            </div>

            <div className="modal-body note-view-body">
              {viewingNote.tags && viewingNote.tags.length > 0 && (
                <div className="note-view-tags">
                  {viewingNote.tags.map((tag, idx) => (
                    <span key={idx} className="note-tag">
                      <FiTag /> {tag}
                    </span>
                  ))}
                </div>
              )}

              <div className="note-view-content">{renderNoteContent(viewingNote, false)}</div>

              <div className="note-view-meta">
                <span>Created: {new Date(viewingNote.created_at).toLocaleString()}</span>
                <span>Updated: {new Date(viewingNote.updated_at).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-overlay-content">
            <LoadingSpinner size="large" text="Please wait..." />
          </div>
        </div>
      )}

      {/* Notification Modal */}
      <NotificationModal
        show={notification.show}
        type={notification.type}
        title={notification.title}
        message={notification.message}
        onClose={closeNotification}
        onConfirm={notification.onConfirm}
        confirmText={notification.confirmText}
        cancelText={notification.cancelText}
        okText={notification.okText}
      />
    </div>
  );
}

export default Notes;
