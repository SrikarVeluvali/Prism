"""
PRISM - FastAPI Backend Server
===============================

An AI-powered learning and preparation platform that combines:
- RAG (Retrieval-Augmented Generation) for document Q&A
- Quiz and mock test generation
- Note-taking and PDF annotations
- Virtual interview preparation
- Interactive learning features (doomscroll, flashcards)

Tech Stack:
- FastAPI: Modern Python web framework
- Groq API: LLM for text generation and Q&A
- Pinecone: Vector database for semantic search
- MongoDB: Document database for persistent storage
- SentenceTransformers: Local embedding generation

Author: Srikar
Project: PRISM
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import PyPDF2
import io
import uuid
from datetime import datetime
import json
import re
import random
from bson import ObjectId
from pathlib import Path

# Import database collections and initialization function
from database import (
    notebooks_collection,
    documents_collection,
    quiz_results_collection,
    mock_test_results_collection,
    chat_history_collection,
    notes_collection,
    annotations_collection,
    interview_sessions_collection,
    saved_cards_collection,
    doomscroll_folders_collection,
    init_db
)

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="PRISM API",
    description="AI-powered learning and preparation platform",
    version="1.0.0"
)

# File Upload Configuration
# =========================
# Directory where uploaded PDF files are stored
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

# Application Startup Event
# =========================
@app.on_event("startup")
async def startup_event():
    """
    Initialize application resources on startup.
    - Creates database indexes for optimal query performance
    """
    init_db()
    print("Application started, database initialized")

# CORS Configuration
# ==================
# Enable Cross-Origin Resource Sharing for frontend communication
# Allows requests from React dev server (Vite on port 3000 and 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# AI Services Initialization
# ===========================

# Groq LLM Client
# Used for text generation, Q&A, quiz generation, and interview responses
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Sentence Transformer Model
# Converts text to 768-dimensional embeddings for semantic search
# Model: all-mpnet-base-v2 (best quality for semantic similarity)
embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Pinecone Vector Database
# =========================
# Initialize Pinecone client for storing and searching document embeddings
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX_NAME", "pdf-rag-index")

# Create Pinecone index if it doesn't exist
# Index stores 768-dimensional vectors with cosine similarity metric
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768,  # Matches all-mpnet-base-v2 embedding dimension
        metric="cosine",  # Cosine similarity for semantic search
        spec=ServerlessSpec(
            cloud="aws",
            region=os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
        )
    )

# Connect to the Pinecone index
index = pc.Index(index_name)

# In-Memory Data Stores
# =====================
# These stores cache data temporarily during runtime
# Persistent data is stored in MongoDB

# Document metadata cache (supplementary to MongoDB)
documents_store = {}

# Generated quizzes cache (before storing in MongoDB)
quizzes_store = {}

# Generated mock tests cache (before storing in MongoDB)
mock_tests_store = {}


# ==================== PYDANTIC MODELS ====================
# Data validation and serialization models using Pydantic

# Notebook Models
# ===============
class NotebookCreate(BaseModel):
    """Model for creating a new notebook"""
    name: str  # Notebook name
    color: str = "#2f5bea"  # Notebook theme color (hex)
    icon: str = "📚"  # Notebook icon emoji

class NotebookUpdate(BaseModel):
    """Model for updating an existing notebook"""
    name: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None


# Q&A and Chat Models
# ===================
class QuestionRequest(BaseModel):
    """Model for asking a question about documents"""
    question: str  # User's question
    document_ids: Optional[List[str]] = None  # Specific documents to search (None = all)
    notebook_id: str  # Notebook context

class ChatMessage(BaseModel):
    """Model for a single chat message"""
    role: str  # 'user' or 'assistant'
    content: str  # Message text

class ChatHistorySave(BaseModel):
    """Model for saving chat conversation history"""
    notebook_id: str
    messages: List[ChatMessage]


# Quiz Models
# ===========
class QuizGenerateRequest(BaseModel):
    """Model for generating a quiz from documents"""
    notebook_id: str
    document_ids: Optional[List[str]] = None  # Specific documents (None = all)
    num_questions: int = 5  # Number of MCQ questions
    difficulty: str = "medium"  # easy, medium, hard

class QuizAnswer(BaseModel):
    """Model for a single quiz answer"""
    question_index: int  # Question number (0-indexed)
    selected_option: int  # Selected option (0-3 for A-D)

class QuizSubmitRequest(BaseModel):
    """Model for submitting quiz answers"""
    quiz_id: str  # Generated quiz identifier
    answers: List[QuizAnswer]


# Mock Test Models
# ================
class MockTestGenerateRequest(BaseModel):
    """Model for generating a comprehensive mock test"""
    notebook_id: str
    document_ids: Optional[List[str]] = None
    num_theory: int = 3  # Number of theory questions
    num_coding: int = 2  # Number of coding questions
    num_reorder: int = 2  # Number of reordering questions
    difficulty: str = "medium"  # easy, medium, hard
    programming_language: str = "python"  # For coding questions

class TheoryAnswer(BaseModel):
    """Model for theory question answer"""
    question_index: int
    answer_text: str  # Long-form text answer

class CodingAnswer(BaseModel):
    """Model for coding question answer"""
    question_index: int
    code: str  # Code solution
    language: str  # Programming language used

class ReorderAnswer(BaseModel):
    """Model for reordering question answer"""
    question_index: int
    ordered_items: List[str]  # Correctly ordered items

class MockTestSubmitRequest(BaseModel):
    """Model for submitting mock test answers"""
    test_id: str
    theory_answers: List[TheoryAnswer]
    coding_answers: List[CodingAnswer]
    reorder_answers: List[ReorderAnswer]


# Notes Models
# ============
class NoteCreate(BaseModel):
    """Model for creating a new note"""
    notebook_id: str
    title: str
    content: str  # Can be text, HTML, JSON for drawing, or structured data
    note_type: str = "text"  # text, rich_text, drawing, ai_mindmap, ai_flashcards, ai_quiz, ai_timeline
    color: str = "#ffffff"  # Note background color
    tags: Optional[List[str]] = []  # Organizational tags

class NoteUpdate(BaseModel):
    """Model for updating an existing note"""
    title: Optional[str] = None
    content: Optional[str] = None
    color: Optional[str] = None
    tags: Optional[List[str]] = None

class NoteGenerateRequest(BaseModel):
    """Model for AI-generating notes from documents"""
    notebook_id: str
    document_ids: Optional[List[str]] = None
    topic: Optional[str] = None  # If provided, generates notes on this topic
    note_type: str = "summary"  # summary, key_points, mind_map, flashcards, quiz, timeline, comparison_table


# Annotation Models
# =================
class AnnotationCreate(BaseModel):
    """Model for creating a PDF annotation"""
    notebook_id: str
    document_id: str  # PDF document being annotated
    page_number: int  # Page number (0-indexed)
    highlighted_text: str  # Text that was highlighted
    position: dict  # Position data: {x, y, width, height}
    color: str = "#ffeb3b"  # Highlight color
    note: Optional[str] = None  # Optional annotation note

class AnnotationQueryRequest(BaseModel):
    """Model for asking questions about a specific annotation"""
    annotation_id: str
    question: str


# ==================== HELPER FUNCTIONS ====================

def extract_text_from_pdf(pdf_file):
    """
    Extract all text content from a PDF file.

    Args:
        pdf_file: File-like object or path to PDF

    Returns:
        str: Concatenated text from all pages
    """
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def chunk_text(text, chunk_size=1000, overlap=200):
    """
    Split text into overlapping chunks for better context retention.

    Overlapping ensures that context at chunk boundaries is not lost,
    improving the quality of semantic search results.

    Args:
        text: Input text to chunk
        chunk_size: Maximum characters per chunk (default: 1000)
        overlap: Number of overlapping characters between chunks (default: 200)

    Returns:
        List[str]: List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def get_embedding(text):
    """
    Convert text to 768-dimensional embedding vector.

    Uses SentenceTransformer model (all-mpnet-base-v2) to generate
    embeddings for semantic similarity search.

    Args:
        text: Input text to embed

    Returns:
        List[float]: 768-dimensional embedding vector, or None on error
    """
    try:
        embedding = embedding_model.encode(text)
        return embedding.tolist()
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None


