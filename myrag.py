import os
import sys
import logging

# Suppress pypdf logs for cleaner terminal output
logging.getLogger("pypdf").setLevel(logging.ERROR)

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# =========================================================
# CONFIGURATION
# =========================================================
DOCS_FOLDER = r"" # Paste your desired folder path here for the script to parse your document and feed it to the model.
VECTOR_DB_DIR = "./chroma_db"
LLM_MODEL = "llama3.2:1b"
EMBEDDING_MODEL = "nomic-embed-text"

# =========================================================
# PHASE 1: DOCUMENT INGESTION & INDEXING
# =========================================================
def load_and_index_documents():
    print(f"\n[1/3] Scanning directory: {DOCS_FOLDER}")
    
    loader_mapping = {
        ".pdf": PyPDFLoader,
        ".txt": TextLoader,
        ".md": TextLoader,
        ".c": TextLoader,
        ".cpp": TextLoader,
        ".h": TextLoader,
        ".py": TextLoader,
        ".json": TextLoader,
        ".js": TextLoader,
        ".jsx": TextLoader,
        ".css": TextLoader,
        ".html": TextLoader,
    }

    IGNORE_KEYWORDS = [
        "node_modules", ".git", "dist", "build", ".next", 
        ".cache", "coverage", "chroma_db", "package-lock.json", 
        "yarn.lock", "pnpm-lock.yaml", ".min.js"
    ]

    raw_documents = []

    for ext, loader_cls in loader_mapping.items():
        print(f" -> Loading '{ext}' files...")
        loader = DirectoryLoader(
            DOCS_FOLDER,
            glob=f"**/*{ext}",
            loader_cls=loader_cls,
            silent_errors=True,
            use_multithreading=False
        )
        loaded = loader.load()
        
       
        clean_docs = [
            doc for doc in loaded 
            if not any(ignore.lower() in doc.metadata.get('source', '').lower() for ignore in IGNORE_KEYWORDS)
        ]
        raw_documents.extend(clean_docs)

    print(f"\nSuccessfully read {len(raw_documents)} file sections.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(raw_documents)
    print(f"Generated {len(chunks)} searchable chunks.")

    if len(chunks) == 0:
        print("\n[ERROR] No valid text/code/PDF files were found to index.")
        sys.exit(1)

    print("\n[2/3] Generating vector embeddings (batched for i3 CPU)...")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    
    vector_db = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embeddings
    )

    batch_size = 500
    total_batches = (len(chunks) + batch_size - 1) // batch_size

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f" -> Processing batch {i // batch_size + 1} of {total_batches}...")
        vector_db.add_documents(batch)

    print("[SUCCESS] Vector database created and saved locally!")
    return vector_db

# =========================================================
# PHASE 2: INITIALIZE RETRIEVAL CHAIN
# =========================================================
def setup_rag_chain(vector_db):
    print("\n[3/3] Setting up local LLM and retrieval pipeline...")
    
    retriever = vector_db.as_retriever(search_kwargs={"k": 2})
    
    llm = OllamaLLM(
        model=LLM_MODEL,
        num_thread=4
    )

    system_prompt = (
        "You are an intelligent personal AI assistant with access to the user's local documents and code.\n"
        "Answer the user's question using ONLY the provided context excerpts.\n"
        "If you don't know the answer or the context doesn't contain it, say clearly that you couldn't find it in the files.\n"
        "Keep your response concise, accurate, and direct.\n\n"
        "Context:\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    def format_documents(documents):
        return "\n\n".join(document.page_content for document in documents)

    question_answer_chain = prompt | llm | StrOutputParser()

    # (x["input"]) extracts the raw string so retriever receives a string instead of a dict
    return (
        {
            "context": (lambda x: x["input"]) | retriever, 
            "input": lambda x: x["input"]
        }
        | RunnablePassthrough.assign(
            answer=(
                {
                    "context": lambda x: format_documents(x["context"]),
                    "input": lambda x: x["input"],
                }
                | question_answer_chain
            )
        )
    )

# =========================================================
# PHASE 3: INTERACTIVE CHAT LOOP
# =========================================================
def main():
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    
    if os.path.exists(VECTOR_DB_DIR) and os.listdir(VECTOR_DB_DIR):
        print("\n[INFO] Found existing ChromaDB database. Loading index...")
        vector_db = Chroma(
            persist_directory=VECTOR_DB_DIR,
            embedding_function=embeddings
        )
    else:
        vector_db = load_and_index_documents()

    rag_chain = setup_rag_chain(vector_db)

    print("\n=========================================================")
    print("      Personal Local File AI Search Ready!")
    print("      (Type 'exit' or 'quit' to close the program)")
    print("=========================================================\n")

    while True:
        try:
            user_query = input("\nAsk a question about your files: ").strip()
            
            if not user_query:
                continue
            if user_query.lower() in ["exit", "quit"]:
                print("Exiting application. Goodbye!")
                break

            print("\nSearching files and generating response...")
            response = rag_chain.invoke({"input": user_query})

            print("\n------------------- AI RESPONSE -------------------")
            print(response["answer"])

            print("\n------------------ SOURCES USED -------------------")
            used_sources = set(doc.metadata.get('source', 'Unknown File') for doc in response["context"])
            for source in used_sources:
                print(f"- {source}")
            print("---------------------------------------------------")

        except KeyboardInterrupt:
            print("\nSession interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\n[ERROR] An error occurred: {str(e)}")

if __name__ == "__main__":
    main()