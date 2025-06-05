from typing import List, Optional
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import numpy as np
from .document_processor import SECDocumentProcessor

class QASystem:
    def __init__(self):
        self.qa_model = pipeline('question-answering', model='deepset/roberta-base-squad2')
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunk_size = 1000
        self.overlap = 200
        self.confidence_threshold = 0.1

    def split_into_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if not text:
            return []
            
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk = ' '.join(words[i:i + self.chunk_size])
            chunks.append(chunk)
            
        return chunks

    def get_most_relevant_chunk(self, chunks: List[str], question: str) -> Optional[str]:
        """Find the most semantically relevant chunk for the question."""
        if not chunks:
            return None
            
        # Encode question and chunks
        question_embedding = self.sentence_model.encode([question])[0]
        chunk_embeddings = self.sentence_model.encode(chunks)
        
        # Calculate similarities
        similarities = np.dot(chunk_embeddings, question_embedding)
        most_relevant_idx = np.argmax(similarities)
        
        return chunks[most_relevant_idx]

    def answer_question(self, relevant_section: str, question: str) -> Optional[str]:
        """Answer a question using the relevant section."""
        try:
            if not relevant_section or not question:
                print("Warning: Missing input for question answering")
                return None
                
            # Split into chunks and find most relevant
            chunks = self.split_into_chunks(relevant_section)
            if not chunks:
                print("Warning: No text chunks generated")
                return None
                
            context = self.get_most_relevant_chunk(chunks, question)
            if not context:
                print("Warning: Could not find relevant context")
                return None
            
            # Get answer from model
            result = self.qa_model(question=question, context=context)
            
            # Check confidence
            if result['score'] < self.confidence_threshold:
                print(f"Warning: Low confidence answer (score: {result['score']:.2f})")
                return None
                
            return result['answer']
            
        except Exception as e:
            print(f"Error answering question: {e}")
            return None

qa_system = QASystem()

def answer_question(context: Optional[str], question: str) -> Optional[str]:
    """Interface function to answer questions."""
    if not context:
        return "Could not find relevant context to answer the question."
    if not question:
        return "Please provide a question."
        
    answer = qa_system.answer_question(context, question)
    if not answer:
        return "Could not find a confident answer to your question."
        
    return answer