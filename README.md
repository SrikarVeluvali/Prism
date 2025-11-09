# PRISM

> An AI-powered learning and preparation platform that transforms documents into interactive study materials

PRISM is a comprehensive educational platform that combines Retrieval-Augmented Generation (RAG) with intelligent learning tools to help students and professionals prepare effectively for exams and interviews.

## 🚀 Quick Stats

- **8 Document Formats**: PDF, DOCX, DOC, TXT, MD, RTF, YouTube, Images
- **7 Note Types**: Rich Text, Drawing, Mind Maps, Flashcards, Quiz, Timeline, Comparison
- **3 Assessment Modes**: Quizzes (MCQ), Mock Tests (Theory/Coding/Reorder), Virtual Interviews
- **40+ API Endpoints**: Full REST API with JWT authentication
- **14 Database Collections**: MongoDB with TTL indexing for caching
- **Real-Time AI Analysis**: Server-Sent Events for live PDF processing
- **Smart Caching**: 30-day cache for cost-effective repeated analyses

## Features

### 🔐 Authentication & User Management
- **Email/Password Authentication** - Secure local account creation and login
- **Google OAuth 2.0** - Quick sign-in with your Google account
- **JWT Token Security** - 7-day session tokens with automatic refresh
- **User Dashboard** - Personalized workspace with notebook organization

### 📚 Document Management
- **Multi-Format Support** - Upload PDFs, Word documents (.docx, .doc), text files (.txt, .md, .rtf), and YouTube videos
- **Notebook Organization** - Create unlimited notebooks with custom colors and icons (12 preset options each)
- **Batch Upload** - Upload multiple documents at once with drag-and-drop support
- **Smart Processing** - Automatic text extraction, metadata parsing, and vector embedding generation
- **Document Viewers** - Specialized viewers for each file type with full feature support

### 🤖 AI-Powered Q&A System
- **RAG Architecture** - Context-aware answers using Retrieval-Augmented Generation
- **Semantic Search** - Advanced vector search using Pinecone for finding relevant information
- **Multi-Document Queries** - Ask questions across multiple documents simultaneously
- **Source Citations** - Every answer includes references to source documents and pages
- **Chat History** - Persistent conversation history for each notebook
- **Context-Aware Responses** - AI remembers previous questions in the conversation

### 🎯 Smart PDF Analysis (NEW!)
- **Auto-Highlight Mode** - AI automatically identifies and highlights key concepts in your PDFs
- **Custom Analysis** - Define your own criteria for what to highlight (e.g., "highlight all formulas")
- **Question Generation** - Automatically generate study questions organized by mark type:
  - 2-mark questions for quick recall
  - 5-mark questions for detailed explanations
  - 10-mark questions for comprehensive understanding
- **Topic Organization** - AI groups highlights and questions by topic
- **Real-Time Processing** - Live progress updates as pages are analyzed
- **Selective Save** - Choose which highlights and questions to keep
- **Page Navigation** - Jump directly to any highlighted section or question source

### 🖍️ PDF Annotations & Interaction
- **Manual Highlighting** - Select and highlight text with 8 color options
- **Annotation Notes** - Add personal notes to any highlight
- **AI Query on Highlights** - Ask questions about highlighted text for instant explanations
- **Persistent Annotations** - All highlights and notes are saved and synced
- **Full PDF Viewer** - Zoom, navigate pages, and view documents with annotations overlay

### 📝 Assessment & Testing
- **AI Quiz Generation** - Generate multiple-choice quizzes with customizable:
  - Question count (1-50 questions)
  - Difficulty levels (easy, medium, hard)
  - Document selection (specific files or entire notebook)
- **Comprehensive Mock Tests** - Three question types:
  - **Theory Questions** - Long-form answers with AI evaluation
  - **Coding Questions** - Programming challenges with multi-language support (Python, Java, C++, JavaScript, Go, Rust, etc.)
  - **Reorder Questions** - Drag-and-drop sequence arrangement
- **Instant Feedback** - Detailed explanations for every question
- **Performance Analytics** - Track scores, identify weak areas, view history
- **Retry Capability** - Retake quizzes to improve understanding

