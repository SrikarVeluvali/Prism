# PRISM

> An AI-powered learning and preparation platform that transforms PDFs into interactive study materials

PRISM is a comprehensive educational platform that combines Retrieval-Augmented Generation (RAG) with intelligent learning tools to help students and professionals prepare effectively for exams and interviews.


## Features

### Core Features
- **📚 Notebook Organization** - Create multiple notebooks to organize your study materials by subject or topic
- **📄 PDF Document Management** - Upload and manage multiple PDF documents per notebook
- **🤖 AI-Powered Q&A** - Ask questions about your documents and get accurate answers with source citations
- **🔍 Semantic Search** - Advanced vector search using Pinecone for finding relevant information

### Assessment & Testing
- **📝 Quiz Generation** - Automatically generate multiple-choice quizzes from your documents
- **🎯 Mock Tests** - Create comprehensive mock tests with theory, coding, and reordering questions
- **📊 Performance Tracking** - Track quiz and test scores over time
- **💯 Instant Evaluation** - Get immediate feedback on your answers

### Note-Taking & Annotation
- **✍️ Rich Text Notes** - Create notes with a powerful TipTap editor
- **🖍️ PDF Annotations** - Highlight and annotate PDFs directly in the browser
- **🎨 Drawing Tools** - Create visual diagrams and sketches
- **🧠 AI-Generated Notes** - Generate summaries, flashcards, mind maps, and timelines

### Interview Preparation
- **🎤 Virtual Interview** - Practice interview questions based on your study materials
- **💬 Interactive Conversations** - Engage in realistic interview-style Q&A sessions
- **📈 Progress Tracking** - Review your interview performance and responses

### Advanced Learning Tools
- **🃏 Flashcards** - AI-generated flashcards for quick revision
- **🧩 Mind Maps** - Visual representations of concepts and relationships
- **⏱️ Timelines** - Chronological organization of events and topics
- **📜 Doomscroll** - Swipeable learning cards for casual study sessions

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework for building APIs
- **Groq API** - High-performance LLM for text generation and Q&A
- **Pinecone** - Vector database for semantic search and similarity matching
- **MongoDB** - NoSQL database for persistent storage
- **SentenceTransformers** - Local embedding generation (all-mpnet-base-v2)
- **PyPDF2** - PDF text extraction
- **Motor** - Async MongoDB driver for FastAPI

### Frontend
- **React 18** - UI library for building interactive interfaces
- **Vite** - Next-generation frontend build tool
- **TipTap** - Rich text editor for notes
- **React PDF** - PDF viewing and rendering
- **ReactFlow** - Interactive diagrams and mind maps
- **Axios** - HTTP client for API communication

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
GROQ_API_KEY=your_groq_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=allinone-prep-index
MONGODB_URL=mongodb://localhost:27017/allinone_prep
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

### 1. Create a Notebook
- Click the "Create Notebook" button
- Enter a name, choose a color, and select an icon
- Click "Create"

### 2. Upload PDFs
- Select your notebook
- Click "Upload PDFs" in the sidebar
- Drag and drop PDF files or click to browse
- Wait for processing to complete

### 3. Ask Questions
- Type your question in the chat input
- Optionally select specific documents to search
- Get AI-powered answers with source citations

### 4. Generate Quizzes
- Navigate to the Quiz section
- Select documents and difficulty level
- Choose the number of questions
- Take the quiz and get instant feedback

### 5. Create Notes
- Go to the Notes section
- Use the rich text editor to create notes
- Generate AI summaries, flashcards, or mind maps
- Organize with tags and colors

### 6. Practice Interviews
- Enter the Virtual Interview mode
- Answer questions based on your study materials
- Review your responses and improve

## Project Structure

