# PDF RAG System

A Retrieval-Augmented Generation (RAG) system that answers questions from PDF documents using semantic search, Qdrant vector database, embeddings, and OpenRouter LLMs

---

## Features

- Read PDF documents
- Split PDF pages into text chunks
- Generate embeddings using a 384-dimensional embedding model
- Store document chunks and embeddings in Qdrant
- Perform semantic similarity search
- Apply a relevance threshold to retrieved results
- Build context from retrieved document chunks
- Generate answers using OpenRouter
- Use the free `openrouter/free` model
- Display document and page citations
- Refuse to answer when relevant information is not found
- Support multiple PDF files in the `data` directory

---

## Project Structure

```text
rag-pdf-qa/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── ingest.py
│   ├── embeddings.py
│   ├── pdf_reader.py
│   ├── chunker.py
│   ├── qdrant_db.py
│   ├── rag.py
│   └── llm.py
│
├── data/
│   └── # PDF not included
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Requirements

- Python 3.10 or later
- Qdrant running locally
- An OpenRouter API key
- Internet access for downloading the embedding model and communicating with OpenRouter

---

## 1. Create a Virtual Environment

From the project root:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

The terminal should show:

```text
(.venv)
```

---

## 2. Install Dependencies

Install the packages listed in `requirements.txt`:

```powershell
pip install -r requirements.txt
```

---

## 3. Configure the API Key

Create a `.env` file in the project root.

```env
OPENROUTER_API_KEY=your_actual_api_key_here
```

Do **not** commit the `.env` file to Git.

The repository contains `.env.example` only as a template:

```env
OPENROUTER_API_KEY=
```

---

## 4. Start Qdrant

The application uses Qdrant at:

```text
http://localhost:6333
```

Make sure Qdrant is running before starting ingestion or asking questions.

---

## 5. Add PDF Documents

Place PDF files inside:

```text
data/
```

The application can process multiple `.pdf` files placed in the `data` directory.

---

## 6. Ingest the PDF

Run the ingestion script from the project root:

```powershell
python -m app.ingest
```

The ingestion process:

1. Finds PDF files in `data/`
2. Reads the PDF pages
3. Splits the pages into chunks
4. Generates embeddings
5. Connects to Qdrant
6. Creates a fresh `documents` collection
7. Inserts the chunks and embeddings

A successful ingestion looks similar to:

```text
Reading PDF: 28_L_Chandra_Kumar_vs_Union_of_India_and_Ors_p3508-p3511.pdf
Total pages: 4
Chunks from 28_L_Chandra_Kumar_vs_Union_of_India_and_Ors_p3508-p3511.pdf: 13

Total chunks: 13

Loading embedding model...
Embedding 13 chunks...
Embedding count: 13
Embedding dimensions: 384

Deleting existing Qdrant collection: documents
Created fresh Qdrant collection: documents
Inserted 13 chunks into Qdrant.

Ingestion completed successfully.
```

---

## 7. Run the Question Answering Application

After ingestion, run:

```powershell
python -m app.main
```

The application will ask:

```text
Ask a question:
```

Enter a question related to the supplied document.

For example:

```text
What did the Supreme Court say about tribunals?
```

The application performs the following steps:

```text
User Question
      ↓
Question Embedding
      ↓
Qdrant Semantic Search
      ↓
Relevant Document Chunks
      ↓
Context Construction
      ↓
OpenRouter LLM
      ↓
Answer + Sources
```

---

## 8. Relevance Filtering

The application uses a Qdrant similarity threshold:

```python
RELEVANCE_THRESHOLD = 0.20
```
Retrieved results below this threshold are excluded from the context.

If no results meet the threshold, the application returns:

The information is not available in the supplied documents.

The answer-generation prompt also instructs the LLM to refuse questions that are not supported by the retrieved document context. This provides an additional safeguard against answers based on the model's general knowledge.

---

## 9. Answer Generation

The application uses OpenRouter through the OpenAI-compatible client.

The configured model is:

```python
MODEL_NAME = "openrouter/free"
```

The LLM is instructed to:

- use only the supplied document context
- not use outside knowledge
- not guess
- not fabricate information
- return the unavailable-document message when the context does not support an answer

---

## 10. Example Question

### Question

```text
Are tribunals equal to High Courts?
```

### Example Answer

```text
Based on the provided document context, tribunals are not equal to High Courts.