### 📓 Advanced Note-Taking
- **7 Note Types**:
  - **Rich Text Notes** - Full WYSIWYG editor with TipTap
  - **Drawing Notes** - Canvas-based sketching and diagrams
  - **Mind Maps** - Interactive visual concept mapping with ReactFlow
  - **Flashcards** - Flip-card format for active recall
  - **Quiz Notes** - Embedded quiz format for self-testing
  - **Timeline Notes** - Chronological event visualization
  - **Comparison Tables** - Structured side-by-side comparisons
- **AI Note Generation** - Auto-generate 7 types of notes from your documents:
  - Summaries, Key Points, Mind Maps, Flashcards, Quizzes, Timelines, Comparison Tables
- **Organization Features**:
  - 8 color themes for visual categorization
  - Tag system for flexible organization
  - Search and filter capabilities
  - Sort by date, title, or type
- **Export to PDF** - Save notes as PDF documents
- **Auto-Save** - Never lose your work with automatic saving

### 🎤 Virtual Interview Practice
- **Interview Types** - Technical, behavioral, or mixed interviews
- **Difficulty Levels** - Easy, medium, and hard questions
- **Customizable Duration** - 5 to 60 minute sessions
- **Speech Recognition** - Answer questions using your voice (optional)
- **Text-to-Speech** - Hear questions read aloud (optional)
- **Dynamic Questions** - AI generates contextual follow-up questions based on your answers
- **Comprehensive Evaluation** - Detailed scoring (0-100) with:
  - Performance feedback
  - Strengths and weaknesses analysis
  - Improvement recommendations
- **Session History** - Review past interview sessions and track progress

### 📜 Doomscroll Learning Cards
- **8 Card Types** - Fun Facts, Mnemonics, Key Concepts, Quotes, Summaries, Tips, Questions, Definitions
- **Infinite Feed** - Endless AI-generated bite-sized learning content
- **Visual Themes** - 8 themed color schemes for engaging design
- **Save & Organize** - Like cards and organize them into custom folders
- **Gallery View** - Browse your collection of saved cards
- **Auto-Generation** - New cards continuously generated from your documents
- **Casual Learning** - Perfect for quick study sessions or breaks

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework for building async APIs
- **Groq API** - High-performance LLM (llama-3.3-70b-versatile) for text generation and Q&A
- **Pinecone** - Serverless vector database for semantic search and similarity matching
- **MongoDB** - NoSQL database for persistent storage with TTL indexes
- **Motor** - Async MongoDB driver for FastAPI
- **SentenceTransformers** - Local embedding generation (all-MiniLM-L6-v2, 384 dimensions)
- **PyPDF2** - PDF text extraction and processing
- **python-docx** - Word document (.docx) processing
- **textract** - Multi-format document extraction
- **youtube-transcript-api** - YouTube transcript extraction
- **yt-dlp** - YouTube metadata extraction
- **python-jose** - JWT token encoding/decoding
- **passlib** - Password hashing with bcrypt
- **google-auth** - Google OAuth 2.0 integration

### Frontend
- **React 18** - UI library with hooks and functional components
- **Vite** - Next-generation frontend build tool with HMR
- **TipTap** - Extensible rich text editor for notes
- **React PDF** - PDF.js wrapper for PDF viewing and rendering
- **ReactFlow** - Interactive node-based diagrams and mind maps
- **Axios** - Promise-based HTTP client for API communication
- **React Icons** - Icon library (Feather Icons)
- **React Dropzone** - Drag-and-drop file upload interface
- **React Markdown** - Markdown rendering with rehype support
- **html2canvas** - HTML to canvas conversion for exports
- **jsPDF** - Client-side PDF generation

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - Backend runtime
- **Node.js 16+** - Frontend runtime
- **MongoDB** - Database (local or MongoDB Atlas)
- **Git** - Version control

