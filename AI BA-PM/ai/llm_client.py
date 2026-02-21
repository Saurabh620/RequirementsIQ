"""
AI Layer: Universal LLM Client Factory
Supports OpenAI and Groq (free tier) with the same interface.
Switch provider via AI_PROVIDER in .env: 'openai' or 'groq'
"""
from config import settings


def get_llm_client():
    """
    Returns an OpenAI-compatible client.
    - 'groq'    → Groq (Llama 3.3 70B)
    - 'mistral' → Mistral (Mistral Large/Small) 
    - 'openai'  → OpenAI (GPT-4o)
    """
    provider = settings.ai_provider.lower()

    if provider == "groq":
        try:
            from groq import Groq
            return Groq(api_key=settings.groq_api_key)
        except ImportError:
            raise RuntimeError("groq package not installed. Run: pip install groq")

    elif provider == "mistral":
        # Mistral provides an OpenAI-compatible endpoint
        from openai import OpenAI
        return OpenAI(
            base_url="https://api.mistral.ai/v1",
            api_key=settings.mistral_api_key
        )

    else:  # default: openai
        from openai import OpenAI
        return OpenAI(api_key=settings.openai_api_key)


def get_model_name() -> str:
    """Returns the active model name for the current provider."""
    provider = settings.ai_provider.lower()
    if provider == "groq":
        return settings.groq_model
    elif provider == "mistral":
        return settings.mistral_model
    return settings.openai_model
