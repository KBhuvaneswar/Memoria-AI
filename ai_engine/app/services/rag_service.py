import os
import pinecone

# from langchain_cohere import CohereEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from groq import Groq
from typing import List, Optional


class RAGService:
    def __init__(self):
        load_dotenv() 

        self.embedding_model = self._get_embedding_model()
        self.pinecone_index = self._get_pinecone_index()
        self.llm_client = self._get_llm_client()
        
    def _get_embedding_model(self):
        model_name = "all-MiniLM-L6-v2"
        return HuggingFaceEmbeddings(model_name=model_name)
        # return CohereEmbeddings(model="embed-english-v3.0", cohere_api_key=os.getenv("COHERE_API_KEY"))

    def _get_pinecone_index(self):
        api_key = os.getenv("PINECONE_API_KEY")

        pc = pinecone.Pinecone(api_key=api_key)
        index_name = os.getenv("PINECONE_INDEX")         
        
        if index_name not in pc.list_indexes().names():
            raise ValueError(f"Pinecone index '{index_name}' does not exist. Please ensure it's created.")
            
        return pc.Index(index_name)

    def _ingest_document(self, file, user_id: str, product_id: str):
        """
        Processes a single PDF document and upserts its chunks to Pinecone.
        """
        
        # 1. Read text from the PDF file
        import fitz 
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        if not text.strip():
            print("No text found in PDF. Ingestion skipped.")
            return 

        # 2. Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text)
        
        # 3. Embed the chunks
        embeddings = self.embedding_model.embed_documents(chunks)
        
        # 4. Prepare vectors for Pinecone
        vectors_to_upsert = []
        for i, chunk in enumerate(chunks):
            vector_id = f"{user_id}_{product_id}_chunk_{i}"
            vector = {
                "id": vector_id,
                "values": embeddings[i],
                "metadata": {
                    "text": chunk,
                    "user_id": user_id,
                    "product_id": product_id
                }
            }
            vectors_to_upsert.append(vector)
            
        # 5. Upsert to Pinecone
        self.pinecone_index.upsert(vectors=vectors_to_upsert) 

        return len(vectors_to_upsert)  # Return number of chunks ingested

    def _get_llm_client(self):
        api_key = os.getenv("GROQ_API_KEY")
        return Groq(api_key=api_key)

    def _generate_llm_response(self, query: str, context_chunks: list[str], history: Optional[list] = None) -> str:
        context = "\n---\n".join(context_chunks)
        
        history_str = ""
        if history:
            for msg in history:
                history_str += f"{msg.role}: {msg.content}\n"

        prompt = f"""
        You are a helpful AI assistant. Use the following context to answer the user's question.
        If the context doesn't contain the answer, state that you don't have enough information.
        Be concise and direct.

        PREVIOUS CHAT HISTORY:
        {history_str}

        CONTEXT FROM KNOWLEDGE BASE:
        {context}

        LATEST USER'S QUESTION:
        {query}

        YOUR ANSWER:
        """
        
        try:
            chat_completion = self.llm_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
            )
            return chat_completion.choices[0].message.content

        except Exception as e:
            return "Sorry, I had trouble generating a response."

    def search(self, query: str, user_id: str, product_id: str, history: Optional[list] = None) -> str:        
        query_embedding = self.embedding_model.embed_query(query)
        
        try:
            results = self.pinecone_index.query(
                vector=query_embedding,
                top_k=3,
                include_metadata=True,
                filter={"user_id": {"$eq": user_id}, "product_id": {"$eq": product_id}}
            )
            
            if not results['matches']:
                return "I couldn't find any relevant information for your query."

            context_chunks = [match['metadata']['text'] for match in results['matches']]
            
            final_answer = self._generate_llm_response(query=query, context_chunks=context_chunks, history=history)
            
            return final_answer

        except Exception as e:
            return "Sorry, an error occurred while searching."