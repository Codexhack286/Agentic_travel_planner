import asyncio
import os
import sys
import shutil
from pathlib import Path

# Add project directories to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
AGENT_ROOT = PROJECT_ROOT / "ai-travel-concierge"
BACKEND_ROOT = PROJECT_ROOT / "backend"

sys.path.insert(0, str(AGENT_ROOT))

def main():
    print("=== Resetting Databases ===")
    
    # 1. Delete backend.db
    backend_db = BACKEND_ROOT / "backend.db"
    if backend_db.exists():
        print(f"Deleting backend database: {backend_db}")
        try:
            backend_db.unlink()
            print("✓ Backend database deleted.")
        except Exception as e:
            print(f"✗ Failed to delete backend database: {e}")
    else:
        print("Backend database does not exist, skipping deletion.")

    # 2. Delete backend/data/vector_db
    backend_vdb = BACKEND_ROOT / "data" / "vector_db"
    if backend_vdb.exists():
        print(f"Deleting backend vector DB directory: {backend_vdb}")
        try:
            shutil.rmtree(backend_vdb)
            print("✓ Backend vector DB deleted.")
        except Exception as e:
            print(f"✗ Failed to delete backend vector DB: {e}")

    # 3. Delete ai-travel-concierge/data/vector_db
    agent_vdb = AGENT_ROOT / "data" / "vector_db"
    if agent_vdb.exists():
        print(f"Deleting agent vector DB directory: {agent_vdb}")
        try:
            shutil.rmtree(agent_vdb)
            print("✓ Agent vector DB deleted.")
        except Exception as e:
            print(f"✗ Failed to delete agent vector DB: {e}")

    # Create directories if missing
    (AGENT_ROOT / "data").mkdir(exist_ok=True)
    
    print("\n=== Initializing Vector DB ===")
    try:
        from scripts.init_vectordb import initialize_vector_db
        asyncio.run(initialize_vector_db())
        print("✓ Vector DB successfully initialized!")
    except Exception as e:
        print(f"✗ Failed to initialize vector DB: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
