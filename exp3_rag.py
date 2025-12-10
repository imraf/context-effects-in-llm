import time
import logging
import json
import random
import shutil
import os
from typing import Dict, Any
import config
from utils import OllamaClient, load_hebrew_articles, count_tokens

# LangChain imports
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class RagExperiment:
    def __init__(self, model: str):
        self.model = model
        self.client = OllamaClient(model)
        self.articles = load_hebrew_articles()
        # Use a shared directory for all models to avoid re-embedding
        self.persist_directory = os.path.join(config.BASE_DIR, "chroma_db_shared")

    def cleanup(self):
        if hasattr(self, 'vectorstore'):
            self.vectorstore = None
        # Do not delete the directory so it can be reused
        # if os.path.exists(self.persist_directory):
        #     shutil.rmtree(self.persist_directory)
        #     logger.info(f"Cleaned up RAG directory: {self.persist_directory}")

    def setup_rag(self):
        # Embed and Store
        # Note: Using nomic-embed-text for embeddings as it's standard with Ollama
        embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=config.OLLAMA_HOST)

        # Check if DB exists and reuse it
        if os.path.exists(self.persist_directory):
            logger.info(f"Loading existing RAG DB from {self.persist_directory}")
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory, 
                embedding_function=embeddings
            )
            # Basic check to ensure it's not empty (optional, but good for safety)
            # If it's empty or broken, we might want to rebuild, but for now assume it's good if it exists.
            return

        logger.info("Creating new RAG DB...")
            
        # Create documents
        docs = [Document(page_content=article, metadata={"source": f"doc_{i}"}) 
                for i, article in enumerate(self.articles)]
        
        # Split
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.EXP3_CHUNK_SIZE, 
            chunk_overlap=50
        )
        splits = text_splitter.split_documents(docs)
        
        self.vectorstore = Chroma.from_documents(
            documents=splits, 
            embedding=embeddings,
            persist_directory=self.persist_directory
        )
        logger.info(f"RAG Setup complete. Stored {len(splits)} chunks.")

    def run(self) -> Dict[str, Any]:
        try:
            return self._run_experiment()
        finally:
            self.cleanup()

    def _run_experiment(self) -> Dict[str, Any]:
        logger.info(f"Starting Experiment 3 (RAG vs Full) for {self.model}")
        
        if not self.articles:
            logger.error("No Hebrew articles found.")
            return {}

        self.setup_rag()
        
        # Pick a random document and a fact
        target_idx = random.randint(0, len(self.articles) - 1)
        target_doc = self.articles[target_idx]
        
        # Extract a snippet to ask about (e.g., a sentence from the middle)
        sentences = target_doc.split('.')
        if len(sentences) < 3:
            fact = target_doc[:100]
        else:
            fact = sentences[len(sentences)//2].strip()
            
        # Create a query
        # Since it's Hebrew, we need a Hebrew query. 
        # Assuming the model can handle "Summarize this: {fact}" or "Does the text mention {fact}?"
        # Let's use a simple retrieval check.
        query = f"האם הטקסט מזכיר את המשפט הבא: '{fact}'? השב בכן או לא."
        
        results = {}

        # 1. Full Context
        full_context = "\n\n".join(self.articles)
        start_time = time.time()
        full_response = self.client.generate(
            prompt=f"Context:\n{full_context}\n\nQuestion: {query}",
            temperature=0.1
        )
        full_latency = time.time() - start_time
        
        results['full_context'] = {
            "latency": full_latency,
            "response": full_response,
            "accuracy": 1.0 if "כן" in full_response or "Yes" in full_response else 0.0
        }
        logger.info(f"Full Context: Latency={full_latency:.2f}s")

        # 2. RAG
        start_time = time.time()
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": config.EXP3_RAG_K})
        relevant_docs = retriever.invoke(query)
        rag_context = "\n\n".join([d.page_content for d in relevant_docs])
        
        rag_response = self.client.generate(
            prompt=f"Context:\n{rag_context}\n\nQuestion: {query}",
            temperature=0.1
        )
        rag_latency = time.time() - start_time
        
        results['rag'] = {
            "latency": rag_latency,
            "response": rag_response,
            "accuracy": 1.0 if "כן" in rag_response or "Yes" in rag_response else 0.0
        }
        logger.info(f"RAG: Latency={rag_latency:.2f}s")

        return results

if __name__ == "__main__":
    exp = RagExperiment(config.MODELS[0])
    print(json.dumps(exp.run(), indent=2))