async def ensure_document_chunks(doc: dict) -> List[str]:
    """
    Ensure a document has text chunks, regenerating from PDF if needed.

    This function checks if a document has pre-cached chunks in the database.
    If not, it re-extracts text from the PDF and chunks it.

    Args:
        doc: Document dictionary from MongoDB

    Returns:
        List[str]: List of text chunks
    """
    chunks = doc.get("chunks") or []

    if chunks:
        return chunks

    # Try to resolve the PDF path
    pdf_path = doc.get("file_path")
    if not pdf_path:
        notebook_id = doc.get("notebook_id")
        doc_id = doc.get("doc_id")
        if notebook_id and doc_id:
            pdf_path = UPLOADS_DIR / notebook_id / f"{doc_id}.pdf"
    else:
        pdf_path = Path(pdf_path)

    if not pdf_path or not Path(pdf_path).exists():
        print(f"Unable to locate PDF for document {doc.get('doc_id')}")
        return []

    try:
        with open(pdf_path, "rb") as pdf_file:
            text = extract_text_from_pdf(pdf_file)
    except Exception as e:
        print(f"Error re-extracting text for document {doc.get('doc_id')}: {e}")
        return []

    chunks = chunk_text(text)

    if not chunks:
        return []

    # Persist chunks for future calls (best effort)
    try:
        update_fields = {"chunks": chunks, "chunks_count": len(chunks)}
        doc_id = doc.get("_id")
        if doc_id:
            await documents_collection.update_one({"_id": doc_id}, {"$set": update_fields})
    except Exception as e:
        print(f"Error caching chunks for document {doc.get('doc_id')}: {e}")

    return chunks


def notebook_helper(notebook) -> dict:
    """
    Convert MongoDB notebook document to API response format.

    Transforms ObjectId to string and provides default values for optional fields.

    Args:
        notebook: MongoDB notebook document

    Returns:
        dict: Formatted notebook data for API response
    """
    return {
        "id": str(notebook["_id"]),
        "name": notebook["name"],
        "color": notebook.get("color", "#2f5bea"),
        "icon": notebook.get("icon", "📚"),
        "created_at": notebook["created_at"],
        "document_count": notebook.get("document_count", 0)
    }


# ==================== API ENDPOINTS ====================

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {"message": "RAG API is running"}


# ==================== NOTEBOOK ENDPOINTS ====================

