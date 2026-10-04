# 🔍 MyRAG — Local AI Document Search

> A lightweight, fully offline RAG (Retrieval-Augmented Generation) app that lets you chat with your own documents using local AI models — no cloud, no API keys, no data leaving your machine.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-green?logo=chainlink&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-purple)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20DB-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## What is MyRAG?

**MyRAG** is a command-line tool that indexes a folder of your local files — documents, code, PDFs, notes — and lets you ask natural-language questions about them. It uses:

- **[Ollama](https://ollama.com/)** to run a local LLM and embedding model entirely on your machine
- **[ChromaDB](https://www.trychroma.com/)** as a local vector database to store and search document embeddings
- **[LangChain](https://www.langchain.com/)** to wire together the retrieval and generation pipeline

Everything runs **100% locally and offline** — your documents never leave your computer.

### How it works

```
Your Files → Chunking → Vector Embeddings → ChromaDB
                                                 ↓
Your Question → Embedding → Similarity Search → Top Chunks → Local LLM → Answer
```

1. **Ingestion** — Scans your target folder and loads supported file types
2. **Chunking** — Splits large documents into overlapping chunks for better retrieval accuracy
3. **Indexing** — Converts chunks into vector embeddings and stores them in a local ChromaDB database
4. **Chat** — You ask a question; the app finds the most relevant chunks and feeds them to the LLM as context

---

##Features

- **Fully local & private** — no cloud, no API keys required
- **Multi-format support** — PDFs, plain text, Markdown, and common code files
- **Persistent index** — ChromaDB is saved to disk; subsequent runs skip re-indexing
- **Source citations** — every answer shows which files it was pulled from
- **Batch embedding** — chunks are processed in batches, suitable for lower-end hardware
- **Smart filtering** — automatically ignores `node_modules`, `.git`, `dist`, build artifacts, and lock files

---

## Supported File Types

| Category | Extensions |
|----------|-----------|
| Documents | `.pdf`, `.txt`, `.md` |
| Python | `.py` |
| Web | `.js`, `.jsx`, `.html`, `.css` |
| Systems / C | `.c`, `.cpp`, `.h` |
| Data | `.json` |

---

## Prerequisites

### 1. Python 3.10+

Download from [python.org](https://www.python.org/downloads/). Verify your version:

```bash
python --version
```

### 2. Ollama

Ollama lets you run LLMs locally. Download and install it from [ollama.com](https://ollama.com/).

Once installed, pull the two required models:

```bash
# The language model (used for generating answers)
ollama pull llama3.2:1b

# The embedding model (used for indexing and searching documents)
ollama pull nomic-embed-text
```

> **Note:** Make sure Ollama is running in the background before launching MyRAG. You can start it with `ollama serve`.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/myrag.git
cd myrag
```

### 2. (Recommended) Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install langchain langchain-community langchain-chroma langchain-core langchain-ollama pypdf
```

---

## Configuration

Open `myrag.py` and update the configuration block near the top of the file:

```python
# =========================================================
# CONFIGURATION
# =========================================================
DOCS_FOLDER     = r""                  # ← Paste the path to your documents folder here
VECTOR_DB_DIR   = "./chroma_db"        # Where the local vector database is stored
LLM_MODEL       = "llama3.2:1b"        # Ollama model used for generating answers
EMBEDDING_MODEL = "nomic-embed-text"   # Ollama model used for embeddings
```

#### Example (Windows)

```python
DOCS_FOLDER = r"C:\Users\YourName\Documents\ProjectNotes"
```

#### Example (macOS / Linux)

```python
DOCS_FOLDER = "/home/yourname/documents/project-notes"
```

> **Tip:** Use a raw string (`r"..."`) on Windows to avoid issues with backslash escape sequences.

---

## Running the App

From the project directory:

```bash
python myrag.py
```

#### What happens on first run

```
[1/3] Scanning directory: C:\...\YourDocs
 -> Loading '.pdf' files...
 -> Loading '.py' files...
 ...
[2/3] Generating vector embeddings...
[3/3] Setting up local LLM and retrieval pipeline...

=========================================================
      Personal Local File AI Search Ready!
      (Type 'exit' or 'quit' to close the program)
=========================================================

Ask a question about your files: _
```

On **subsequent runs**, the app detects the existing ChromaDB index and skips the ingestion step entirely, starting up much faster.

#### Example session

```text
Ask a question about your files: What does the authentication flow do?

Searching files and generating response...

------------------- AI RESPONSE -------------------
The authentication flow validates the user's token by checking it against
the database. If the token is expired, it returns a 401 response...

------------------ SOURCES USED -------------------
- C:\...\auth.py
- C:\...\README.md
---------------------------------------------------
```

Type `exit` or `quit` to close the program.

---

## Project Structure

```
myrag/
├── myrag.py          # Main application script
├── chroma_db/        # Auto-generated local vector database (gitignored)
└── README.md
```

> The `chroma_db/` folder is generated automatically on first run. Add it to your `.gitignore` to avoid committing it to version control.

---






## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Connection refused` error on startup | Make sure Ollama is running: `ollama serve` |
| `model not found` error | Pull the required models: `ollama pull llama3.2:1b` and `ollama pull nomic-embed-text` |
| No files indexed | Check that `DOCS_FOLDER` path is correct and contains supported file types |
| Want to re-index after adding new files | Delete the `chroma_db/` folder and re-run the script |
| Slow on first run | Normal — embedding large document sets takes time depending on your hardware |

---

## Roadmap / Ideas

- [ ] CLI argument support for `DOCS_FOLDER` (no need to edit the script)
- [ ] `requirements.txt` / `pyproject.toml` for easier dependency management
- [ ] Support for `.docx` (Microsoft Word) files
- [ ] Web UI (Gradio or Streamlit frontend)
- [ ] Incremental indexing (only re-embed changed files)
- [ ] Multi-model support via config file

---



## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

- [LangChain](https://www.langchain.com/) — the backbone retrieval and LLM orchestration framework
- [Ollama](https://ollama.com/) — for making local LLM inference easy
- [ChromaDB](https://www.trychroma.com/) — for the lightweight local vector store
- [nomic-embed-text](https://huggingface.co/nomic-ai/nomic-embed-text-v1) — the embedding model used for document indexing