The document states that tribunals cannot claim the status or parity of High Courts and cannot act as substitutes for them.
```

The application also displays the retrieved document sources and page numbers.

---

## 11. Example Source Output

The application displays sources in this format:

```text
--- Sources ---

Source 1
Document: 28_L_Chandra_Kumar_vs_Union_of_India_and_Ors_p3508-p3511.pdf
Page: 3
Snippet: ...
```

This provides traceability between the generated answer and the retrieved PDF content.

---

## 12. Test Cases

The RAG system was tested using both relevant and irrelevant questions.

### Test 1 — Relevant Question

```text
What did the Supreme Court say about tribunals?
```

Expected behavior:

- Relevant chunks are retrieved from Qdrant
- The LLM generates an answer using the supplied document context
- Document and page sources are displayed

### Test 2 — Irrelevant Question

```text
What is the capital of France?
```

Expected behavior:

```text
The information is not available in the supplied documents.
```

The system should not answer using the model's general knowledge.

### Test 3 — Tribunal Equality

```text
Are tribunals equal to High Courts?
```

Expected behavior:

The system explains from the supplied context that tribunals cannot claim the status or parity of High Courts.

### Test 4 — Tribunal Qualifications

```text
What qualifications were emphasized for members of tribunals?
```

Expected behavior:

The system identifies qualifications emphasized in the retrieved context, including:

- adequate legal expertise
- judicial experience
- legal training

### Test 5 — Source Traceability

For retrieved results, the application displays:

- document name
- page number
- retrieved text snippet

This allows the user to trace the answer back to the relevant PDF content.

---

## 13. Security

The real API key must remain in:

```text
.env
```

The following files/directories should not be committed:

```text
.env
.venv/
__pycache__/
```

The `.env.example` file contains only:

```env
OPENROUTER_API_KEY=
```

Never replace the empty value in `.env.example` with a real API key.

---

## 14. Important Notes

### Embedding model

The application currently uses a 384-dimensional embedding model.

The Qdrant collection is therefore configured with:

```python
VECTOR_SIZE = 384
```

The embedding model and Qdrant vector size must remain compatible.

### Qdrant collection

The application uses:

```text
documents
```

as the Qdrant collection name.

The ingestion process resets the collection before inserting the current document chunks. This helps prevent old PDF data from remaining in the database when documents are replaced.

### Multiple PDFs

Additional PDFs can later be placed in:

```text
data/
```

and processed by the ingestion pipeline.

For the current assignment, the system is being tested with the supplied `L. Chandra Kumar` PDF.

---

## 15. Typical Workflow

For a fresh set of documents:

```powershell
# Activate environment
.venv\Scripts\Activate.ps1

# Start Qdrant

# Place PDF files in data/

# Ingest documents
python -m app.ingest

# Start question answering
python -m app.main
```

Then ask questions about the supplied documents.

---

## 16. RAG Architecture

```text
                    PDF Documents
                         │
                         ▼
                    PDF Reader
                         │
                         ▼
                     Chunking
                         │
                         ▼
                   Embeddings
                         │
                         ▼
                       Qdrant
                  Vector Database
                         │
                         │
User Question ──► Question Embedding
                         │
                         ▼
                  Similarity Search
                         │
                         ▼
                 Relevant Chunks
                         │
                         ▼
                   RAG Context
                         │
                         ▼
                 OpenRouter LLM
                         │
                         ▼
                  Final Answer
                         │
                         ▼
                  Source Citations
```

---

## 17. Project Goal

The goal of this project is to demonstrate a complete PDF-based Retrieval-Augmented Generation pipeline:

**PDF → chunks → embeddings → vector database → retrieval → context → LLM → answer with sources**

The system is designed to ground its answers in the supplied documents rather than relying on the model's general knowledge.

## 18. MIT LICENSE

```markdown
The MIT License applies to the project source code and other original materials authored by the project contributors.
Documents and other materials provided separately for the assignment, including files that may be placed in the `data/` directory, are not necessarily covered by the MIT License and may be subject to their respective copyright, license, and usage terms.
Users are responsible for complying with the applicable terms for such materials.