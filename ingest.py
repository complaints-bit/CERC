from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

import glob

def ingest_data():
    # check if pdfs exist
    pdf_files = glob.glob("*.pdf")
    if not pdf_files:
        print("❌ No PDF files found in the project folder.")
        return

    documents = []
    for pdf_file in pdf_files:
        print(f"📄 Loading {pdf_file}...")
        loader = PyPDFLoader(pdf_file)
        documents.extend(loader.load())
    
    print("✂️ Splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    
    print("🧠 Creating embeddings (FastEmbed BGE-Small)...")
    from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    
    print("💾 Saving vector index...")
    db = FAISS.from_documents(texts, embeddings)
    db.save_local("ngo_index")
    
    print("✅ Ingestion complete! 'ngo_index' created.")

if __name__ == "__main__":
    ingest_data()