@app.post("/notebooks")
async def create_notebook(notebook: NotebookCreate):
    """
    Create a new notebook.

    Notebooks are the primary organizational unit, containing documents,
    notes, quizzes, and chat history.
    """
    try:
        notebook_data = {
            "name": notebook.name,
            "color": notebook.color,
            "icon": notebook.icon,
            "created_at": datetime.now().isoformat(),
            "document_count": 0
        }

        result = await notebooks_collection.insert_one(notebook_data)
        notebook_data["_id"] = result.inserted_id

        return notebook_helper(notebook_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notebooks")
async def get_notebooks():
    """Get all notebooks"""
    try:
        notebooks = []
        async for notebook in notebooks_collection.find().sort("created_at", -1):
            # Count documents for this notebook
            doc_count = await documents_collection.count_documents({"notebook_id": str(notebook["_id"])})
            notebook["document_count"] = doc_count
            notebooks.append(notebook_helper(notebook))

        return {"notebooks": notebooks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notebooks/{notebook_id}")
async def get_notebook(notebook_id: str):
    """Get a specific notebook"""
    try:
        notebook = await notebooks_collection.find_one({"_id": ObjectId(notebook_id)})
        if not notebook:
            raise HTTPException(status_code=404, detail="Notebook not found")

        doc_count = await documents_collection.count_documents({"notebook_id": notebook_id})
        notebook["document_count"] = doc_count

        return notebook_helper(notebook)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/notebooks/{notebook_id}")
async def update_notebook(notebook_id: str, notebook_update: NotebookUpdate):
    """Update a notebook"""
    try:
        update_data = {}
        if notebook_update.name is not None:
            update_data["name"] = notebook_update.name
        if notebook_update.color is not None:
            update_data["color"] = notebook_update.color
        if notebook_update.icon is not None:
            update_data["icon"] = notebook_update.icon

        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")

        result = await notebooks_collection.update_one(
            {"_id": ObjectId(notebook_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Notebook not found")

        updated_notebook = await notebooks_collection.find_one({"_id": ObjectId(notebook_id)})
        doc_count = await documents_collection.count_documents({"notebook_id": notebook_id})
        updated_notebook["document_count"] = doc_count

        return notebook_helper(updated_notebook)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/notebooks/{notebook_id}")
async def delete_notebook(notebook_id: str):
    """Delete a notebook and all its documents"""
    try:
        # Delete all documents associated with this notebook
        await documents_collection.delete_many({"notebook_id": notebook_id})

        # Delete from Pinecone (all vectors with this notebook metadata)
        try:
            index.delete(filter={"notebook_id": notebook_id})
        except:
            pass  # Pinecone might not have any vectors

        # Delete the notebook
        result = await notebooks_collection.delete_one({"_id": ObjectId(notebook_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Notebook not found")

        return {"message": "Notebook deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-pdfs/{notebook_id}")
async def upload_pdfs(notebook_id: str, files: List[UploadFile] = File(...)):
    """Upload and process multiple PDF files for a notebook"""
    try:
        # Verify notebook exists
        notebook = await notebooks_collection.find_one({"_id": ObjectId(notebook_id)})
        if not notebook:
            raise HTTPException(status_code=404, detail="Notebook not found")

        uploaded_docs = []

        # Create notebook directory if it doesn't exist
        notebook_dir = UPLOADS_DIR / notebook_id
        notebook_dir.mkdir(exist_ok=True)

        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"{file.filename} is not a PDF file")

            # Read PDF content
            content = await file.read()
            pdf_file = io.BytesIO(content)

            # Extract text
            text = extract_text_from_pdf(pdf_file)

            # Create chunks
            chunks = chunk_text(text)

            # Generate document ID
            doc_id = str(uuid.uuid4())

            # Save PDF file to disk
            pdf_path = notebook_dir / f"{doc_id}.pdf"
            with open(pdf_path, "wb") as f:
                f.write(content)

            # Store document metadata in MongoDB
            doc_data = {
                "doc_id": doc_id,
                "notebook_id": notebook_id,
                "filename": file.filename,
                "uploaded_at": datetime.now().isoformat(),
                "chunks_count": len(chunks),
                "chunks": chunks,
                "file_path": str(pdf_path)
            }
            await documents_collection.insert_one(doc_data)

            # Process and store chunks in Pinecone
            vectors = []
            for i, chunk in enumerate(chunks):
                embedding = get_embedding(chunk)
                if embedding:
                    vectors.append({
                        "id": f"{doc_id}_{i}",
                        "values": embedding,
                        "metadata": {
                            "doc_id": doc_id,
                            "notebook_id": notebook_id,
                            "filename": file.filename,
                            "chunk_index": i,
                            "text": chunk
                        }
                    })

            # Upsert to Pinecone in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                index.upsert(vectors=batch)

            uploaded_docs.append({
                "id": doc_id,
                "filename": file.filename,
                "uploaded_at": doc_data["uploaded_at"],
                "chunks_count": len(chunks)
            })

        # Update notebook document count
        await notebooks_collection.update_one(
            {"_id": ObjectId(notebook_id)},
            {"$inc": {"document_count": len(files)}}
        )

        return {
            "message": f"Successfully uploaded {len(files)} PDF(s)",
            "documents": uploaded_docs
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{notebook_id}")
async def get_documents(notebook_id: str):
    """Get list of uploaded documents for a notebook"""
    try:
        documents = []
        async for doc in documents_collection.find({"notebook_id": notebook_id}).sort("uploaded_at", -1):
            documents.append({
                "id": doc["doc_id"],
                "filename": doc["filename"],
                "uploaded_at": doc["uploaded_at"],
                "chunks_count": doc["chunks_count"]
            })
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{notebook_id}/{doc_id}/pdf")
async def get_pdf(notebook_id: str, doc_id: str):
    """Serve PDF file"""
    try:
        # Find the document
        doc = await documents_collection.find_one({"doc_id": doc_id, "notebook_id": notebook_id})
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Get the PDF file path
        if "file_path" in doc:
            pdf_path = Path(doc["file_path"])
        else:
            # Fallback for old documents
            pdf_path = UPLOADS_DIR / notebook_id / f"{doc_id}.pdf"

        print(f"Attempting to serve PDF from: {pdf_path.absolute()}")

        if not pdf_path.exists():
            print(f"PDF file not found at: {pdf_path.absolute()}")
            raise HTTPException(status_code=404, detail=f"PDF file not found on disk: {pdf_path.name}")

        return FileResponse(
            path=str(pdf_path.absolute()),
            media_type="application/pdf",
            filename=doc["filename"],
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error serving PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and its vectors"""
    try:
        # Find the document
        doc = await documents_collection.find_one({"doc_id": doc_id})
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        notebook_id = doc["notebook_id"]

        # Delete the PDF file from disk
        if "file_path" in doc:
            pdf_path = Path(doc["file_path"])
            if pdf_path.exists():
                pdf_path.unlink()

        # Delete vectors from Pinecone
        try:
            index.delete(filter={"doc_id": doc_id})
        except:
            pass

        # Remove from MongoDB
        await documents_collection.delete_one({"doc_id": doc_id})

        # Update notebook document count
        await notebooks_collection.update_one(
            {"_id": ObjectId(notebook_id)},
            {"$inc": {"document_count": -1}}
        )

        return {"message": "Document deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Ask a question about the uploaded documents"""
    try:
        # Get question embedding
        question_embedding = embedding_model.encode(request.question).tolist()

        # Build filter for notebook and specific documents if provided
        filter_dict = {"notebook_id": request.notebook_id}
        if request.document_ids:
            filter_dict["doc_id"] = {"$in": request.document_ids}

        # Query Pinecone
        results = index.query(
            vector=question_embedding,
            top_k=5,
            include_metadata=True,
            filter=filter_dict
        )

        if not results.matches:
            return {
                "answer": "I couldn't find any relevant information in the uploaded documents.",
                "sources": []
            }

        # Extract relevant context
        context_parts = []
        sources = []

        for match in results.matches:
            context_parts.append(match.metadata['text'])
            sources.append({
                "filename": match.metadata['filename'],
                "chunk_index": match.metadata['chunk_index'],
                "score": float(match.score)
            })

        context = "\n\n".join(context_parts)

        # Generate answer using Groq
        prompt = f"""Based on the following context from the uploaded documents, please answer the question.
If the answer cannot be found in the context, say so.

Context:
{context}

Question: {request.question}

Answer:"""

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",  # You can also use "mixtral-8x7b-32768" or other Groq models
            temperature=0.7,
            max_tokens=1024
        )

        answer = chat_completion.choices[0].message.content

        return {
            "answer": answer,
            "sources": sources
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-quiz")
async def generate_quiz(request: QuizGenerateRequest):
    """Generate a quiz based on uploaded documents"""
    try:
        print(f"Generating quiz with {request.num_questions} questions, difficulty: {request.difficulty}")

        # Check if notebook has documents
        doc_count = await documents_collection.count_documents({"notebook_id": request.notebook_id})
        if doc_count == 0:
            raise HTTPException(status_code=400, detail="No documents uploaded. Please upload documents first.")

        # Build filter for notebook and specific documents if provided
        filter_dict = {"notebook_id": request.notebook_id}
        if request.document_ids:
            filter_dict["doc_id"] = {"$in": request.document_ids}

        # Get random chunks from documents
        # We'll query multiple times with different random embeddings to get diverse content
        all_chunks = []
        num_queries = min(request.num_questions * 2, 10)  # Get more chunks than questions needed

        for _ in range(num_queries):
            # Create a random query to get different chunks
            random_text = f"question {random.randint(1, 10000)}"
            query_embedding = embedding_model.encode(random_text).tolist()

            results = index.query(
                vector=query_embedding,
                top_k=3,
                include_metadata=True,
                filter=filter_dict
            )

            for match in results.matches:
                if match.metadata['text'] not in [c['text'] for c in all_chunks]:
                    all_chunks.append({
                        'text': match.metadata['text'],
                        'filename': match.metadata['filename']
                    })

        # Limit to a reasonable amount of context
        selected_chunks = all_chunks[:min(len(all_chunks), request.num_questions * 2)]

        if not selected_chunks:
            raise HTTPException(status_code=400, detail="Could not retrieve content from documents. Please ensure documents are properly uploaded.")

        context = "\n\n".join([chunk['text'] for chunk in selected_chunks])
        print(f"Retrieved {len(selected_chunks)} chunks for quiz generation")

        # Generate quiz using Groq
        prompt = f"""Based on the following content from educational documents, generate {request.num_questions} multiple-choice questions (MCQs).

Content:
{context}

Requirements:
1. Generate exactly {request.num_questions} questions
2. Each question should have 4 options (A, B, C, D)
3. Questions should test understanding of the content
4. Difficulty level: {request.difficulty}
5. Indicate the correct answer for each question
6. Questions should be diverse and cover different topics from the content

Format your response as a JSON array with this structure:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Brief explanation of why this is correct",
    "topic": "Main topic this question covers"
  }}
]

IMPORTANT: Return ONLY the JSON array, no additional text."""

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful educational assistant that creates high-quality quiz questions. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=2048
        )

        response_text = chat_completion.choices[0].message.content.strip()

        # Try to extract JSON if there's extra text
        # Look for JSON array in the response
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if json_match:
            response_text = json_match.group()

        questions = json.loads(response_text)

        # Generate quiz ID
        quiz_id = str(uuid.uuid4())

        # Store quiz
        quizzes_store[quiz_id] = {
            "id": quiz_id,
            "questions": questions,
            "created_at": datetime.now().isoformat(),
            "document_ids": request.document_ids,
            "num_questions": len(questions)
        }

        # Return questions without correct answers
        questions_for_user = [
            {
                "question": q["question"],
                "options": q["options"],
                "topic": q.get("topic", "General")
            }
            for q in questions
        ]

        return {
            "quiz_id": quiz_id,
            "questions": questions_for_user,
            "total_questions": len(questions)
        }

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse quiz questions: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit-quiz")
async def submit_quiz(request: QuizSubmitRequest):
    """Submit quiz answers and get score with analysis"""
    try:
        if request.quiz_id not in quizzes_store:
            raise HTTPException(status_code=404, detail="Quiz not found")

        quiz = quizzes_store[request.quiz_id]
        questions = quiz["questions"]

        # Calculate score
        correct_count = 0
        total_questions = len(questions)
        results = []
        topic_performance = {}

        for answer in request.answers:
            question = questions[answer.question_index]
            is_correct = answer.selected_option == question["correct_answer"]

            if is_correct:
                correct_count += 1

            topic = question.get("topic", "General")
            if topic not in topic_performance:
                topic_performance[topic] = {"correct": 0, "total": 0}

            topic_performance[topic]["total"] += 1
            if is_correct:
                topic_performance[topic]["correct"] += 1

            results.append({
                "question_index": answer.question_index,
                "question": question["question"],
                "selected_option": answer.selected_option,
                "correct_answer": question["correct_answer"],
                "is_correct": is_correct,
                "explanation": question.get("explanation", ""),
                "topic": topic
            })

        score_percentage = (correct_count / total_questions) * 100

        # Generate analysis using Groq
        weak_topics = [
            topic for topic, perf in topic_performance.items()
            if perf["correct"] / perf["total"] < 0.6
        ]

        strong_topics = [
            topic for topic, perf in topic_performance.items()
            if perf["correct"] / perf["total"] >= 0.8
        ]

        analysis_prompt = f"""Analyze this quiz performance and provide personalized feedback:

Score: {correct_count}/{total_questions} ({score_percentage:.1f}%)

Topic Performance:
{json.dumps(topic_performance, indent=2)}

Weak Topics: {', '.join(weak_topics) if weak_topics else 'None'}
Strong Topics: {', '.join(strong_topics) if strong_topics else 'None'}

Provide:
1. Brief overall assessment (2-3 sentences)
2. Specific areas to improve with actionable recommendations
3. Strengths to maintain
4. Study suggestions

Keep the response concise, encouraging, and actionable."""

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": analysis_prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1024
        )

        analysis = chat_completion.choices[0].message.content

        return {
            "quiz_id": request.quiz_id,
            "score": correct_count,
            "total_questions": total_questions,
            "score_percentage": score_percentage,
            "results": results,
            "topic_performance": topic_performance,
            "analysis": analysis,
            "weak_topics": weak_topics,
            "strong_topics": strong_topics
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-mock-test")
async def generate_mock_test(request: MockTestGenerateRequest):
    """Generate a comprehensive mock test with theory, coding, and reorder questions"""
    try:
        print(f"Generating mock test: {request.num_theory} theory, {request.num_coding} coding, {request.num_reorder} reorder")

        # Check if notebook has documents
        doc_count = await documents_collection.count_documents({"notebook_id": request.notebook_id})
        if doc_count == 0:
            raise HTTPException(status_code=400, detail="No documents uploaded. Please upload documents first.")

        # Build filter for notebook and specific documents if provided
        filter_dict = {"notebook_id": request.notebook_id}
        if request.document_ids:
            filter_dict["doc_id"] = {"$in": request.document_ids}

        # Get diverse chunks from documents
        all_chunks = []
        num_queries = min((request.num_theory + request.num_coding + request.num_reorder) * 2, 15)

        for _ in range(num_queries):
            random_text = f"test {random.randint(1, 10000)}"
            query_embedding = embedding_model.encode(random_text).tolist()

            results = index.query(
                vector=query_embedding,
                top_k=3,
                include_metadata=True,
                filter=filter_dict
            )

            for match in results.matches:
                if match.metadata['text'] not in [c['text'] for c in all_chunks]:
                    all_chunks.append({
                        'text': match.metadata['text'],
                        'filename': match.metadata['filename']
                    })

        if not all_chunks:
            raise HTTPException(status_code=400, detail="Could not retrieve content from documents.")

        context = "\n\n".join([chunk['text'] for chunk in all_chunks])

        # Detect if content has code (for determining if coding questions are applicable)
        has_code = any(keyword in context.lower() for keyword in ['function', 'class', 'def ', 'int ', 'string', 'array', 'algorithm'])

        # Generate questions using Groq
        # Language-specific examples
        lang_examples = {
            "python": 'def function_name(params):',
            "javascript": 'function functionName(params) { }',
            "java": 'public returnType functionName(params) { }',
            "cpp": 'returnType functionName(params) { }',
            "c": 'returnType functionName(params) { }',
            "go": 'func functionName(params) returnType { }',
            "rust": 'fn function_name(params) -> ReturnType { }',
            "typescript": 'function functionName(params): ReturnType { }'
        }

        func_example = lang_examples.get(request.programming_language.lower(), 'def function_name(params):')

        prompt = f"""Based on the following educational content, generate a comprehensive mock test.

Content:
{context}

Generate a JSON object with the following structure:
{{
  "theory_questions": [
    {{
      "question": "Theory question text?",
      "topic": "Topic name",
      "expected_points": ["key point 1", "key point 2"],
      "difficulty": "{request.difficulty}"
    }}
  ],
  "coding_questions": [
    {{
      "question": "Coding problem description",
      "topic": "Topic name",
      "function_signature": "{func_example}",
      "language": "{request.programming_language}",
      "test_cases": [
        {{"input": "example input", "expected_output": "expected result"}}
      ],
      "difficulty": "{request.difficulty}"
    }}
  ],
  "reorder_questions": [
    {{
      "question": "Put these steps in the correct order:",
      "topic": "Topic name",
      "items": ["Step 1", "Step 2", "Step 3", "Step 4"],
      "correct_order": ["Step 2", "Step 1", "Step 4", "Step 3"],
      "difficulty": "{request.difficulty}"
    }}
  ]
}}

Requirements:
1. Generate {request.num_theory} theory questions that require written explanations
2. Generate {request.num_coding if has_code else 0} coding questions in {request.programming_language.upper()} {"(code-related content detected)" if has_code else "(skip if content is not programming-related)"}
3. Generate {request.num_reorder} reordering questions for sequential/procedural content
4. Theory questions should test understanding and ask for explanations
5. Coding questions MUST be in {request.programming_language.upper()} with appropriate syntax and function signatures
6. Reorder questions should have items shuffled (not in correct order)
7. Difficulty: {request.difficulty}

IMPORTANT: Return ONLY the JSON object, no additional text."""

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational assessment creator. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=3000
        )

        response_text = chat_completion.choices[0].message.content.strip()

        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            response_text = json_match.group()

        test_data = json.loads(response_text)

        # Generate test ID
        test_id = str(uuid.uuid4())

        # Store test with correct answers
        mock_tests_store[test_id] = {
            "id": test_id,
            "theory_questions": test_data.get("theory_questions", []),
            "coding_questions": test_data.get("coding_questions", []) if has_code else [],
            "reorder_questions": test_data.get("reorder_questions", []),
            "created_at": datetime.now().isoformat(),
            "document_ids": request.document_ids,
            "has_code": has_code
        }

        # Return questions without answers
        return {
            "test_id": test_id,
            "theory_questions": [
                {
                    "question": q["question"],
                    "topic": q.get("topic", "General")
                }
                for q in test_data.get("theory_questions", [])
            ],
            "coding_questions": [
                {
                    "question": q["question"],
                    "topic": q.get("topic", "Coding"),
                    "function_signature": q.get("function_signature", ""),
                    "language": q.get("language", "python"),
                    "test_cases": [{"input": tc["input"]} for tc in q.get("test_cases", [])]
                }
                for q in (test_data.get("coding_questions", []) if has_code else [])
            ],
            "reorder_questions": [
                {
                    "question": q["question"],
                    "topic": q.get("topic", "General"),
                    "items": q["items"]  # Already shuffled by AI
                }
                for q in test_data.get("reorder_questions", [])
            ],
            "total_questions": len(test_data.get("theory_questions", [])) +
                             len(test_data.get("coding_questions", []) if has_code else []) +
                             len(test_data.get("reorder_questions", []))
        }

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse test questions: {str(e)}")
    except Exception as e:
        print(f"Error generating mock test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit-mock-test")
async def submit_mock_test(request: MockTestSubmitRequest):
    """Submit mock test answers and get AI evaluation"""
    try:
        print(f"Submitting mock test: {request.test_id}")

        if request.test_id not in mock_tests_store:
            raise HTTPException(status_code=404, detail="Test not found")

        test = mock_tests_store[request.test_id]

        print(f"Test found. Theory: {len(test['theory_questions'])}, Coding: {len(test['coding_questions'])}, Reorder: {len(test['reorder_questions'])}")
        print(f"Submitted answers - Theory: {len(request.theory_answers)}, Coding: {len(request.coding_answers)}, Reorder: {len(request.reorder_answers)}")

        # Evaluate theory questions
        theory_results = []
        for answer in request.theory_answers:
            if answer.question_index >= len(test["theory_questions"]):
                print(f"Warning: Theory question index {answer.question_index} out of range")
                continue
            question = test["theory_questions"][answer.question_index]

            # Use AI to evaluate the answer
            eval_prompt = f"""Evaluate this answer to a theory question and respond with ONLY a JSON object.

Question: {question['question']}

Expected key points: {', '.join(question.get('expected_points', []))}

Student's answer: {answer.answer_text}

Return ONLY this JSON format (no other text):
{{
  "score": <number 0-100>,
  "feedback": "<detailed feedback on what was good and what was missing>",
  "covered_points": ["<point 1>", "<point 2>"],
  "missing_points": ["<point 1>", "<point 2>"]
}}

Be fair but thorough. Award partial credit for partially correct answers.
CRITICAL: Return ONLY the JSON object. No explanations before or after."""

            eval_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an educational evaluator. You MUST respond with ONLY valid JSON. No markdown, no explanations, just the JSON object."
                    },
                    {
                        "role": "user",
                        "content": eval_prompt
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.2,
                max_tokens=500
            )

            eval_text = eval_completion.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            eval_text = re.sub(r'^```json\s*', '', eval_text)
            eval_text = re.sub(r'^```\s*', '', eval_text)
            eval_text = re.sub(r'\s*```$', '', eval_text)
            eval_text = eval_text.strip()

            # Extract JSON object
            json_match = re.search(r'\{[\s\S]*\}', eval_text)
            if json_match:
                eval_text = json_match.group()

            try:
                evaluation = json.loads(eval_text)
                # Validate required fields
                if "score" not in evaluation or "feedback" not in evaluation:
                    raise ValueError("Missing required fields in evaluation")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"JSON parse error for theory question {answer.question_index}: {str(e)}")
                print(f"Response text: {eval_text[:500]}")  # Print first 500 chars
                # Fallback evaluation
                evaluation = {
                    "score": 50,
                    "feedback": "Your answer has been recorded but could not be fully evaluated. Consider providing more detail and covering the key concepts.",
                    "covered_points": [],
                    "missing_points": []
                }

            theory_results.append({
                "question_index": answer.question_index,
                "question": question["question"],
                "user_answer": answer.answer_text,
                "score": evaluation["score"],
                "feedback": evaluation["feedback"],
                "covered_points": evaluation.get("covered_points", []),
                "missing_points": evaluation.get("missing_points", []),
                "topic": question.get("topic", "General")
            })

        # Evaluate coding questions
        coding_results = []
        for answer in request.coding_answers:
            if answer.question_index >= len(test["coding_questions"]):
                print(f"Warning: Coding question index {answer.question_index} out of range")
                continue
            question = test["coding_questions"][answer.question_index]

            # Use AI to evaluate the code
            eval_prompt = f"""Evaluate this code solution and respond with ONLY a JSON object.

Problem: {question['question']}

Expected function signature: {question.get('function_signature', '')}

Test cases:
{json.dumps(question.get('test_cases', []), indent=2)}

Student's code:
```{answer.language}
{answer.code}
```

Return ONLY this JSON format (no other text):
{{
  "score": <number 0-100>,
  "correctness": "<brief assessment of logic>",
  "code_quality": "<brief assessment of quality>",
  "test_results": ["<pass or fail for each test>"],
  "feedback": "<detailed feedback in 2-3 sentences>",
  "suggestions": ["<suggestion 1>", "<suggestion 2>"]
}}

CRITICAL: Return ONLY the JSON object. No explanations before or after."""

            eval_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a code evaluator. You MUST respond with ONLY valid JSON. No markdown, no explanations, just the JSON object."
                    },
                    {
                        "role": "user",
                        "content": eval_prompt
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.2,
                max_tokens=800
            )

            eval_text = eval_completion.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            eval_text = re.sub(r'^```json\s*', '', eval_text)
            eval_text = re.sub(r'^```\s*', '', eval_text)
            eval_text = re.sub(r'\s*```$', '', eval_text)
            eval_text = eval_text.strip()

            # Extract JSON object
            json_match = re.search(r'\{[\s\S]*\}', eval_text)
            if json_match:
                eval_text = json_match.group()

            try:
                evaluation = json.loads(eval_text)
                # Validate required fields
                if "score" not in evaluation or "feedback" not in evaluation:
                    raise ValueError("Missing required fields in evaluation")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"JSON parse error for coding question {answer.question_index}: {str(e)}")
                print(f"Response text: {eval_text[:500]}")  # Print first 500 chars
                # Fallback evaluation
                evaluation = {
                    "score": 50,
                    "correctness": "Code has syntax errors or incomplete implementation",
                    "code_quality": "Needs improvement",
                    "test_results": [],
                    "feedback": "The code appears incomplete or has errors. Please review the function signature and ensure proper implementation.",
                    "suggestions": ["Complete the function implementation", "Fix any syntax errors", "Test with provided test cases"]
                }

            coding_results.append({
                "question_index": answer.question_index,
                "question": question["question"],
                "user_code": answer.code,
                "score": evaluation["score"],
                "correctness": evaluation.get("correctness", ""),
                "code_quality": evaluation.get("code_quality", ""),
                "feedback": evaluation["feedback"],
                "suggestions": evaluation.get("suggestions", []),
                "topic": question.get("topic", "Coding")
            })

        # Evaluate reorder questions
        reorder_results = []
        for answer in request.reorder_answers:
            if answer.question_index >= len(test["reorder_questions"]):
                print(f"Warning: Reorder question index {answer.question_index} out of range")
                continue
            question = test["reorder_questions"][answer.question_index]
            correct_order = question["correct_order"]
            user_order = answer.ordered_items

            # Calculate score based on correct positions
            correct_count = sum(1 for i, item in enumerate(user_order) if i < len(correct_order) and item == correct_order[i])
            score = (correct_count / len(correct_order)) * 100

            reorder_results.append({
                "question_index": answer.question_index,
                "question": question["question"],
                "user_order": user_order,
                "correct_order": correct_order,
                "score": score,
                "correct_positions": correct_count,
                "total_items": len(correct_order),
                "topic": question.get("topic", "General")
            })

        # Calculate overall score
        all_scores = [r["score"] for r in theory_results + coding_results + reorder_results]
        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0

        print(f"Evaluation complete. Overall score: {overall_score:.1f}%")

        # Topic-wise performance
        topic_performance = {}
        for result in theory_results + coding_results + reorder_results:
            topic = result["topic"]
            if topic not in topic_performance:
                topic_performance[topic] = {"scores": [], "count": 0}
            topic_performance[topic]["scores"].append(result["score"])
            topic_performance[topic]["count"] += 1

        for topic in topic_performance:
            scores = topic_performance[topic]["scores"]
            topic_performance[topic]["average"] = sum(scores) / len(scores)

        # Generate overall analysis
        if all_scores:
            theory_avg = sum(r['score'] for r in theory_results) / len(theory_results) if theory_results else 0
            coding_avg = sum(r['score'] for r in coding_results) / len(coding_results) if coding_results else 0
            reorder_avg = sum(r['score'] for r in reorder_results) / len(reorder_results) if reorder_results else 0

            analysis_prompt = f"""Provide a comprehensive performance analysis for this mock test:

Overall Score: {overall_score:.1f}%

Theory Questions Performance: {theory_avg:.1f}% ({len(theory_results)} questions)
Coding Questions Performance: {coding_avg:.1f}% ({len(coding_results)} questions)
Reordering Performance: {reorder_avg:.1f}% ({len(reorder_results)} questions)

Topic Performance:
{json.dumps(topic_performance, indent=2)}

Provide:
1. Overall assessment (2-3 sentences)
2. Strengths demonstrated
3. Areas needing improvement
4. Specific study recommendations
5. Next steps for preparation

Keep it encouraging but honest and actionable."""

            try:
                analysis_completion = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": analysis_prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    max_tokens=1000
                )
                overall_analysis = analysis_completion.choices[0].message.content
            except Exception as e:
                print(f"Error generating overall analysis: {str(e)}")
                overall_analysis = f"Overall Score: {overall_score:.1f}%. You completed {len(all_scores)} questions. Review the detailed feedback for each question to improve."
        else:
            overall_analysis = "No questions were answered. Please complete the test and submit again."

        return {
            "test_id": request.test_id,
            "overall_score": overall_score,
            "theory_results": theory_results,
            "coding_results": coding_results,
            "reorder_results": reorder_results,
            "topic_performance": topic_performance,
            "overall_analysis": overall_analysis,
            "total_questions": len(theory_results) + len(coding_results) + len(reorder_results)
        }

    except json.JSONDecodeError as e:
        print(f"JSON decode error in mock test submission: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to parse test data: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting mock test: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error evaluating test: {str(e)}")

# ==================== CHAT HISTORY ENDPOINTS ====================

@app.get("/chat-history/{notebook_id}")
async def get_chat_history(notebook_id: str):
    """Get chat history for a notebook"""
    try:
        messages = []
        async for chat in chat_history_collection.find(
            {"notebook_id": notebook_id}
        ).sort("created_at", 1):
            messages.append({
                "role": chat["role"],
                "content": chat["content"],
                "created_at": chat["created_at"]
            })
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat-history")
async def save_chat_message(request: ChatHistorySave):
    """Save chat messages to history"""
    try:
        # Save each message
        for message in request.messages:
            chat_data = {
                "notebook_id": request.notebook_id,
                "role": message.role,
                "content": message.content,
                "created_at": datetime.now().isoformat()
            }
            await chat_history_collection.insert_one(chat_data)
        return {"message": "Chat history saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chat-history/{notebook_id}")
async def clear_chat_history(notebook_id: str):
    """Clear chat history for a notebook"""
    try:
        await chat_history_collection.delete_many({"notebook_id": notebook_id})
        return {"message": "Chat history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== NOTES ENDPOINTS ====================

@app.get("/notes/{notebook_id}")
async def get_notes(notebook_id: str):
    """Get all notes for a notebook"""
    try:
        notes = []
        async for note in notes_collection.find(
            {"notebook_id": notebook_id}
        ).sort("created_at", -1):
            notes.append({
                "id": str(note["_id"]),
                "title": note["title"],
                "content": note["content"],
                "note_type": note["note_type"],
                "color": note.get("color", "#ffffff"),
                "tags": note.get("tags", []),
                "created_at": note["created_at"],
                "updated_at": note.get("updated_at", note["created_at"])
            })
        return {"notes": notes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notes")
async def create_note(note: NoteCreate):
    """Create a new note"""
    try:
        note_data = {
            "notebook_id": note.notebook_id,
            "title": note.title,
            "content": note.content,
            "note_type": note.note_type,
            "color": note.color,
            "tags": note.tags or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        result = await notes_collection.insert_one(note_data)

        # Return serializable response
        return {
            "id": str(result.inserted_id),
            "notebook_id": note.notebook_id,
            "title": note.title,
            "content": note.content,
            "note_type": note.note_type,
            "color": note.color,
            "tags": note.tags or [],
            "created_at": note_data["created_at"],
            "updated_at": note_data["updated_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/notes/{note_id}")
async def update_note(note_id: str, note_update: NoteUpdate):
    """Update a note"""
    try:
        update_data = {"updated_at": datetime.now().isoformat()}
        if note_update.title is not None:
            update_data["title"] = note_update.title
        if note_update.content is not None:
            update_data["content"] = note_update.content
        if note_update.color is not None:
            update_data["color"] = note_update.color
        if note_update.tags is not None:
            update_data["tags"] = note_update.tags

        await notes_collection.update_one(
            {"_id": ObjectId(note_id)},
            {"$set": update_data}
        )
        return {"message": "Note updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    """Delete a note"""
    try:
        await notes_collection.delete_one({"_id": ObjectId(note_id)})
        return {"message": "Note deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notes/generate")
async def generate_note(request: NoteGenerateRequest):
    """Generate AI notes from documents"""
    try:
        # Get relevant documents
        filter_dict = {"notebook_id": request.notebook_id}
        if request.document_ids:
            filter_dict["doc_id"] = {"$in": request.document_ids}

        # Query Pinecone for relevant content
        query_text = request.topic if request.topic else "comprehensive summary of all topics"
        query_embedding = get_embedding(query_text)

        if not query_embedding:
            raise HTTPException(status_code=500, detail="Failed to generate embedding")

        results = index.query(
            vector=query_embedding,
            top_k=10,
            filter=filter_dict,
            include_metadata=True
        )

        if not results['matches']:
            raise HTTPException(status_code=404, detail="No content found")

        # Gather context
        context_chunks = []
        for match in results['matches']:
            context_chunks.append(match['metadata']['text'])

        context = "\n\n".join(context_chunks)

        # Generate notes based on type
        if request.note_type == "summary":
            prompt = f"Create a comprehensive summary of the following content:\n\n{context}\n\nProvide a well-structured summary with key points."
            ai_note_type = "rich_text"
        elif request.note_type == "key_points":
            prompt = f"Extract and list the key points from the following content:\n\n{context}\n\nFormat as bullet points with brief explanations."
            ai_note_type = "rich_text"
        elif request.note_type == "mind_map":
            prompt = f"Create a mind map structure from the following content:\n\n{context}\n\nFormat as a hierarchical text structure with main topics and subtopics. Use indentation (2 spaces per level) to show hierarchy. Start each line with a dash. Example:\n- Main Topic 1\n  - Subtopic 1.1\n    - Detail 1.1.1\n  - Subtopic 1.2\n- Main Topic 2"
            ai_note_type = "ai_mindmap"
        elif request.note_type == "flashcards":
            prompt = f"Create study flashcards from the following content:\n\n{context}\n\nFormat each flashcard as:\nQ: [Question]\nA: [Answer]\n\nCreate 5-10 flashcards covering the most important concepts. Separate each flashcard with a blank line."
            ai_note_type = "ai_flashcards"
        elif request.note_type == "quiz":
            prompt = f"Create a multiple choice quiz from the following content:\n\n{context}\n\nFor each question, provide:\n1. The question text\nA) First option\nB) Second option\nC) Third option\nD) Fourth option\nAnswer: [Correct letter]\nExplanation: [Brief explanation]\n\nCreate 5-8 questions. Separate each question with a blank line."
            ai_note_type = "ai_quiz"
        elif request.note_type == "timeline":
            prompt = f"Create a chronological timeline from the following content:\n\n{context}\n\nFormat each event as:\n[Date/Year]: [Event Title]\n[Description]\n\nList events in chronological order. Separate each event with a blank line."
            ai_note_type = "ai_timeline"
        elif request.note_type == "comparison_table":
            prompt = f"Create a comparison table from the following content:\n\n{context}\n\nFormat as a markdown table comparing key concepts, features, or topics. Include relevant columns and rows."
            ai_note_type = "rich_text"
        else:
            prompt = f"Create study notes from the following content:\n\n{context}\n\nMake it comprehensive and well-organized."
            ai_note_type = "rich_text"

        completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=2000
        )

        generated_content = completion.choices[0].message.content

        # Create the note
        title = f"AI Generated {request.note_type.replace('_', ' ').title()}"
        if request.topic:
            title += f": {request.topic}"

        note_data = {
            "notebook_id": request.notebook_id,
            "title": title,
            "content": generated_content,
            "note_type": ai_note_type,
            "color": "#e3f2fd",
            "tags": ["AI Generated", request.note_type],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        result = await notes_collection.insert_one(note_data)

        # Return serializable response
        return {
            "id": str(result.inserted_id),
            "notebook_id": request.notebook_id,
            "title": title,
            "content": generated_content,
            "note_type": ai_note_type,
            "color": "#e3f2fd",
            "tags": ["AI Generated", request.note_type],
            "created_at": note_data["created_at"],
            "updated_at": note_data["updated_at"]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating note: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANNOTATIONS ENDPOINTS ====================

@app.get("/annotations/{notebook_id}")
async def get_annotations(notebook_id: str, document_id: Optional[str] = None):
    """Get annotations for a notebook or specific document"""
    try:
        filter_dict = {"notebook_id": notebook_id}
        if document_id:
            filter_dict["document_id"] = document_id

        annotations = []
        async for ann in annotations_collection.find(filter_dict).sort("created_at", -1):
            annotations.append({
                "id": str(ann["_id"]),
                "document_id": ann["document_id"],
                "page_number": ann["page_number"],
                "highlighted_text": ann["highlighted_text"],
                "position": ann["position"],
                "color": ann.get("color", "#ffeb3b"),
                "note": ann.get("note"),
                "created_at": ann["created_at"]
            })
        return {"annotations": annotations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/annotations")
async def create_annotation(annotation: AnnotationCreate):
    """Create a new annotation"""
    try:
        ann_data = {
            "notebook_id": annotation.notebook_id,
            "document_id": annotation.document_id,
            "page_number": annotation.page_number,
            "highlighted_text": annotation.highlighted_text,
            "position": annotation.position,
            "color": annotation.color,
            "note": annotation.note,
            "created_at": datetime.now().isoformat()
        }
        result = await annotations_collection.insert_one(ann_data)

        # Return serializable response
        return {
            "id": str(result.inserted_id),
            "notebook_id": annotation.notebook_id,
            "document_id": annotation.document_id,
            "page_number": annotation.page_number,
            "highlighted_text": annotation.highlighted_text,
            "position": annotation.position,
            "color": annotation.color,
            "note": annotation.note,
            "created_at": ann_data["created_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/annotations/{annotation_id}")
async def delete_annotation(annotation_id: str):
    """Delete an annotation"""
    try:
        await annotations_collection.delete_one({"_id": ObjectId(annotation_id)})
        return {"message": "Annotation deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/annotations/query")
async def query_annotation(request: AnnotationQueryRequest):
    """Ask AI about highlighted text"""
    try:
        # Get the annotation
        annotation = await annotations_collection.find_one({"_id": ObjectId(request.annotation_id)})
        if not annotation:
            raise HTTPException(status_code=404, detail="Annotation not found")

        # Create prompt with context
        prompt = f"""Based on this highlighted text from the document:

"{annotation['highlighted_text']}"

Question: {request.question}

Provide a clear and detailed answer."""

        completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=500
        )

        answer = completion.choices[0].message.content

        return {
            "question": request.question,
            "highlighted_text": annotation['highlighted_text'],
            "answer": answer
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error querying annotation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== UTILITY ENDPOINTS ====================

@app.delete("/clear-all")
def clear_all():
    """Clear all documents and vectors"""
    try:
        # Delete all vectors from Pinecone
        index.delete(delete_all=True)

        # Clear documents store
        documents_store.clear()

        # Clear quizzes store
        quizzes_store.clear()

        # Clear mock tests store
        mock_tests_store.clear()

        return {"message": "All documents cleared successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== VIRTUAL INTERVIEW ENDPOINTS ====================

class InterviewStartRequest(BaseModel):
    notebook_id: str
    interview_type: str  # technical, behavioral, mixed
    difficulty: str  # easy, medium, hard
    duration: int  # in minutes

class InterviewRespondRequest(BaseModel):
    session_id: str
    user_response: str

class InterviewEndRequest(BaseModel):
    session_id: str

@app.post("/interview/start")
async def start_interview(request: InterviewStartRequest):
    """Start a new interview session"""
    try:
        session_id = str(uuid.uuid4())

        # Get relevant content from documents in the notebook
        documents = []
        async for doc in documents_collection.find({"notebook_id": request.notebook_id}):
            documents.append(doc)

        # Generate initial greeting and first question based on interview type
        if request.interview_type == "technical":
            context_prompt = "You are conducting a technical interview. Focus on coding, algorithms, data structures, and technical problem-solving."
        elif request.interview_type == "behavioral":
            context_prompt = "You are conducting a behavioral interview. Focus on past experiences, teamwork, leadership, and soft skills."
        else:  # mixed
            context_prompt = "You are conducting a comprehensive interview covering both technical skills and behavioral aspects."

        difficulty_desc = {
            "easy": "Ask entry-level questions suitable for beginners.",
            "medium": "Ask intermediate-level questions for experienced candidates.",
            "hard": "Ask advanced questions for senior-level positions."
        }

        system_prompt = f"""You are an AI interviewer for a job interview simulation. {context_prompt}
{difficulty_desc.get(request.difficulty, '')}

Guidelines:
1. Be professional and friendly
2. Ask one question at a time
3. Listen to the candidate's response and ask relevant follow-up questions
4. The interview will last approximately {request.duration} minutes
5. Start with an introduction and ask the first question
6. Keep questions concise and clear
7. Adapt your questions based on the candidate's responses

Start the interview with a friendly introduction and ask your first question."""

        # Generate initial message
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "system",
                "content": system_prompt
            }],
            temperature=0.7,
            max_tokens=300
        )

        initial_message = completion.choices[0].message.content

        # Create session in database
        session_data = {
            "session_id": session_id,
            "notebook_id": request.notebook_id,
            "interview_type": request.interview_type,
            "difficulty": request.difficulty,
            "duration": request.duration,
            "messages": [{
                "role": "interviewer",
                "content": initial_message,
                "timestamp": datetime.utcnow()
            }],
            "status": "active",
            "created_at": datetime.utcnow()
        }

        await interview_sessions_collection.insert_one(session_data)

        return {
            "session_id": session_id,
            "initial_message": initial_message
        }

    except Exception as e:
        print(f"Error starting interview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interview/respond")
async def respond_to_interview(request: InterviewRespondRequest):
    """Send user response and get next question"""
    try:
        # Get session from database
        session = await interview_sessions_collection.find_one({"session_id": request.session_id})

        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")

        # Add user response to messages
        session["messages"].append({
            "role": "user",
            "content": request.user_response,
            "timestamp": datetime.utcnow()
        })

        # Build conversation history for context
        conversation_messages = []

        # System prompt
        if session["interview_type"] == "technical":
            context_prompt = "You are conducting a technical interview. Focus on coding, algorithms, and problem-solving."
        elif session["interview_type"] == "behavioral":
            context_prompt = "You are conducting a behavioral interview. Focus on experiences and soft skills."
        else:
            context_prompt = "You are conducting a comprehensive interview."

        conversation_messages.append({
            "role": "system",
            "content": f"""{context_prompt}
Continue the interview by:
1. Acknowledging the candidate's response briefly
2. Asking a relevant follow-up question or moving to a new topic
3. Keep your response concise (2-3 sentences max)
4. Be professional and encouraging"""
        })

        # Add conversation history (last 8 messages for context)
        for msg in session["messages"][-8:]:
            conversation_messages.append({
                "role": "assistant" if msg["role"] == "interviewer" else "user",
                "content": msg["content"]
            })

        # Generate next question
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation_messages,
            temperature=0.7,
            max_tokens=300
        )

        next_question = completion.choices[0].message.content

        # Add interviewer response to messages
        session["messages"].append({
            "role": "interviewer",
            "content": next_question,
            "timestamp": datetime.utcnow()
        })

        # Update session in database
        await interview_sessions_collection.update_one(
            {"session_id": request.session_id},
            {"$set": {"messages": session["messages"]}}
        )

        return {"next_question": next_question}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error responding to interview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interview/end")
async def end_interview(request: InterviewEndRequest):
    """End interview session and generate scoring"""
    try:
        # Get session from database
        session = await interview_sessions_collection.find_one({"session_id": request.session_id})

        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")

        # Build transcript for analysis
        transcript = []
        for msg in session["messages"]:
            role = "Interviewer" if msg["role"] == "interviewer" else "Candidate"
            transcript.append(f"{role}: {msg['content']}")

        transcript_text = "\n\n".join(transcript)

        # Generate scoring and feedback using AI
        scoring_prompt = f"""Analyze this job interview transcript and provide detailed scoring and feedback.

Interview Type: {session["interview_type"]}
Difficulty: {session["difficulty"]}

TRANSCRIPT:
{transcript_text}

Provide a JSON response with the following structure:
{{
    "overall_score": <0-100>,
    "communication_score": <0-100>,
    "technical_score": <0-100>,
    "problem_solving_score": <0-100>,
    "strengths": ["strength1", "strength2", "strength3"],
    "improvements": ["area1", "area2", "area3"],
    "recommendations": ["recommendation1", "recommendation2", "recommendation3"]
}}

Evaluate based on:
1. Communication: Clarity, articulation, professionalism
2. Technical Knowledge: Understanding of concepts, depth of answers
3. Problem Solving: Analytical thinking, approach to questions
4. Overall: Holistic performance assessment

Be constructive and specific in your feedback."""

        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": scoring_prompt
            }],
            temperature=0.5,
            max_tokens=1000
        )

        # Parse the scoring response
        scoring_text = completion.choices[0].message.content

        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', scoring_text)
        if json_match:
            scoring_data = json.loads(json_match.group())
        else:
            # Fallback scoring if parsing fails
            scoring_data = {
                "overall_score": 75,
                "communication_score": 75,
                "technical_score": 70,
                "problem_solving_score": 75,
                "strengths": ["Participated actively", "Showed engagement", "Attempted all questions"],
                "improvements": ["Practice more technical concepts", "Provide more detailed examples", "Work on time management"],
                "recommendations": ["Study common interview questions", "Practice mock interviews", "Review fundamental concepts"]
            }

        # Update session status
        await interview_sessions_collection.update_one(
            {"session_id": request.session_id},
            {
                "$set": {
                    "status": "completed",
                    "score": scoring_data,
                    "completed_at": datetime.utcnow()
                }
            }
        )

        return {
            "score": scoring_data,
            "feedback": {
                "strengths": scoring_data.get("strengths", []),
                "improvements": scoring_data.get("improvements", []),
                "recommendations": scoring_data.get("recommendations", [])
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error ending interview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ====================================
# Doomscroll Endpoints
# ====================================

class DoomscrollGenerateRequest(BaseModel):
    notebook_id: str
    count: int = 10

class DoomscrollLikeRequest(BaseModel):
    notebook_id: str
    card_id: str
    type: str
    title: str
    content: str
    example: Optional[str] = None
    color: str

class DoomscrollFolderCreate(BaseModel):
    notebook_id: str
    name: str

class DoomscrollMoveCardRequest(BaseModel):
    folder_id: Optional[str] = None

CARD_TYPES = ['fun_fact', 'mnemonic', 'key_concept', 'quote', 'summary', 'tip', 'question', 'definition']

def generate_card_with_llm(card_type: str, content: str, max_retries: int = 2) -> Optional[dict]:
    """Generate a doomscroll card using LLM"""

    prompts = {
        "fun_fact": """Extract ONE interesting, surprising, or little-known fact from this text. Make it engaging and memorable.

Text: {content}

Respond in this EXACT JSON format:
{{
  "title": "Did you know?",
  "content": "The interesting fact in 1-2 sentences",
  "example": "Optional real-world application or context"
}}""",

        "mnemonic": """Create a mnemonic device to help remember key information from this text.

Text: {content}

Respond in this EXACT JSON format:
{{
  "title": "Remember this!",
  "content": "The mnemonic device",
  "example": "Explanation of what each part means"
}}""",

        "key_concept": """Identify and explain ONE key concept from this text in simple, clear terms.

Text: {content}

Respond in this EXACT JSON format:
{{
  "title": "The concept name (2-5 words)",
  "content": "Clear explanation in 2-3 sentences",
  "example": "A concrete example or application"
}}""",

        "quote": """Extract or create ONE important, memorable quote or key statement from this text.

Text: {content}

Respond in this EXACT JSON format:
{{
  "title": "Key Insight",
  "content": "The quote or important statement",
  "example": "Why this is important or what it means"
}}""",

        "summary": """Create a brief, engaging summary of the main point from this text.

Text: {content}

Respond in this EXACT JSON format:
{{
  "title": "In a nutshell",
  "content": "Concise summary in 2-3 sentences",
  "example": "Optional key takeaway"
}}""",

        "tip": """Extract ONE practical tip or advice from this text.

Text: {content}

Respond in this EXACT JSON format:
{{
  "title": "Pro Tip",
  "content": "The practical tip or advice",
  "example": "How to apply it"
}}""",

        "question": """Create ONE thought-provoking question based on this text that encourages deeper thinking.

Text: {content}

Respond in this EXACT JSON format:
{{
  "title": "Think about this",
  "content": "The thought-provoking question",
  "example": "Why this question matters or what it reveals"
}}""",

        "definition": """Provide a clear definition of ONE important term or concept from this text.

Text: {content}

Respond in this EXACT JSON format:
{{
  "title": "Definition: [Term]",
  "content": "Clear, simple definition",
  "example": "Usage example or analogy"
}}"""
    }

    if card_type not in prompts:
        return None

    prompt = prompts[card_type].format(content=content[:2000])  # Limit content length

    for attempt in range(max_retries):
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a learning content creator. Always respond with valid JSON only, no markdown or extra text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )

            response_text = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = re.sub(r'^```json?\s*', '', response_text)
                response_text = re.sub(r'\s*```$', '', response_text)

            # Parse JSON response
            card_data = json.loads(response_text)

            # Validate required fields
            if "title" in card_data and "content" in card_data:
                return {
                    "type": card_type,
                    "title": card_data["title"][:100],  # Limit title length
                    "content": card_data["content"][:500],  # Limit content length
                    "example": card_data.get("example", "")[:300] if card_data.get("example") else None
                }

        except json.JSONDecodeError as e:
            print(f"JSON decode error for {card_type} (attempt {attempt + 1}): {e}")
            print(f"Response was: {response_text}")
            if attempt == max_retries - 1:
                return None
            continue
        except Exception as e:
            print(f"Error generating {card_type} card (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                return None
            continue

    return None

@app.post("/doomscroll/generate")
async def generate_doomscroll_cards(request: DoomscrollGenerateRequest):
    """Generate doomscroll cards from notebook documents"""
    try:
        # Get all documents for the notebook
        documents = await documents_collection.find({
            "notebook_id": request.notebook_id
        }).to_list(length=None)

        if not documents:
            return {
                "cards": [],
                "message": "No documents found for this notebook"
            }

        # Collect all chunks from all documents
        all_chunks = []
        for doc in documents:
            chunks = await ensure_document_chunks(doc)
            all_chunks.extend(chunks)

        if not all_chunks:
            return {
                "cards": [],
                "message": "No content found in documents"
            }

        # Shuffle chunks for variety
        random.shuffle(all_chunks)

        # Generate diverse card types
        cards = []
        card_type_index = 0
        chunk_index = 0
        attempts = 0
        max_attempts = request.count * 3  # Allow up to 3 attempts per card

        while len(cards) < request.count and attempts < max_attempts and chunk_index < len(all_chunks):
            card_type = CARD_TYPES[card_type_index % len(CARD_TYPES)]
            chunk = all_chunks[chunk_index]

            # Generate card
            card = generate_card_with_llm(card_type, chunk)

            if card:
                cards.append(card)
                card_type_index += 1  # Move to next card type for variety

            chunk_index += 1
            attempts += 1

        # If we couldn't generate enough cards, that's ok, return what we have
        if len(cards) == 0:
            return {
                "cards": [],
                "message": "Could not generate cards from the content"
            }

        return {"cards": cards}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating doomscroll cards: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/doomscroll/like")
async def like_doomscroll_card(request: DoomscrollLikeRequest):
    """Save a doomscroll card"""
    try:
        # Check if card is already saved
        existing = await saved_cards_collection.find_one({
            "notebook_id": request.notebook_id,
            "card_id": request.card_id
        })

        if existing:
            return {"success": True, "saved_card_id": str(existing["_id"]), "message": "Card already saved"}

        # Save the card
        card_doc = {
            "notebook_id": request.notebook_id,
            "card_id": request.card_id,
            "type": request.type,
            "title": request.title,
            "content": request.content,
            "example": request.example,
            "color": request.color,
            "folder_id": None,
            "created_at": datetime.utcnow()
        }

        result = await saved_cards_collection.insert_one(card_doc)

        return {
            "success": True,
            "saved_card_id": str(result.inserted_id)
        }

    except Exception as e:
        print(f"Error saving card: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/doomscroll/saved/{notebook_id}")
async def get_saved_cards(notebook_id: str):
    """Get all saved cards for a notebook"""
    try:
        cards = await saved_cards_collection.find({
            "notebook_id": notebook_id
        }).sort("created_at", -1).to_list(length=None)

        # Convert ObjectId to string
        for card in cards:
            card["id"] = str(card["_id"])
            del card["_id"]

        return {"cards": cards}

    except Exception as e:
        print(f"Error fetching saved cards: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/doomscroll/saved/{notebook_id}/{card_id}")
async def delete_saved_card(notebook_id: str, card_id: str):
    """Delete a saved card"""
    try:
        result = await saved_cards_collection.delete_one({
            "notebook_id": notebook_id,
            "card_id": card_id
        })

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Card not found")

        return {"success": True}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting saved card: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/doomscroll/folders")
async def create_folder(request: DoomscrollFolderCreate):
    """Create a folder for organizing cards"""
    try:
        folder_doc = {
            "notebook_id": request.notebook_id,
            "name": request.name,
            "created_at": datetime.utcnow()
        }

        result = await doomscroll_folders_collection.insert_one(folder_doc)

        folder_doc["id"] = str(result.inserted_id)
        del folder_doc["_id"]

        return {"folder": folder_doc}

    except Exception as e:
        print(f"Error creating folder: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/doomscroll/folders/{notebook_id}")
async def get_folders(notebook_id: str):
    """Get all folders for a notebook"""
    try:
        folders = await doomscroll_folders_collection.find({
            "notebook_id": notebook_id
        }).sort("created_at", 1).to_list(length=None)

        # Convert ObjectId to string
        for folder in folders:
            folder["id"] = str(folder["_id"])
            del folder["_id"]

        return {"folders": folders}

    except Exception as e:
        print(f"Error fetching folders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/doomscroll/folders/{folder_id}")
async def delete_folder(folder_id: str):
    """Delete a folder and move its cards to uncategorized"""
    try:
        # Move all cards in this folder to uncategorized (folder_id = None)
        await saved_cards_collection.update_many(
            {"folder_id": folder_id},
            {"$set": {"folder_id": None}}
        )

        # Delete the folder
        result = await doomscroll_folders_collection.delete_one({
            "_id": ObjectId(folder_id)
        })

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Folder not found")

        return {"success": True}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting folder: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/doomscroll/card/{card_id}/folder")
async def move_card_to_folder(card_id: str, request: DoomscrollMoveCardRequest):
    """Move a card to a folder"""
    try:
        # Update the card's folder_id
        result = await saved_cards_collection.update_one(
            {"_id": ObjectId(card_id)},
            {"$set": {"folder_id": request.folder_id}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Card not found")

        return {"success": True}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error moving card: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
