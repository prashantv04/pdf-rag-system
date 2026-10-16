# ⚖️ SC Case Law AI (Legal RAG System)

A production-ready Retrieval-Augmented Generation (RAG) web application that acts as an AI Legal Assistant. It answers complex legal questions from massive PDF documents (like Supreme Court judgments) using semantic search, Qdrant Cloud, embeddings, and OpenRouter LLMs.

**🚀 Live App:** [https://sc-case-law-ai.streamlit.app](https://sc-case-law-ai.streamlit.app)

## ✨ Product Features

- **Interactive Web Interface:** Built with Streamlit for a seamless, chat-like user experience.
- **Dynamic Document Library:** Automatically queries the database to list available legal texts in the sidebar.
- **Cloud Vector Database:** Uses Qdrant Cloud for fast, scalable semantic similarity search.
- **Batched Ingestion Pipeline:** Safely processes and uploads thousands of embeddings (e.g., 13,000+ chunks) to the cloud in optimized batches to prevent timeouts.
- **Anti-Hallucination Guardrails:** Refuses to answer questions if the information is not explicitly found in the retrieved legal text, using a strict similarity threshold (`0.45`).
- **Exact Citations:** Displays exact source documents and page numbers for complete legal traceability.
- **In-App User Feedback Loop:** Native Google Forms integration in the sidebar to capture qualitative user feedback, track hallucination rates, and drive continuous product iteration.

## 🛠️ Tech Stack

- **Frontend/UI:** Streamlit
- **Vector Database:** Qdrant Cloud
- **Embeddings:** `sentence-transformers` (384-dimensional local model)
- **LLM:** OpenRouter (`openrouter/free`)
- **PDF Processing:** `pymupdf`

## 📂 Project Structure

```text
rag-pdf-qa/
│
├── app/
│   ├── main.py          # Streamlit web application & UI
│   ├── ingest.py        # Pipeline to process PDFs and push to Qdrant Cloud
│   ├── qdrant_db.py     # Cloud connection & batched vector insertion
│   ├── embeddings.py    # Embedding generation
│   ├── pdf_reader.py    # PDF text extraction
│   ├── chunker.py       # Text splitting logic
│   ├── rag.py           # Context and citation builder
│   └── llm.py           # OpenRouter LLM integration
│
├── data/                # Directory for local PDFs (Git ignored)
├── .env                 # API Keys and Cloud URLs
├── requirements.txt     # Linux-compatible dependencies
└── README.md
```

## ⚙️ Local Setup & Installation

**1. Create a Virtual Environment**
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
# source .venv/bin/activate  # Mac/Linux
```

**2. Install Dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure Environment Variables**
Create a `.env` file in the project root with your cloud credentials:
```env
OPENROUTER_API_KEY=your_openrouter_key
QDRANT_URL=https://your-cluster-url.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key
```

**4. Ingest Documents**
Place your legal PDFs in the `data/` folder and run the ingestion pipeline. This will chunk the PDFs, generate embeddings, and upload them to Qdrant Cloud in batches of 250.
```bash
python -m app.ingest
```

**5. Run the Web Application**
Start the Streamlit server to interact with your documents via the web UI.
```bash
streamlit run app/main.py
```

## 🧠 RAG Architecture

```text
[PDF Documents] ➔ PDF Reader ➔ Text Chunker ➔ Local Embeddings
                                                      │
                                                      ▼
[Streamlit Web UI] ➔ User Question                [Qdrant Cloud]
        │                   │                         │
        ▼                   ▼                         ▼
   Final Answer   🡨    RAG Context  🡨  Similarity Search (Threshold 0.45)
  + Citations               │                         
                            ▼
                     OpenRouter LLM
```

## 🎯 Project Goal: From Discovery to Adoption

This project demonstrates the complete lifecycle of an AI product:
1. **Discovery:** Identifying the pain point of reading 100+ page court judgments to find specific legal precedents.
2. **Build:** Creating a robust, anti-hallucinating RAG backend with precise citations and strict relevance filtering (`0.45` threshold).
3. **Adoption:** Moving from a local CLI tool to a cloud-hosted, user-friendly web application designed for non-technical end users (law students and professionals).

## 📄 License
The MIT License applies to the project source code. Documents placed in the `data/` directory are subject to their respective copyright and usage terms.