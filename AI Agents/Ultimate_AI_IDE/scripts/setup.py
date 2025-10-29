"""
UAIDE Setup Script

Installs dependencies, downloads models, and initializes the database.
Phase 1 implementation stub.
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.12 or higher."""
    if sys.version_info < (3, 12):
        print("Error: Python 3.12 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def install_dependencies():
    """Install required Python packages."""
    print("\nInstalling dependencies...")
    requirements_file = Path(__file__).parent.parent / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"Error: requirements.txt not found at {requirements_file}")
        return False
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    print("\nCreating directories...")
    base_path = Path(__file__).parent.parent
    
    directories = [
        "data",
        "data/backups",
        "data/faiss_index",
        "logs",
        "llama-cpp",
        "llama-cpp/models",
    ]
    
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created: {directory}/")
    
    return True


def create_config():
    """Create default configuration file."""
    print("\nCreating configuration...")
    base_path = Path(__file__).parent.parent
    config_file = base_path / "config.json"
    example_config = base_path / "config.example.json"
    
    if config_file.exists():
        print("✓ config.json already exists")
        return True
    
    if example_config.exists():
        import shutil
        shutil.copy(example_config, config_file)
        print("✓ Created config.json from example")
        return True
    
    print("Warning: config.example.json not found")
    return False


def initialize_database():
    """Initialize the database."""
    print("\nInitializing database...")
    try:
        # Add parent directory to path to import src modules
        base_path = Path(__file__).parent.parent
        sys.path.insert(0, str(base_path))
        
        from src.db.database import Database
        from src.config.config import Config
        
        # Load config to get database path
        cfg = Config()
        cfg.load()
        db_path = cfg.get('database.path', 'data/uaide.db')
        
        # Initialize database
        db = Database(db_path)
        if db.connect() and db.initialize():
            print("✓ Database initialized successfully")
            db.close()
            return True
        else:
            print("✗ Database initialization failed")
            return False
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False


def check_llama_setup():
    """Check if llama.cpp binary and model are set up."""
    print("\nChecking llama.cpp setup...")
    base_path = Path(__file__).parent.parent
    
    # Check for llama.cpp binary
    llama_dir = base_path / "llama-cpp"
    binary_found = False
    
    if llama_dir.exists():
        binary_names = ["llama-cli.exe", "main.exe", "llama.exe", "llama-cli", "main", "llama"]
        for binary_name in binary_names:
            if (llama_dir / binary_name).exists():
                print(f"✓ Found llama.cpp binary: {binary_name}")
                binary_found = True
                break
    
    if not binary_found:
        print("⚠ llama.cpp binary not found")
        print("  Download from: https://github.com/ggerganov/llama.cpp/releases")
        print("  Place in: llama-cpp/ directory")
        print("  See: docs/LLAMA_CPP_SETUP.md for instructions")
    
    # Check for models
    models_dir = llama_dir / "models"
    model_found = False
    
    if models_dir.exists():
        gguf_files = list(models_dir.glob("*.gguf"))
        if gguf_files:
            print(f"✓ Found {len(gguf_files)} model(s) in llama-cpp/models/")
            model_found = True
    
    if not model_found:
        print("⚠ No AI models found")
        print("  Download .gguf model from HuggingFace")
        print("  Place in: llama-cpp/models/ directory")
        print("  Update config.json with model path")
    
    return True  # Don't fail setup, just warn


def main():
    """Run setup process."""
    print("=" * 60)
    print("Ultimate AI-Powered IDE - Setup")
    print("=" * 60)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Creating directories", create_directories),
        ("Creating configuration", create_config),
        ("Initializing database", initialize_database),
        ("Checking llama.cpp setup", check_llama_setup),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n✗ Setup failed at: {step_name}")
            return 1
    
    print("\n" + "=" * 60)
    print("✓ Setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Download llama.cpp binary (see docs/LLAMA_CPP_SETUP.md)")
    print("2. Place binary in llama-cpp/ directory")
    print("3. Download AI model (.gguf) and place in llama-cpp/models/")
    print("4. Update config.json with model path")
    print("5. Run: scripts/run_uaide.bat --help (or python src/main.py --help)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
