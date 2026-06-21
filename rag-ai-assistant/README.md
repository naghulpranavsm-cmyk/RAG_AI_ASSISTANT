# RAG-Based AI Assistant

A complete Retrieval-Augmented Generation chatbot for answering questions from PDFs, research papers, company documents, and college notes.

## Tech Stack

| Component | Technology |
| --- | --- |
| Frontend | Streamlit |
| Backend | Python |
| LLM | Gemini or GPT |
| Embedding Model | Sentence Transformers |
| Vector DB | ChromaDB |
| Framework | LangChain |
| PDF Parsing | PyPDF2 |
| Deployment | Docker + AWS |

## Features

- Upload multiple PDF, TXT, or Markdown files.
- Extract PDF text with PyPDF2.
- Split documents into retrieval-friendly chunks with LangChain.
- Create local embeddings with Sentence Transformers.
- Store and retrieve document chunks from persistent ChromaDB.
- Ask questions through Gemini or OpenAI GPT.
- Show source citations from retrieved chunks.
- Run locally, in Docker, or on AWS ECS/App Runner/EC2.

## Project Structure

```text
rag-ai-assistant/
  app/
    config.py
    document_loader.py
    llm.py
    rag_chain.py
    vector_store.py
  deploy/
    aws.md
  streamlit_app.py
  requirements.txt
  Dockerfile
  docker-compose.yml
  .env.example
```

## Local Setup

Use Python 3.11 for this project. The Dockerfile already pins Python 3.11, and the Python AI package stack is most reliable on that runtime.

1. Create and activate a virtual environment.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Create your environment file.

```powershell
Copy-Item .env.example .env
```

4. Edit `.env` and set your API key.

Use Gemini:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_real_gemini_api_key_here
```

Use OpenAI:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
```

5. Start the app.

```powershell
python -m streamlit run streamlit_app.py
```

Open `http://localhost:8501`.

If `py -3.11` is not available, install Python 3.11 first or use Docker.

You can also run the helper script from the project folder:

```powershell
.\run_app.ps1
```

## Fix Gemini API Key Errors

If you see `API key not valid`, create a fresh key from [Google AI Studio](https://aistudio.google.com/app/apikey), then update `.env`:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=paste_your_real_key_here
```

Then stop Streamlit with `Ctrl+C` and start it again:

```powershell
python -m streamlit run streamlit_app.py
```

If you also have a Windows environment variable named `GOOGLE_API_KEY`, it takes precedence over `GEMINI_API_KEY`. Remove or update the old `GOOGLE_API_KEY` value if the app still uses the wrong key.

## Docker Setup

```powershell
Copy-Item .env.example .env
docker compose up --build
```

The app will be available at `http://localhost:8501`.

## How To Use

1. Upload one or more documents in the sidebar.
2. Click **Index Documents**.
3. Ask a question in the chat box.
4. Review the answer and the cited source chunks.

## Notes

- ChromaDB data is stored in `./chroma_db`.
- The embedding model runs locally, so the first startup can take time while Sentence Transformers downloads the model.
- Uploaded document contents are embedded locally, but retrieved context is sent to the selected LLM provider when answering.
- For scanned PDFs, add OCR before ingestion because PyPDF2 only extracts selectable text.
