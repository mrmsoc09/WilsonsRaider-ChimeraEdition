"""
Data Integration Module for Kaison Zero-SOC
Handles real-time data ingestion from 8+ sources
"""

__version__ = "1.0.0"
__all__ = [
    "BBPDataHandler",
    "WazuhDataHandler",
    "CortexDataHandler",
    "TheHiveDataHandler",
    "ShuffleDataHandler",
    "RSSDataHandler",
    "ElasticsearchDataHandler",
    "BatchPromptEngine",
    "ContextCompressor"
]
