"""Multi-Provider LLM Configuration

Centralized configuration for accessing multiple AI model providers:
- OpenAI (GPT-4, GPT-3.5, GPT-4o)
- Anthropic (Claude 3 Opus, Sonnet, Haiku)
- Google (Gemini Pro, Gemini Ultra, Gemma)
- Ollama (Local models: llama2, mistral, codellama)
- Cohere (Command, Command-Light)
- Mistral AI (Mistral Large, Medium, Small)
- Meta (Llama 2, Llama 3)
- Additional providers as needed

Provides unified interface for model selection across cost tiers.

Version: 1.0.0
"""

import os
import logging
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Supported AI model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    COHERE = "cohere"
    MISTRAL = "mistral"
    META = "meta"


class CostTier(Enum):
    """Model cost/performance tiers."""
    ECONOMIC = "economic"          # Lowest cost, fastest, good for simple tasks
    BALANCED = "balanced"          # Balance of cost and performance
    HIGH_PERFORMANCE = "high-performance"  # Best performance, higher cost
    ULTRA_PERFORMANCE = "ultra-performance" # Premium models (GPT-4o, Claude Opus)


# Model Configuration Matrix
# Format: {provider: {tier: model_name}}
MODEL_MATRIX = {
    ModelProvider.OPENAI: {
        CostTier.ECONOMIC: "gpt-3.5-turbo",
        CostTier.BALANCED: "gpt-4",
        CostTier.HIGH_PERFORMANCE: "gpt-4-turbo",
        CostTier.ULTRA_PERFORMANCE: "gpt-4o"
    },
    ModelProvider.ANTHROPIC: {
        CostTier.ECONOMIC: "claude-3-haiku-20240307",
        CostTier.BALANCED: "claude-3-sonnet-20240229",
        CostTier.HIGH_PERFORMANCE: "claude-3-opus-20240229",
        CostTier.ULTRA_PERFORMANCE: "claude-3-opus-20240229"
    },
    ModelProvider.GOOGLE: {
        CostTier.ECONOMIC: "gemini-pro",
        CostTier.BALANCED: "gemini-pro-1.5",
        CostTier.HIGH_PERFORMANCE: "gemini-ultra",
        CostTier.ULTRA_PERFORMANCE: "gemini-ultra-1.5"
    },
    ModelProvider.OLLAMA: {
        CostTier.ECONOMIC: "llama2:7b",
        CostTier.BALANCED: "mistral:7b",
        CostTier.HIGH_PERFORMANCE: "llama2:13b",
        CostTier.ULTRA_PERFORMANCE: "llama2:70b"
    },
    ModelProvider.COHERE: {
        CostTier.ECONOMIC: "command-light",
        CostTier.BALANCED: "command",
        CostTier.HIGH_PERFORMANCE: "command-nightly",
        CostTier.ULTRA_PERFORMANCE: "command-r-plus"
    },
    ModelProvider.MISTRAL: {
        CostTier.ECONOMIC: "mistral-small-latest",
        CostTier.BALANCED: "mistral-medium-latest",
        CostTier.HIGH_PERFORMANCE: "mistral-large-latest",
        CostTier.ULTRA_PERFORMANCE: "mistral-large-latest"
    },
    ModelProvider.META: {
        CostTier.ECONOMIC: "llama-2-7b",
        CostTier.BALANCED: "llama-2-13b",
        CostTier.HIGH_PERFORMANCE: "llama-2-70b",
        CostTier.ULTRA_PERFORMANCE: "llama-3-70b"
    }
}

# Provider API endpoints
PROVIDER_ENDPOINTS = {
    ModelProvider.OPENAI: "https://api.openai.com/v1",
    ModelProvider.ANTHROPIC: "https://api.anthropic.com/v1",
    ModelProvider.GOOGLE: "https://generativelanguage.googleapis.com/v1beta",
    ModelProvider.OLLAMA: "http://localhost:11434",  # Default Ollama endpoint
    ModelProvider.COHERE: "https://api.cohere.ai/v1",
    ModelProvider.MISTRAL: "https://api.mistral.ai/v1"
}

# Vault secret paths for API keys
VAULT_SECRET_PATHS = {
    ModelProvider.OPENAI: ("wilsons-raiders/creds", "OPENAI_API_KEY"),
    ModelProvider.ANTHROPIC: ("wilsons-raiders/creds", "ANTHROPIC_API_KEY"),
    ModelProvider.GOOGLE: ("wilsons-raiders/creds", "GOOGLE_API_KEY"),
    ModelProvider.OLLAMA: None,  # Local, no API key needed
    ModelProvider.COHERE: ("wilsons-raiders/creds", "COHERE_API_KEY"),
    ModelProvider.MISTRAL: ("wilsons-raiders/creds", "MISTRAL_API_KEY"),
    ModelProvider.META: ("wilsons-raiders/creds", "META_API_KEY")
}