You'll also need API keys for:
- **Groq API** - Get it from [Groq Console](https://console.groq.com/keys)
- **Pinecone** - Sign up at [Pinecone](https://www.pinecone.io/)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/PRISM.git
cd PRISM
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment (recommended)
# On Windows:
python -m venv venv
venv\Scripts\activate

# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Edit the `.env` file and add your API keys:

```env
# Required - AI Services
GROQ_API_KEY=your_groq_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1

# Optional - Database
MONGODB_URL=mongodb://localhost:27017

# Required - Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Optional - Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install
```

## Running the Application

You'll need to run both the backend and frontend servers.

### Start the Backend Server

```bash
# From the backend directory with venv activated
cd backend
python main.py
```

The backend will start on **http://localhost:8000**

You can verify it's running by visiting:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/

### Start the Frontend Server

```bash
# From the frontend directory (in a new terminal)
cd frontend
npm run dev
```

The frontend will start on **http://localhost:3000**

## Usage Guide

### 1. Sign Up / Login
- **Create Account**: Click "Sign Up" and register with email/password
- **Google Sign-In**: Use "Sign in with Google" for quick access
- Your account securely stores all notebooks, documents, and progress

### 2. Create a Notebook
- Click "Create Notebook" in your library
- Choose from 12 colors (Indigo, Purple, Pink, Amber, Emerald, etc.)
- Select from 12 icons (📚, 📖, 📝, 🎓, 💡, 🚀, etc.)
- Organize by subject, course, or topic

### 3. Upload Documents
- Select your notebook from the library
- Click "Upload Documents" or drag-and-drop files
- **Supported formats**: PDF, DOCX, DOC, TXT, MD, RTF, YouTube URLs
- AI automatically extracts text and generates embeddings
- Track upload progress for each file

### 4. Analyze PDFs with AI (NEW!)
- Open any PDF document
- Click the "Analyze" button
- **Choose mode**:
  - **Auto Highlight**: AI finds and highlights key concepts
  - **Custom Prompt**: Define what to highlight (e.g., "highlight all dates and events")
- **Generate Questions**: Create 2-mark, 5-mark, and 10-mark study questions
- View real-time progress as pages are processed
- Review highlights organized by topic
- Select which highlights/questions to save
- Navigate directly to highlighted sections in PDF

### 5. Annotate PDFs Manually
- Select text in any PDF to highlight
- Choose from 8 colors for your highlights
- Add personal notes to each highlight
- **AI Query**: Right-click any highlight and ask questions about it
- All annotations are saved and synced automatically

### 6. Ask Questions (RAG Chat)
- Type questions in the chat interface
- AI searches across all documents in your notebook
- Get contextual answers with source citations (document name, page number)
- Ask follow-up questions - AI remembers the conversation
- **Pro tip**: Select specific documents to narrow the search scope

### 7. Take Quizzes
- Navigate to "Assessment" → "Quiz"
- Configure:
  - Number of questions (1-50)
  - Difficulty (easy, medium, hard)
  - Source documents (all or specific files)
- Take the quiz with instant answer checking
- View detailed explanations for each question
- Track your performance over time
- Retry quizzes to improve scores

### 8. Take Mock Tests
- Navigate to "Assessment" → "Mock Test"
- Customize question distribution:
  - **Theory Questions**: Long-form answers evaluated by AI
  - **Coding Questions**: Programming challenges (choose your language: Python, Java, C++, JavaScript, etc.)
  - **Reorder Questions**: Drag-and-drop to arrange steps in correct order
- Submit test for comprehensive AI evaluation
- Review detailed feedback and scoring

### 9. Create and Generate Notes
- Go to "Notes" section
- **Create manually** with 7 note types:
  - Rich Text, Drawing, Mind Map, Flashcards, Quiz, Timeline, Comparison Table
- **Generate with AI**:
  - Click "Generate Notes" button
  - Select documents and note type
  - AI creates structured notes automatically
- Organize with colors, tags, and search
- Export notes to PDF

### 10. Practice Virtual Interviews
- Enter "Interview" mode
- Configure:
  - Interview type (technical, behavioral, mixed)
  - Difficulty level
  - Duration (5-60 minutes)
- **Answer using voice** (speech recognition) or text
- Receive follow-up questions based on your responses
- Get comprehensive evaluation with:
  - Score (0-100)
  - Strengths and weaknesses
  - Improvement recommendations
- Review past interview sessions

### 11. Doomscroll Learning
- Navigate to "Doomscroll" mode
- Scroll through infinite AI-generated learning cards:
  - Fun Facts, Mnemonics, Key Concepts, Quotes, Summaries, Tips, Questions, Definitions
- **Save cards** you want to review later
- **Organize into folders** for different topics
- Browse saved cards in gallery view
- Perfect for casual learning during breaks

## Project Structure

```
PRISM/
├── backend/                     # Python FastAPI backend
│   ├── main.py                  # Main application and API endpoints (~2400 lines)
│   ├── auth.py                  # JWT authentication and Google OAuth
│   ├── database.py              # MongoDB configuration and collections
│   ├── processors/              # Document processors
│   │   ├── pdf_processor.py     # PDF text extraction
│   │   ├── word_processor.py    # Word document processing
│   │   ├── text_processor.py    # Text file processing
│   │   └── youtube_processor.py # YouTube transcript extraction
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment variables template
│   ├── .env                     # Your environment variables (gitignored)
│   ├── uploads/                 # Document file storage
│   └── run.py                   # Development server launcher
│
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── Auth.jsx         # Authentication UI
│   │   │   ├── Library.jsx      # Notebook library
│   │   │   ├── FileUploadModal.jsx
│   │   │   ├── DocumentViewer.jsx
│   │   │   ├── PDFAnnotator.jsx
│   │   │   ├── PDFAnalyzer.jsx  # NEW: AI-powered PDF analysis
│   │   │   ├── StudyQuestions.jsx  # NEW: Question management
│   │   │   ├── Quiz.jsx
│   │   │   ├── MockTest.jsx
│   │   │   ├── Notes.jsx
│   │   │   ├── RichTextEditor.jsx
│   │   │   ├── VirtualInterview.jsx
│   │   │   ├── Doomscroll.jsx
│   │   │   ├── FlashcardsViewer.jsx
│   │   │   ├── MindMapViewer.jsx
│   │   │   ├── TimelineViewer.jsx
│   │   │   └── ...
│   │   ├── contexts/
│   │   │   ├── AuthContext.jsx      # Authentication state
│   │   │   └── NotebookContext.jsx  # Notebook selection state
│   │   ├── App.jsx              # Main app component
│   │   ├── main.jsx             # React entry point
│   │   ├── index.css            # Global styles
│   │   └── library-styles.css   # Library-specific styles
│   ├── public/                  # Static assets
│   ├── package.json             # Frontend dependencies
│   └── vite.config.js           # Vite configuration
│
├── .gitignore                   # Git ignore rules
├── CLAUDE.md                    # Claude Code development guide
└── README.md                    # This file
```

## API Documentation

Once the backend is running, visit **http://localhost:8000/docs** for interactive API documentation (Swagger UI).

### Key Endpoints

#### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login with email/password
- `POST /auth/google` - Login/register with Google OAuth
- `GET /auth/me` - Get current user profile (protected)

#### Notebooks
- `POST /notebooks` - Create a new notebook (protected)
- `GET /notebooks` - List all user notebooks (protected)
- `GET /notebooks/{notebook_id}` - Get a specific notebook (protected)
- `PUT /notebooks/{notebook_id}` - Update a notebook (protected)
- `DELETE /notebooks/{notebook_id}` - Delete a notebook and all its data (protected)

#### Documents
- `POST /upload-pdfs/{notebook_id}` - Upload documents (PDF, DOCX, TXT, etc.) (protected)
- `GET /documents/{notebook_id}` - List documents in a notebook (protected)
- `DELETE /documents/{doc_id}` - Delete a document (protected)
- `GET /documents/{notebook_id}/{doc_id}/pdf` - Download/view document (protected)

#### PDF Analysis (NEW!)
- `GET /analyze-pdf/{document_id}` - Analyze PDF with AI (SSE stream) (protected)
- `POST /save-analysis` - Save analysis results (highlights/questions) (protected)
- `GET /pdf-questions/{document_id}` - Get saved questions for a PDF (protected)

#### Annotations
- `POST /annotations` - Create a new annotation (protected)
- `GET /annotations/{notebook_id}` - Get all annotations for a notebook (protected)
- `GET /annotations/document/{document_id}` - Get annotations for a document (protected)
- `DELETE /annotations/{annotation_id}` - Delete an annotation (protected)
- `POST /annotations/query` - Ask AI about a highlighted section (protected)

#### Q&A (RAG Chat)
- `POST /ask` - Ask a question about documents (protected)
- `GET /chat-history/{notebook_id}` - Get chat history (protected)
- `POST /chat-history` - Save chat messages (protected)
- `DELETE /chat-history/{notebook_id}` - Clear chat history (protected)

#### Quizzes & Assessments
- `POST /generate-quiz` - Generate a multiple-choice quiz (protected)
- `POST /submit-quiz` - Submit quiz answers for evaluation (protected)
- `POST /generate-mock-test` - Generate a mock test (theory/coding/reorder) (protected)
- `POST /submit-mock-test` - Submit mock test for AI evaluation (protected)
- `GET /quiz-results/{notebook_id}` - Get quiz history and scores (protected)

#### Notes
- `GET /notes/{notebook_id}` - Get all notes in a notebook (protected)
- `POST /notes` - Create a new note (protected)
- `PUT /notes/{note_id}` - Update a note (protected)
- `DELETE /notes/{note_id}` - Delete a note (protected)
- `POST /generate-note` - AI-generate a note from documents (protected)

#### Virtual Interview
- `POST /interview/start` - Start an interview session (protected)
- `POST /interview/answer` - Submit an answer and get next question (protected)
- `POST /interview/end` - End interview and get evaluation (protected)
- `GET /interview/sessions/{notebook_id}` - Get interview history (protected)

#### Doomscroll
- `POST /generate-doomscroll-cards` - Generate learning cards (protected)
- `POST /saved-cards` - Save a card to collection (protected)
- `GET /saved-cards/{notebook_id}` - Get saved cards (protected)
- `DELETE /saved-cards/{card_id}` - Delete a saved card (protected)
- `POST /doomscroll-folders` - Create a folder (protected)
- `GET /doomscroll-folders/{notebook_id}` - Get folders (protected)
- `PUT /saved-cards/{card_id}/folder` - Move card to folder (protected)

## How It Works

### Authentication Flow

1. **Registration/Login**
   - User registers with email/password or signs in with Google OAuth
   - Password hashed with bcrypt (local auth) or Google token verified (OAuth)
   - JWT token generated with 7-day expiration
   - Token stored in localStorage and sent in Authorization header for all requests

2. **Protected Routes**
   - All API endpoints (except auth endpoints) require valid JWT token
   - Token verified on each request via `get_current_user` dependency
   - Invalid/expired tokens return 401 Unauthorized

### Document Processing Pipeline

1. **Multi-Format Upload**
   - Documents uploaded to `uploads/` directory
   - File type detected based on extension
   - Appropriate processor selected (PDF, Word, Text, YouTube)
   - Text extracted with metadata (title, author, page count, etc.)

2. **Text Chunking**
   - Extracted text split into chunks (1000 characters with 200 overlap)
   - Overlap ensures context isn't lost between chunks
   - Each chunk tagged with document ID, page number, and chunk index

3. **Vector Embedding**
   - Each chunk converted to 384-dimensional vector (all-MiniLM-L6-v2)
   - Embeddings uploaded to Pinecone in batches for efficiency
   - Metadata stored: notebook_id, doc_id, filename, page, chunk_index

### RAG (Retrieval-Augmented Generation)

1. **Query Processing**
   - User question converted to embedding using same model
   - Pinecone similarity search finds top 5 most relevant chunks
   - Cosine similarity metric ranks results

2. **Context Assembly**
   - Retrieved chunks combined with metadata
   - Source citations prepared (filename, page numbers)
   - Context formatted for LLM prompt

3. **Answer Generation**
   - Context + question sent to Groq LLM (llama-3.3-70b-versatile)
   - LLM generates answer based only on provided context
   - Response includes inline source citations
   - Answer returned with conversation context

### AI PDF Analysis

1. **Page-by-Page Processing**
   - PDF analyzed page-by-page with real-time progress (SSE)
   - Each page sent to LLM with analysis prompt
   - Auto-highlight mode: AI identifies key concepts
   - Custom prompt mode: User defines analysis criteria

2. **Question Generation**
   - LLM generates 2-mark, 5-mark, and 10-mark questions per page
   - Questions organized by topic and mark type
   - Includes answers with page references
   - Results cached for 30 days to reduce costs

3. **Caching System**
   - Analysis results cached in MongoDB with TTL index (30 days)
   - Cache key: document_id + page_number + custom_prompt_hash
   - Subsequent analyses use cached results if available
   - Significant cost savings for repeated analyses

### Quiz & Assessment Generation

1. **Content Retrieval**
   - Relevant chunks retrieved from Pinecone based on document selection
   - Multiple documents can be combined for comprehensive quizzes

2. **Question Generation**
   - **Quizzes**: MCQs with 4 options, correct answer, explanation
   - **Mock Tests**: Theory (long-form), Coding (with templates), Reorder (sequence)
   - Difficulty level affects complexity of questions
   - LLM generates JSON-formatted questions

3. **Evaluation**
   - **MCQs**: Automatic scoring with instant feedback
   - **Theory**: AI evaluates answers against model answers
   - **Coding**: AI checks logic, correctness, and approach
   - **Reorder**: Automatic sequence comparison
   - Results saved to MongoDB for performance tracking

### Virtual Interview System

1. **Question Generation**
   - AI generates contextual questions based on interview type and difficulty
   - Questions derived from user's uploaded documents
   - Follow-up questions adapt to previous answers

2. **Real-Time Interaction**
   - Speech recognition converts voice to text (Web Speech API)
   - Text-to-speech reads questions aloud (optional)
   - Answers sent to backend for processing

3. **Evaluation**
   - AI analyzes all answers comprehensively
   - Generates score (0-100) with detailed feedback
   - Identifies strengths, weaknesses, and improvement areas
   - Session saved to MongoDB for review

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GROQ_API_KEY` | Groq API key for LLM inference | Yes | - |
| `PINECONE_API_KEY` | Pinecone API key for vector database | Yes | - |
| `PINECONE_ENVIRONMENT` | Pinecone region (e.g., us-east-1) | Yes | us-east-1 |
| `PINECONE_INDEX_NAME` | Name for Pinecone index | No | pdf-rag-index |
| `MONGODB_URL` | MongoDB connection string | No | mongodb://localhost:27017 |
| `JWT_SECRET_KEY` | Secret key for JWT token signing | Yes | your-secret-key-change-this-in-production |
| `GOOGLE_CLIENT_ID` | Google OAuth 2.0 client ID | No (for OAuth) | - |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 2.0 client secret | No (for OAuth) | - |

**Important Notes:**
- **JWT_SECRET_KEY**: Change this in production! Use a strong, random string.
- **Google OAuth**: Only required if you want to enable Google Sign-In.
- **MONGODB_URL**: Can use MongoDB Atlas connection string for cloud database.

## Troubleshooting

### Backend Issues

**Import errors**
```bash
# Ensure virtual environment is activated and dependencies installed
pip install -r requirements.txt
```

**API key errors**
- Verify your `.env` file has correct API keys
- Check that `.env` is in the `backend/` directory
- Ensure `JWT_SECRET_KEY` is set (required for authentication)

**Pinecone connection errors**
- Ensure your Pinecone environment matches your account region
- Wait ~1 minute after first run for index creation
- Check Pinecone dashboard for index status

**MongoDB connection errors**
- Ensure MongoDB is running locally: `mongod` or check system services
- For MongoDB Atlas, verify connection string includes username and password
- Test connection: `mongosh "mongodb://localhost:27017"`
- Database indexes are created automatically on startup

**Authentication errors**
- **401 Unauthorized**: JWT token expired or invalid (re-login required)
- **Google OAuth fails**: Verify `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct
- **Token not persisting**: Check browser localStorage for token storage

**PDF Analysis issues**
- Analysis may be slow for large PDFs (page-by-page processing)
- Check Groq API rate limits if analysis fails
- Cached results used automatically for repeated analyses

### Frontend Issues

**Port already in use**
- Change the port in `vite.config.js` (default: 3000)
- Or kill the process using the port

**CORS errors**
- Ensure backend is running on `http://localhost:8000`
- Check CORS configuration in `backend/main.py`
- Verify frontend is making requests to correct backend URL

**Dependencies errors**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**PDF viewing issues**
- Ensure PDF.js worker is loaded correctly
- Check browser console for errors
- Some PDFs with complex formatting may not render perfectly

**Speech recognition not working** (Virtual Interview)
- Speech recognition only works in Chrome/Edge
- Requires HTTPS or localhost
- Check microphone permissions in browser

## Development

### Running in Development Mode

Both frontend and backend support hot reloading for development:

```bash
# Backend (auto-reloads on file changes)
cd backend
uvicorn main:app --reload

# Frontend (Vite dev server)
cd frontend
npm run dev
```

### Building for Production

```bash
# Frontend build
cd frontend
npm run build
```

## What Makes PRISM Unique?

### 🎯 Comprehensive Learning Ecosystem
Unlike simple PDF readers or basic quiz generators, PRISM provides an **end-to-end learning platform** that combines document management, AI analysis, assessments, and innovative learning tools in one place.

### 🤖 Advanced AI Features
- **Smart PDF Analysis**: AI automatically highlights important concepts and generates study questions by mark type (2/5/10 marks)
- **RAG-Powered Q&A**: Context-aware answers with source citations using retrieval-augmented generation
- **Multi-Format Support**: Process PDFs, Word docs, text files, and even YouTube videos
- **30-Day Caching**: Intelligent caching reduces API costs and speeds up repeated analyses

### 📚 Diverse Learning Modes
- **7 Note Types**: From rich text to mind maps, timelines, and comparison tables
- **3 Assessment Types**: MCQ quizzes, comprehensive mock tests (theory/coding/reorder), and virtual interviews
- **8 Doomscroll Cards**: Bite-sized learning content for casual study sessions
- **Speech-Enabled Interviews**: Practice with voice recognition and text-to-speech

### 🔒 Secure & Personalized
- **User Authentication**: Local accounts and Google OAuth support
- **Personal Workspaces**: Each user has isolated notebooks and documents
- **JWT Security**: 7-day tokens with automatic session management
- **Performance Tracking**: Monitor progress across quizzes, tests, and interviews

### 💡 Smart Organization
- **12 Colors + 12 Icons**: Visually organize notebooks by subject
- **Tag System**: Flexible categorization for notes and documents
- **Folder Organization**: Custom folders for saved learning cards
- **Search & Filter**: Quickly find any content across the platform

### ⚡ Modern Tech Stack
- **Async Architecture**: FastAPI with Motor for non-blocking database operations
- **Real-Time Updates**: Server-Sent Events (SSE) for live analysis progress
- **Vector Search**: Pinecone for semantic similarity matching
- **Groq LLM**: Fast inference with llama-3.3-70b-versatile

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

### Core Technologies
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern async Python web framework
- **[Groq](https://groq.com/)** - Lightning-fast LLM inference (llama-3.3-70b-versatile)
- **[Pinecone](https://www.pinecone.io/)** - Serverless vector database for semantic search
- **[MongoDB](https://www.mongodb.com/)** - NoSQL database with Motor async driver
- **[React](https://react.dev/)** - UI library with hooks and modern patterns
- **[Vite](https://vitejs.dev/)** - Next-generation frontend build tool

### AI/ML Libraries
- **[SentenceTransformers](https://www.sbert.net/)** - State-of-the-art text embeddings
- **[PyPDF2](https://pypdf2.readthedocs.io/)** - PDF processing and text extraction
- **[python-docx](https://python-docx.readthedocs.io/)** - Word document processing
- **[youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)** - YouTube transcript extraction

### Frontend Libraries
- **[TipTap](https://tiptap.dev/)** - Extensible rich text editor
- **[React PDF](https://react-pdf.org/)** - PDF.js integration for React
- **[ReactFlow](https://reactflow.dev/)** - Interactive node-based diagrams
- **[React Icons](https://react-icons.github.io/react-icons/)** - Icon library

### Authentication & Security
- **[python-jose](https://python-jose.readthedocs.io/)** - JWT token handling
- **[passlib](https://passlib.readthedocs.io/)** - Password hashing with bcrypt
- **[google-auth](https://google-auth.readthedocs.io/)** - Google OAuth 2.0 integration

### Special Thanks
- UI/UX inspired by modern learning platforms and productivity tools
- Community contributors and open-source maintainers

## Contact

For questions or feedback, please open an issue on GitHub.

---

Made with ❤️ for better learning
