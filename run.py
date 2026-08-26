import os
import sys
import uvicorn
from dotenv import load_dotenv

load_dotenv()

# Force utf-8 stdout encoding for Windows console compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure root directory and backend directory are in sys.path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))

    print(f"\nStarting FastAPI Server on http://{host}:{port} ...")
    print("Open your browser and navigate to: http://127.0.0.1:8000")
    print("==========================================================\n")

    uvicorn.run("backend.main:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
