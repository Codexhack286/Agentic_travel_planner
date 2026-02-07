"""
RAG-based Travel Knowledge Retriever.
"""
import logging
from typing import List, Dict, Any, Optional

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


class TravelRetriever:
    """
    Retrieval-Augmented Generation system for travel knowledge.
    
    Manages:
    - Vector store of travel information
    - Embedding-based retrieval
    - Context filtering and ranking
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=config.get("embedding_model", "text-embedding-3-small")
        )
        
        # Initialize or load vector store
        self.vector_store = self._initialize_vector_store()
        
        # Text splitter for document processing
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.get("chunk_size", 1000),
            chunk_overlap=config.get("chunk_overlap", 200),
            length_function=len,
        )
        
        logger.info("Travel Retriever initialized")
    
    def _initialize_vector_store(self) -> Chroma:
        """Initialize or load the vector store."""
        
        persist_directory = self.config.get(
            "chroma_persist_directory",
            "./data/vector_db"
        )
        collection_name = self.config.get("collection_name", "travel_knowledge")
        
        try:
            # Try to load existing vector store
            vector_store = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=persist_directory
            )
            logger.info(f"Loaded existing vector store from {persist_directory}")
            
        except Exception as e:
            logger.warning(f"Could not load existing vector store: {e}")
            logger.info("Creating new vector store")
            
            # Create new vector store
            vector_store = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=persist_directory
            )
        
        return vector_store
    
    async def retrieve(
        self,
        query: str,
        k: int = None,
        filters: Dict[str, Any] = None
    ) -> List[Document]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            filters: Metadata filters (destination, category, etc.)
        
        Returns:
            List of relevant documents
        """
        k = k or self.config.get("top_k_results", 5)
        
        logger.info(f"Retrieving documents for query: {query[:50]}...")
        
        # Build search kwargs
        search_kwargs = {"k": k}
        if filters:
            search_kwargs["filter"] = self._build_metadata_filter(filters)
        
        # Perform similarity search
        docs = await self.vector_store.asimilarity_search(
            query,
            **search_kwargs
        )
        
        logger.info(f"Retrieved {len(docs)} documents")
        return docs
    
    async def retrieve_with_scores(
        self,
        query: str,
        k: int = None,
        score_threshold: float = None
    ) -> List[tuple[Document, float]]:
        """
        Retrieve documents with similarity scores.
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            score_threshold: Minimum similarity score
        
        Returns:
            List of (document, score) tuples
        """
        k = k or self.config.get("top_k_results", 5)
        score_threshold = score_threshold or self.config.get("similarity_threshold", 0.7)
        
        logger.info(f"Retrieving documents with scores for: {query[:50]}...")
        
        # Perform similarity search with scores
        docs_and_scores = await self.vector_store.asimilarity_search_with_relevance_scores(
            query,
            k=k,
            score_threshold=score_threshold
        )
        
        logger.info(f"Retrieved {len(docs_and_scores)} documents above threshold")
        return docs_and_scores
    
    def add_documents(
        self,
        documents: List[Document],
        batch_size: int = 100
    ) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of documents to add
            batch_size: Batch size for adding documents
        
        Returns:
            List of document IDs
        """
        logger.info(f"Adding {len(documents)} documents to vector store")
        
        # Process documents in batches
        ids = []
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_ids = self.vector_store.add_documents(batch)
            ids.extend(batch_ids)
            
            logger.debug(f"Added batch {i // batch_size + 1}")
        
        logger.info(f"Added {len(ids)} documents successfully")
        return ids
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Add raw texts to the vector store.
        
        Args:
            texts: List of text strings
            metadatas: Optional list of metadata dicts
        
        Returns:
            List of document IDs
        """
        logger.info(f"Adding {len(texts)} texts to vector store")
        
        # Split texts into chunks
        chunks = []
        chunk_metadatas = []
        
        for i, text in enumerate(texts):
            text_chunks = self.text_splitter.split_text(text)
            chunks.extend(text_chunks)
            
            # Replicate metadata for each chunk
            if metadatas and i < len(metadatas):
                chunk_metadatas.extend([metadatas[i]] * len(text_chunks))
        
        # Add to vector store
        ids = self.vector_store.add_texts(
            texts=chunks,
            metadatas=chunk_metadatas if chunk_metadatas else None
        )
        
        logger.info(f"Added {len(ids)} text chunks")
        return ids
    
    def delete_documents(self, ids: List[str]) -> None:
        """
        Delete documents from the vector store.
        
        Args:
            ids: List of document IDs to delete
        """
        logger.info(f"Deleting {len(ids)} documents")
        self.vector_store.delete(ids=ids)
    
    def _build_metadata_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build metadata filter for vector store queries.
        
        Args:
            filters: Filter criteria
        
        Returns:
            Formatted filter dict
        """
        # Convert filters to vector store format
        # This depends on your vector store backend
        
        formatted_filter = {}
        
        if "destination" in filters and filters["destination"]:
            formatted_filter["destination"] = filters["destination"]
        
        if "category" in filters and filters["category"]:
            formatted_filter["category"] = filters["category"]
        
        if "interests" in filters and filters["interests"]:
            # Handle list of interests
            formatted_filter["interests"] = {"$in": filters["interests"]}
        
        return formatted_filter
    
    async def hybrid_search(
        self,
        query: str,
        k: int = 5,
        alpha: float = 0.5
    ) -> List[Document]:
        """
        Perform hybrid search combining semantic and keyword search.
        
        Args:
            query: Search query
            k: Number of results
            alpha: Weight between semantic (1.0) and keyword (0.0) search
        
        Returns:
            List of documents
        """
        # TODO: Implement hybrid search
        # This would combine vector similarity with keyword matching
        
        logger.info(f"Performing hybrid search: {query[:50]}...")
        return await self.retrieve(query, k=k)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        
        try:
            collection = self.vector_store._collection
            count = collection.count()
            
            return {
                "total_documents": count,
                "collection_name": self.vector_store._collection.name,
                "embedding_model": self.config.get("embedding_model")
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