# Model capabilities and characteristics
MODEL_CAPABILITIES = {
    "gpt-4o": {
        "context_window": 128000,
        "max_output": 4096,
        "supports_vision": True,
        "supports_function_calling": True,
        "supports_json_mode": True
    },
    "gpt-4-turbo": {
        "context_window": 128000,
        "max_output": 4096,
        "supports_vision": True,
        "supports_function_calling": True,
        "supports_json_mode": True
    },
    "gpt-4": {
        "context_window": 8192,
        "max_output": 4096,
        "supports_vision": False,
        "supports_function_calling": True,
        "supports_json_mode": True
    },
    "gpt-3.5-turbo": {
        "context_window": 16385,
        "max_output": 4096,
        "supports_vision": False,
        "supports_function_calling": True,
        "supports_json_mode": True
    },
    "claude-3-opus-20240229": {
        "context_window": 200000,
        "max_output": 4096,
        "supports_vision": True,
        "supports_function_calling": True,
        "supports_json_mode": True
    },
    "claude-3-sonnet-20240229": {
        "context_window": 200000,
        "max_output": 4096,
        "supports_vision": True,
        "supports_function_calling": True,
        "supports_json_mode": True
    },
    "claude-3-haiku-20240307": {
        "context_window": 200000,
        "max_output": 4096,
        "supports_vision": True,
        "supports_function_calling": True,
        "supports_json_mode": True
    },
    "gemini-ultra": {
        "context_window": 32000,
        "max_output": 2048,
        "supports_vision": True,
        "supports_function_calling": True,
        "supports_json_mode": True
    },
    "gemini-pro": {
        "context_window": 32000,
        "max_output": 2048,
        "supports_vision": False,
        "supports_function_calling": True,
        "supports_json_mode": True
    }
}


class ModelConfig:
    """Unified model configuration and selection interface."""

    def __init__(self, 
                 provider: Optional[ModelProvider] = None,
                 cost_tier: CostTier = CostTier.BALANCED,
                 custom_model: Optional[str] = None):
        """Initialize model configuration.

        Args:
            provider: AI provider to use (defaults to OpenAI)
            cost_tier: Performance/cost tier
            custom_model: Override with specific model name
        """
        self.provider = provider or ModelProvider.OPENAI
        self.cost_tier = cost_tier
        self.custom_model = custom_model

        # Select model
        if custom_model:
            self.model = custom_model
        else:
            self.model = self.get_model_for_tier(self.provider, self.cost_tier)

        self.endpoint = PROVIDER_ENDPOINTS.get(self.provider)
        self.capabilities = MODEL_CAPABILITIES.get(self.model, {})

        logger.info(f"ModelConfig initialized: provider={self.provider.value}, "
                   f"model={self.model}, tier={self.cost_tier.value}")

    @staticmethod
    def get_model_for_tier(provider: ModelProvider, tier: CostTier) -> str:
        """Get model name for provider and cost tier.

        Args:
            provider: AI provider
            tier: Cost/performance tier

        Returns:
            Model identifier string

        Raises:
            ValueError: If provider/tier combination not supported
        """
        if provider not in MODEL_MATRIX:
            raise ValueError(f"Provider {provider.value} not configured")

        if tier not in MODEL_MATRIX[provider]:
            raise ValueError(f"Tier {tier.value} not available for {provider.value}")

        return MODEL_MATRIX[provider][tier]

    @staticmethod
    def get_available_providers() -> List[ModelProvider]:
        """Get list of configured providers."""
        return list(MODEL_MATRIX.keys())

    @staticmethod
    def get_available_tiers(provider: ModelProvider) -> List[CostTier]:
        """Get available tiers for a provider."""
        if provider not in MODEL_MATRIX:
            return []
        return list(MODEL_MATRIX[provider].keys())

    def get_vault_secret_path(self) -> Optional[tuple]:
        """Get Vault secret path for provider's API key."""
        return VAULT_SECRET_PATHS.get(self.provider)

    def get_context_window(self) -> int:
        """Get model's context window size."""
        return self.capabilities.get("context_window", 4096)

    def supports_vision(self) -> bool:
        """Check if model supports vision/image input."""
        return self.capabilities.get("supports_vision", False)

    def supports_function_calling(self) -> bool:
        """Check if model supports function calling."""
        return self.capabilities.get("supports_function_calling", False)

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "cost_tier": self.cost_tier.value,
            "endpoint": self.endpoint,
            "capabilities": self.capabilities
        }


# Convenience functions for backwards compatibility
def get_model_for_cost_tier(cost_tier: str, 
                            provider: str = "openai") -> str:
    """Legacy function: Get model name for cost tier.

    Args:
        cost_tier: 'economic', 'balanced', 'high-performance', 'ultra-performance'
        provider: Provider name (default: openai)

    Returns:
        Model identifier
    """
    provider_enum = ModelProvider(provider)
    tier_enum = CostTier(cost_tier)
    return ModelConfig.get_model_for_tier(provider_enum, tier_enum)
