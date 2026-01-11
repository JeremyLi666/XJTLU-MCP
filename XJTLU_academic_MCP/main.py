"""
XJTLU Academic Navigator - Main Entry Point

This script serves as the entry point for the application.
It initializes and starts the FastAPI server that powers the MCP (Model-Context-Protocol) architecture.

Usage:
    python main.py

Environment Variables:
    PORT - Port to run the server on (default: 8000)
    USE_MOCK_AI - Whether to use mock AI responses (default: true)
    DEEPSEEK_API_KEY - API key for DeepSeek (required if USE_MOCK_AI=false)

Note: For production deployment, use uvicorn directly:
    uvicorn app.main:app --host 0.0.0.0 --port $PORT
"""

import os
import sys
import subprocess
import webbrowser
from threading import Timer

def check_environment():
    """Check required environment setup"""
    print(" Checking environment...")
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info < (3, 9):
        print(f" Python 3.9+ required. Current version: {python_version}")
        sys.exit(1)
    else:
        print(f"Python version: {python_version}")
    
    # Check dependencies
    try:
        import fastapi
        import uvicorn
        print(f" FastAPI version: {fastapi.__version__}")
        print(f" Uvicorn version: {uvicorn.__version__}")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please install requirements first: pip install -r requirements.txt")
        sys.exit(1)

def setup_environment():
    """Setup environment variables with defaults if not set"""
    if "USE_MOCK_AI" not in os.environ:
        os.environ["USE_MOCK_AI"] = "true"
        print("  USE_MOCK_AI not set - defaulting to mock mode")
    
    if "PORT" not in os.environ:
        os.environ["PORT"] = "8000"
    
    # Validate API key if not in mock mode
    if os.environ.get("USE_MOCK_AI", "true").lower() == "false":
        if not os.environ.get("DEEPSEEK_API_KEY"):
            print("⚠️  WARNING: DEEPSEEK_API_KEY not set but USE_MOCK_AI=false")
            print("   The application will fail when making AI requests.")
            print("   Set USE_MOCK_AI=true or provide a valid DEEPSEEK_API_KEY to continue.")
            # Don't exit - let the application start and handle errors gracefully

def open_browser():
    """Open web browser to the application"""
    webbrowser.open(f"http://localhost:{os.environ['PORT']}/web/index.html")

def start_server():
    """Start the FastAPI server"""
    port = int(os.environ.get("PORT", 8000))
    print(f"\n Starting XJTLU Academic Navigator on port {port}")
    print("=" * 60)
    print(f" API Documentation: http://localhost:{port}/api/docs")
    print(f" Web Interface: http://localhost:{port}/web/index.html")
    print(f" Server running in {'MOCK' if os.environ.get('USE_MOCK_AI', 'true').lower() == 'true' else 'REAL'} mode")
    print("=" * 60)
    
    # Start the FastAPI server
    uvicorn_cmd = [
        "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", str(port),
        "--reload"
    ]
    
    # Add reload directories if in development mode
    if os.environ.get("APP_ENV", "development") == "development":
        uvicorn_cmd.extend(["--reload-dir", "app", "--reload-dir", "mock"])
    
    try:
        subprocess.run(uvicorn_cmd)
    except KeyboardInterrupt:
        print("\n\n Server stopped by user")
    except Exception as e:
        print(f"\n Server error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("🎓 XJTLU Academic Navigator")
    print("Model-Context-Protocol Architecture for Academic Planning")
    print("-" * 60)
    
    # Setup and validate environment
    check_environment()
    setup_environment()
    
    # Open browser after 2 seconds (gives server time to start)
    Timer(2.0, open_browser).start()
    
    # Start the server
    start_server()
    
    print("\nApplication terminated gracefully")