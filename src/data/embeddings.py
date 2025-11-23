"""Embedding generation using sentence transformers for news articles."""

from typing import List, Optional
import torch
from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingError(Exception):
    """Custom exception for embedding generation errors."""
    pass


class EmbeddingGenerator:
    """Generates embeddings for text using sentence transformers."""
    
    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5",
        device: Optional[str] = None
    ):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence transformer model
                       Default: BAAI/bge-small-en-v1.5 (384 dimensions, lightweight)
            device: Device to use ('cuda', 'mps', 'cpu'). Auto-detected if None.
        """
        self.model_name = model_name
        
        # Auto-detect device if not specified
        if device is None:
            if torch.cuda.is_available():
                self.device = 'cuda'
            elif torch.backends.mps.is_available():
                self.device = 'mps'
            else:
                self.device = 'cpu'
        else:
            self.device = device
        
        print(f"🧠 Loading embedding model: {model_name}")
        print(f"🖥️  Using device: {self.device}")
        
        try:
            self.model = SentenceTransformer(model_name, device=self.device)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            print(f"✓ Model loaded. Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            raise EmbeddingError(f"Failed to load model '{model_name}': {str(e)}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        if not text or not text.strip():
            raise EmbeddingError("Cannot generate embedding for empty text")
        
        try:
            # Generate embedding
            embedding = self.model.encode(
                text,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            # Convert to list and ensure it's the right type
            return embedding.tolist()
            
        except Exception as e:
            raise EmbeddingError(f"Failed to generate embedding: {str(e)}")
    
    def batch_generate(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.
        
        Args:
            texts: List of input texts
            batch_size: Number of texts to process at once
            show_progress: Whether to show progress bar
            
        Returns:
            List of embedding vectors
            
        Raises:
            EmbeddingError: If batch generation fails
        """
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [text for text in texts if text and text.strip()]
        
        if not valid_texts:
            raise EmbeddingError("No valid texts to embed")
        
        try:
            # Generate embeddings in batch
            embeddings = self.model.encode(
                valid_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=show_progress
            )
            
            # Convert to list of lists
            return embeddings.tolist()
            
        except Exception as e:
            raise EmbeddingError(f"Failed to generate batch embeddings: {str(e)}")
    
    def compute_similarity(
        self,
        text1: str,
        text2: str
    ) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between -1 and 1 (higher is more similar)
        """
        emb1 = np.array(self.generate_embedding(text1))
        emb2 = np.array(self.generate_embedding(text2))
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        return float(similarity)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        return self.embedding_dim
    
    def __repr__(self) -> str:
        return f"EmbeddingGenerator(model='{self.model_name}', device='{self.device}', dim={self.embedding_dim})"
