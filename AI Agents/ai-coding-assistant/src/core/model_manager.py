"""
Model Manager Module

Provides functionality to list, select, and manage LLM models.
Supports both llama.cpp models and embedding models for RAG.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ModelInfo:
    """Information about a model."""
    name: str
    path: str
    size_mb: float
    type: str  # 'llm' or 'embedding'
    description: str
    parameters: Optional[str] = None
    quantization: Optional[str] = None
    context_size: Optional[int] = None
    is_available: bool = True
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: dict) -> 'ModelInfo':
        """Create from dictionary."""
        return ModelInfo(**data)


class ModelManager:
    """
    Manage LLM and embedding models.
    
    Features:
    - List available models
    - Get model information
    - Change active models
    - Detect models in directories
    - Save/load model registry
    """
    
    # Common llama.cpp model patterns
    MODEL_EXTENSIONS = ['.gguf', '.ggml', '.bin']
    
    # Known embedding models
    EMBEDDING_MODELS = {
        'all-MiniLM-L6-v2': {
            'description': 'Fast, 80MB, good quality',
            'size_mb': 80,
            'context_size': 256
        },
        'all-mpnet-base-v2': {
            'description': 'Balanced, 420MB, better quality',
            'size_mb': 420,
            'context_size': 384
        },
        'microsoft/codebert-base': {
            'description': 'Code-optimized, 500MB',
            'size_mb': 500,
            'context_size': 512
        }
    }
    
    def __init__(self, models_dir: str = "data/models", config_file: str = "data/model_registry.json"):
        """
        Initialize model manager.
        
        Args:
            models_dir: Directory containing models
            config_file: JSON file for model registry
        """
        self.models_dir = Path(models_dir)
        self.config_file = Path(config_file)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create registry
        self.registry = self._load_registry()
        
        # Scan for models
        self._scan_models()
    
    def _load_registry(self) -> Dict[str, ModelInfo]:
        """Load model registry from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {
                        name: ModelInfo.from_dict(info)
                        for name, info in data.items()
                    }
            except Exception as e:
                print(f"Warning: Could not load model registry: {e}")
        
        return {}
    
    def _save_registry(self):
        """Save model registry to file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                data = {
                    name: model.to_dict()
                    for name, model in self.registry.items()
                }
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save model registry: {e}")
    
    def _scan_models(self):
        """Scan models directory and update registry."""
        if not self.models_dir.exists():
            return
        
        # Scan for LLM models
        for ext in self.MODEL_EXTENSIONS:
            for model_path in self.models_dir.glob(f'*{ext}'):
                self._add_discovered_model(model_path)
        
        # Add known embedding models
        for name, info in self.EMBEDDING_MODELS.items():
            if name not in self.registry:
                self.registry[name] = ModelInfo(
                    name=name,
                    path='huggingface',
                    size_mb=info['size_mb'],
                    type='embedding',
                    description=info['description'],
                    context_size=info['context_size'],
                    is_available=True
                )
        
        self._save_registry()
    
    def _add_discovered_model(self, model_path: Path):
        """Add a discovered model to registry."""
        name = model_path.stem
        
        # Skip if already in registry with same path
        if name in self.registry and self.registry[name].path == str(model_path):
            return
        
        # Get file size
        size_mb = model_path.stat().st_size / (1024 * 1024)
        
        # Try to detect model properties from filename
        filename_lower = name.lower()
        
        # Detect quantization
        quantization = None
        for quant in ['q2_k', 'q3_k', 'q4_k', 'q5_k', 'q6_k', 'q8_0', 'f16', 'f32']:
            if quant in filename_lower:
                quantization = quant.upper()
                break
        
        # Detect parameters
        parameters = None
        for param in ['7b', '13b', '30b', '65b', '70b']:
            if param in filename_lower:
                parameters = param.upper()
                break
        
        # Detect context size
        context_size = None
        if '4k' in filename_lower or '4096' in filename_lower:
            context_size = 4096
        elif '8k' in filename_lower or '8192' in filename_lower:
            context_size = 8192
        elif '16k' in filename_lower:
            context_size = 16384
        elif '32k' in filename_lower:
            context_size = 32768
        
        # Create description
        desc_parts = []
        if parameters:
            desc_parts.append(parameters)
        if quantization:
            desc_parts.append(quantization)
        if context_size:
            desc_parts.append(f"{context_size//1024}K context")
        
        description = ", ".join(desc_parts) if desc_parts else "LLM model"
        
        self.registry[name] = ModelInfo(
            name=name,
            path=str(model_path),
            size_mb=size_mb,
            type='llm',
            description=description,
            parameters=parameters,
            quantization=quantization,
            context_size=context_size,
            is_available=model_path.exists()
        )
    
    def list_models(self, model_type: Optional[str] = None) -> List[ModelInfo]:
        """
        List available models.
        
        Args:
            model_type: Filter by type ('llm' or 'embedding'), or None for all
        
        Returns:
            List of ModelInfo objects
        """
        models = list(self.registry.values())
        
        if model_type:
            models = [m for m in models if m.type == model_type]
        
        # Sort by type, then by name
        models.sort(key=lambda m: (m.type, m.name))
        
        return models
    
    def get_model(self, name: str) -> Optional[ModelInfo]:
        """
        Get information about a specific model.
        
        Args:
            name: Model name
        
        Returns:
            ModelInfo or None if not found
        """
        return self.registry.get(name)
    
    def add_model(self, model_info: ModelInfo) -> bool:
        """
        Add a model to registry.
        
        Args:
            model_info: Model information
        
        Returns:
            True if successful
        """
        try:
            self.registry[model_info.name] = model_info
            self._save_registry()
            return True
        except Exception as e:
            print(f"Error adding model: {e}")
            return False
    
    def remove_model(self, name: str) -> bool:
        """
        Remove a model from registry (does not delete file).
        
        Args:
            name: Model name
        
        Returns:
            True if successful
        """
        if name in self.registry:
            del self.registry[name]
            self._save_registry()
            return True
        return False
    
    def get_llm_models(self) -> List[ModelInfo]:
        """Get list of LLM models."""
        return self.list_models(model_type='llm')
    
    def get_embedding_models(self) -> List[ModelInfo]:
        """Get list of embedding models."""
        return self.list_models(model_type='embedding')
    
    def set_active_llm(self, name: str, config_path: str = "data/config.json") -> bool:
        """
        Set active LLM model in config.
        
        Args:
            name: Model name
            config_path: Path to config file
        
        Returns:
            True if successful
        """
        model = self.get_model(name)
        if not model or model.type != 'llm':
            return False
        
        try:
            # Load config
            config_path = Path(config_path)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Update model path
            config['model_path'] = model.path
            
            # Update context size if known
            if model.context_size:
                config['context_size'] = model.context_size
            
            # Save config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error setting active model: {e}")
            return False
    
    def get_active_llm(self, config_path: str = "data/config.json") -> Optional[str]:
        """
        Get name of active LLM model.
        
        Args:
            config_path: Path to config file
        
        Returns:
            Model name or None
        """
        try:
            config_path = Path(config_path)
            if not config_path.exists():
                return None
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            model_path = config.get('model_path', '')
            
            # Find model by path
            for name, model in self.registry.items():
                if model.path == model_path and model.type == 'llm':
                    return name
            
            return None
        except Exception as e:
            print(f"Error getting active model: {e}")
            return None
    
    def rescan(self):
        """Rescan models directory."""
        self._scan_models()
    
    def get_model_stats(self) -> Dict[str, int]:
        """Get statistics about models."""
        models = self.list_models()
        
        return {
            'total': len(models),
            'llm': len([m for m in models if m.type == 'llm']),
            'embedding': len([m for m in models if m.type == 'embedding']),
            'available': len([m for m in models if m.is_available]),
            'total_size_mb': sum(m.size_mb for m in models)
        }
    
    def format_model_info(self, model: ModelInfo, include_path: bool = False) -> str:
        """
        Format model information for display.
        
        Args:
            model: Model information
            include_path: Whether to include file path
        
        Returns:
            Formatted string
        """
        info = f"{model.name}"
        
        if model.description:
            info += f" - {model.description}"
        
        info += f" ({model.size_mb:.0f} MB)"
        
        if not model.is_available:
            info += " [NOT AVAILABLE]"
        
        if include_path and model.path != 'huggingface':
            info += f"\n  Path: {model.path}"
        
        return info


if __name__ == "__main__":
    # Test model manager
    print("Testing Model Manager...\n")
    
    manager = ModelManager()
    
    # List all models
    print("=== All Models ===")
    models = manager.list_models()
    for model in models:
        print(f"  {manager.format_model_info(model)}")
    
    # List LLM models
    print("\n=== LLM Models ===")
    llm_models = manager.get_llm_models()
    for model in llm_models:
        print(f"  {manager.format_model_info(model, include_path=True)}")
    
    # List embedding models
    print("\n=== Embedding Models ===")
    emb_models = manager.get_embedding_models()
    for model in emb_models:
        print(f"  {manager.format_model_info(model)}")
    
    # Get stats
    print("\n=== Statistics ===")
    stats = manager.get_model_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Get active model
    active = manager.get_active_llm()
    if active:
        print(f"\n=== Active LLM Model ===")
        print(f"  {active}")
    else:
        print("\n=== Active LLM Model ===")
        print("  None configured")
    
    print("\n✓ Model Manager test complete!")