```
PRISM/
├── backend/                     # Python FastAPI backend
│   ├── main.py                  # Main application and API endpoints (~2400 lines)
│   ├── database.py              # MongoDB configuration and collections
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment variables template
│   ├── .env                     # Your environment variables (gitignored)
│   └── uploads/                 # PDF file storage
│
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── FileUploadModal.jsx
│   │   │   ├── Quiz.jsx
│   │   │   ├── MockTest.jsx
│   │   │   ├── Notes.jsx
│   │   │   ├── PDFAnnotator.jsx
│   │   │   ├── VirtualInterview.jsx
│   │   │   ├── Doomscroll.jsx
│   │   │   ├── Library.jsx
│   │   │   └── ...
│   │   ├── contexts/
│   │   │   └── NotebookContext.jsx  # Global state management
│   │   ├── App.jsx              # Main app component
│   │   ├── main.jsx             # React entry point
│   │   └── index.css            # Global styles
│   ├── public/                  # Static assets
│   ├── package.json             # Frontend dependencies
│   └── vite.config.js           # Vite configuration
│
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## API Documentation

Once the backend is running, visit **http://localhost:8000/docs** for interactive API documentation (Swagger UI).

### Key Endpoints

#### Notebooks
- `POST /notebooks` - Create a new notebook
- `GET /notebooks` - List all notebooks
- `GET /notebooks/{notebook_id}` - Get a specific notebook
- `PUT /notebooks/{notebook_id}` - Update a notebook
- `DELETE /notebooks/{notebook_id}` - Delete a notebook

#### Documents
- `POST /upload-pdfs/{notebook_id}` - Upload PDF files
- `GET /documents/{notebook_id}` - List documents in a notebook
- `DELETE /documents/{doc_id}` - Delete a document
- `GET /documents/{notebook_id}/{doc_id}/pdf` - Download PDF

#### Q&A
- `POST /ask` - Ask a question about documents
- `GET /chat-history/{notebook_id}` - Get chat history
- `POST /chat-history` - Save chat messages
- `DELETE /chat-history/{notebook_id}` - Clear chat history

#### Quizzes
- `POST /generate-quiz` - Generate a quiz from documents
- `POST /submit-quiz` - Submit quiz answers

#### Notes
- `GET /notes/{notebook_id}` - Get all notes
- `POST /notes` - Create a new note
- `PUT /notes/{note_id}` - Update a note
- `DELETE /notes/{note_id}` - Delete a note

## How It Works

### RAG Pipeline

1. **Document Upload**
   - PDF files are uploaded and stored in the `uploads/` directory
   - Text is extracted from PDFs using PyPDF2
   - Text is split into chunks (1000 characters with 200 character overlap)

2. **Embedding Generation**
   - Each text chunk is converted to a 768-dimensional vector using SentenceTransformers
   - Embeddings are stored in Pinecone vector database with metadata

3. **Question Answering**
   - User question is converted to an embedding
   - Pinecone performs similarity search to find relevant chunks
   - Retrieved context is sent to LLM along with the question
   - LLM generates an answer based on the context
   - Sources are cited in the response

4. **Quiz Generation**
   - Relevant content is retrieved from documents
   - Groq LLM generates multiple-choice questions with varying difficulty
   - Questions are stored in MongoDB for tracking

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GROQ_API_KEY` | Groq API key for LLM | Yes | - |
| `PINECONE_API_KEY` | Pinecone API key | Yes | - |
| `PINECONE_ENVIRONMENT` | Pinecone environment region | Yes | us-east-1 |
| `PINECONE_INDEX_NAME` | Pinecone index name | No | pdf-rag-index |
| `MONGODB_URL` | MongoDB connection string | No | mongodb://localhost:27017 |

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

**Pinecone connection errors**
- Ensure your Pinecone environment matches your account region
- Wait ~1 minute after first run for index creation

**MongoDB connection errors**
- Ensure MongoDB is running locally, or check your MongoDB Atlas connection string
- Test connection: `mongosh "mongodb://localhost:27017"`

### Frontend Issues

**Port already in use**
- Change the port in `vite.config.js`

**CORS errors**
- Ensure backend is running on `http://localhost:8000`
- Check CORS configuration in `backend/main.py`

**Dependencies errors**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

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

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI inspired by modern learning platforms
- Powered by [Groq](https://groq.com/) for fast LLM inference
- Vector search by [Pinecone](https://www.pinecone.io/)

## Contact

For questions or feedback, please open an issue on GitHub.

---

Made with ❤️ for better learning
