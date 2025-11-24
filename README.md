# PRISM

**AI-Powered Learning and Preparation Platform**

[![Live Demo](https://img.shields.io/badge/Demo-Live-brightgreen)](https://prism-teal-seven.vercel.app/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

PRISM is a comprehensive learning platform that leverages AI to transform how students study and prepare. Upload your study materials and unlock intelligent features like document Q&A, quiz generation, flashcards, virtual interviews, and more.

🌐 **Live Application**: [https://prism-learning.vercel.app/](https://prism-learning.vercel.app/)

## ✨ Features

### 📚 Document Management
- **Multi-format Support**: Upload PDFs, Word documents (.docx), text files, and YouTube videos
- **Smart Library**: Organize materials into notebooks with drag-and-drop interface
- **Progress Tracking**: Monitor reading progress and study time across all documents

### 🤖 AI-Powered Learning
- **RAG-based Q&A**: Ask questions about your documents and get contextual answers powered by semantic search
- **Interactive Chat**: Natural conversation with your study materials using Groq LLM
- **Smart Context**: AI retrieves relevant sections from your documents to provide accurate answers

### 📝 Assessment Tools
- **Quiz Generation**: Automatically create multiple-choice quizzes from your documents
- **Mock Tests**: Generate comprehensive practice tests with customizable difficulty
- **Performance Analytics**: Track scores, identify weak areas, and monitor improvement over time

### 📓 Note-Taking & Annotation
- **Rich Text Editor**: Full-featured editor with formatting, tables, images, and more (powered by TipTap)
- **PDF Annotation**: Highlight, comment, and annotate PDFs directly in the browser
- **Synchronized Storage**: All notes and annotations saved to the cloud

### 🎤 Virtual Interview Practice
- **AI Interviewer**: Practice technical and behavioral interviews with AI
- **Real-time Feedback**: Get instant feedback on your responses
- **Session History**: Review past interviews to track improvement

### 🎴 Interactive Learning
- **Doomscroll Mode**: Swipeable flashcards for bite-sized learning
- **Flashcard Viewer**: Study with AI-generated flashcards from your materials
- **Mind Maps**: Visualize concepts and connections with interactive diagrams
- **Timelines & Tables**: Auto-generated visual study aids

### 📊 Progress Dashboard
- **Performance Metrics**: Visualize quiz scores, study time, and document completion
- **Analytics**: Track your learning journey with detailed statistics
- **Goal Setting**: Monitor progress toward study goals

## 🏗️ Tech Stack

### Frontend
- **React 18** - Modern UI framework
- **Vite** - Fast build tool and dev server
- **TipTap** - Rich text editor framework
- **ReactFlow** - Interactive diagrams and mind maps
- **Axios** - HTTP client for API communication
- **React Icons** - Comprehensive icon library

### Backend
- **FastAPI** - High-performance Python web framework
- **Groq API** - Fast LLM inference for text generation
- **Pinecone** - Vector database for semantic search
- **MongoDB** - Document database for persistent storage
- **SentenceTransformers** - Local embedding generation
- **PyPDF2** - PDF text extraction
- **python-docx** - Word document processing
- **youtube-transcript-api** - YouTube video transcript extraction

### Authentication & Security
- **JWT Tokens** - Secure session management
- **Google OAuth** - Social login integration
- **Password Hashing** - bcrypt-based secure password storage

## 🚀 Getting Started

### Prerequisites
- **Node.js** 16+ and npm
- **Python** 3.8+
- **MongoDB** instance (local or cloud)
- **Pinecone** account and API key
- **Groq** API key

### Environment Setup

#### Backend Configuration
Create a `.env` file in the `backend/` directory:

```env
# API Keys
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key

# MongoDB Connection
MONGODB_URL=your_mongodb_connection_string

# JWT Secret
SECRET_KEY=your_secret_key_for_jwt

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your_google_client_id
```

#### Frontend Configuration
Update `frontend/src/config.js` with your backend URL:

```javascript
export const API_URL = 'http://localhost:8000'
```

### Installation

#### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

The backend server will start on `http://localhost:8000`

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

The frontend development server will start on `http://localhost:5173`

## 📖 Usage

1. **Sign Up / Login**: Create an account or sign in with Google
2. **Create a Notebook**: Organize your study materials by subject or topic
3. **Upload Documents**: Add PDFs, Word docs, text files, or YouTube videos
4. **Start Learning**:
   - **Chat Mode**: Ask questions about your documents
   - **Assessment Mode**: Generate and take quizzes or mock tests
   - **Notes Mode**: Take rich-text notes
   - **PDF Mode**: View and annotate PDFs
   - **Interview Mode**: Practice with the AI interviewer
   - **Doomscroll Mode**: Study with swipeable flashcards
   - **Progress Mode**: Track your learning metrics

## 🎯 Key Workflows

### Document Q&A (RAG)
1. Upload study materials to a notebook
2. Select documents to query
3. Ask natural language questions
4. Get AI-generated answers with source context

### Quiz Generation
1. Select a document from your library
2. Choose "Assessment" mode and click "Quiz"
3. AI generates multiple-choice questions
4. Take the quiz and get instant results
5. Review explanations for each question

### Note-Taking
1. Switch to "Notes" mode
2. Create or select a note
3. Use the rich text editor with formatting tools
4. Notes auto-save to the cloud

## 📁 Project Structure

```
Prism/
├── backend/
│   ├── main.py              # FastAPI application and routes
│   ├── auth.py              # Authentication logic
│   ├── database.py          # MongoDB collections and queries
│   ├── processors.py        # Document processing utilities
│   ├── requirements.txt     # Python dependencies
│   └── run.py              # Server startup script
│
└── frontend/
    ├── src/
    │   ├── components/      # React components
    │   ├── contexts/        # React context providers
    │   ├── hooks/          # Custom React hooks
    │   ├── App.jsx         # Main application component
    │   ├── config.js       # Configuration
    │   └── main.jsx        # Application entry point
    │
    ├── package.json        # Node dependencies
    └── vite.config.js      # Vite configuration
```

## 🔧 API Endpoints

### Authentication
- `POST /register` - Create new user account
- `POST /login` - User login with credentials
- `POST /google-auth` - Google OAuth login

### Documents
- `POST /upload` - Upload a document
- `GET /documents` - List all documents in a notebook
- `DELETE /documents/{doc_id}` - Delete a document

### Chat & RAG
- `POST /query` - Ask a question about documents
- `GET /chat-history/{notebook_id}` - Retrieve chat history

### Assessments
- `POST /quiz` - Generate a quiz
- `POST /mocktest` - Generate a mock test
- `POST /quiz-results` - Save quiz results
- `GET /quiz-results/{user_id}` - Get user quiz results

### Notes & Annotations
- `POST /notes` - Create or update a note
- `GET /notes/{notebook_id}` - Get all notes
- `POST /annotations` - Save PDF annotations

### Interview & Learning
- `POST /interview` - Virtual interview session
- `POST /doomscroll` - Generate flashcards
- `GET /progress/{user_id}` - Get learning progress

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ for people who want to learn**
