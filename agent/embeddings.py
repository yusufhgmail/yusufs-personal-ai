"""Embedding helper for vector-based memory search."""

from openai import OpenAI

from config.settings import get_settings


# Cache the client to avoid recreating it on every call
_client = None


def _get_client() -> OpenAI:
    """Get or create the OpenAI client."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """
    Get embedding vector for text using OpenAI's embedding API.
    
    Args:
        text: The text to embed
        model: The embedding model to use (default: text-embedding-3-small)
        
    Returns:
        List of floats representing the embedding vector (1536 dimensions)
    """
    client = _get_client()
    
    # Clean the text - remove excessive whitespace
    text = text.strip()
    if not text:
        # Return zero vector for empty text
        return [0.0] * 1536
    
    # Truncate very long text to avoid API limits (8191 tokens max for this model)
    # Rough estimate: 1 token ~= 4 chars, so 32000 chars should be safe
    if len(text) > 32000:
        text = text[:32000]
    
    response = client.embeddings.create(
        input=text,
        model=model
    )
    
    return response.data[0].embedding

