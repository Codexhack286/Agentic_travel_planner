import asyncio
import os
import sys
import sqlite3
from pathlib import Path

# Add project root to path if running directly
SCRIPT_DIR = Path(__file__).parent.resolve()
AGENT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(AGENT_ROOT))

# Load config and environment
from src.utils.config import load_config

async def test_groq():
    print("\n--- Testing Groq API Key ---")
    config = load_config()
    api_key = config.get("groq_api_key")
    if not api_key:
        print("❌ Groq API key is not configured in environment/config.")
        return False
    
    try:
        from langchain_groq import ChatGroq
        chat = ChatGroq(groq_api_key=api_key, model_name="openai/gpt-oss-120b")
        response = await chat.ainvoke("Hello, please respond with the single word 'OK'.")
        content = response.content.strip()
        print(f"✅ Groq API response: '{content}'")
        return True
    except Exception as e:
        print(f"❌ Groq API failed: {e}")
        return False

async def test_unsplash():
    print("\n--- Testing Unsplash API Key ---")
    config = load_config()
    access_key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not access_key:
        print("❌ Unsplash API key (UNSPLASH_ACCESS_KEY) is not set.")
        return False
        
    try:
        from src.tools.external_apis.image_tools import UnsplashImageTool
        tool = UnsplashImageTool()
        result = await tool._call_api(query="Paris", per_page=1)
        if result and "results" in result:
            print(f"✅ Unsplash search successful. Found {len(result.get('results', []))} images.")
            return True
        else:
            print(f"❌ Unsplash search returned unexpected format: {result}")
            return False
    except Exception as e:
        print(f"❌ Unsplash API failed: {e}")
        return False

async def test_amadeus():
    print("\n--- Testing Amadeus API Keys ---")
    api_key = os.environ.get("AMADEUS_API_KEY")
    api_secret = os.environ.get("AMADEUS_API_SECRET")
    if not api_key or not api_secret:
        print("❌ Amadeus API key or secret is not set in environment.")
        return False
        
    try:
        from src.tools.external_apis.amadeus_tools import FlightSearchTool
        tool = FlightSearchTool()
        # Verify authentication
        token = await tool._get_access_token()
        print("✅ Amadeus OAuth2 token generated successfully.")
        
        # Verify a simple test query (JFK to LHR flights)
        from datetime import datetime, timedelta
        next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        result = await tool._call_api(origin="JFK", destination="LHR", departure_date=next_week, max_results=1)
        if "data" in result:
            print(f"✅ Amadeus Flight Search successful. Found {len(result.get('data', []))} flight options.")
            return True
        else:
            print(f"❌ Amadeus search returned unexpected format or error: {result}")
            return False
    except Exception as e:
        print(f"❌ Amadeus API failed: {e}")
        return False

async def test_visa():
    print("\n--- Testing Visa Requirements API Key ---")
    passport_api_key = os.environ.get("PASSPORT_API_KEY")
    if not passport_api_key:
        print("❌ Visa API key (PASSPORT_API_KEY) is not set.")
        return False
        
    try:
        from src.tools.external_apis.visa_tools import VisaRequirementTool
        tool = VisaRequirementTool()
        # Test USA to France
        result = await tool._call_api(from_country="US", to_country="FR")
        if "data" in result:
            label = result.get("data", {}).get("visaRules", {}).get("primary", {}).get("label", "Unknown")
            print(f"✅ Visa Requirements API successful. Requirement: {label}")
            return True
        else:
            print(f"❌ Visa API returned unexpected format or error: {result}")
            return False
    except Exception as e:
        print(f"❌ Visa Requirements API failed: {e}")
        return False

def test_databases():
    print("\n--- Testing Database Connections ---")
    
    # 1. Relational database in backend/backend.db
    backend_db = AGENT_ROOT.parent / "backend" / "backend.db"
    if backend_db.exists():
        try:
            conn = sqlite3.connect(str(backend_db))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [r[0] for r in cursor.fetchall()]
            print(f"✅ Backend relational database is accessible. Found tables: {tables}")
            conn.close()
        except Exception as e:
            print(f"❌ Backend database connection failed: {e}")
    else:
        print("ℹ️ Backend SQLite database (backend.db) does not exist yet. It will be initialized on backend server startup.")

    # 2. Travel concierge database in ai-travel-concierge/data/travel_concierge.db
    agent_db = AGENT_ROOT / "data" / "travel_concierge.db"
    if agent_db.exists():
        try:
            conn = sqlite3.connect(str(agent_db))
            conn.close()
            print("✅ Agent travel concierge database is accessible.")
        except Exception as e:
            print(f"❌ Agent travel concierge database connection failed: {e}")
    else:
        print("ℹ️ Agent SQLite database (travel_concierge.db) does not exist yet.")

    # 3. Checkpoints database in ai-travel-concierge/data/checkpoints.db
    checkpoints_db = AGENT_ROOT / "data" / "checkpoints.db"
    if checkpoints_db.exists():
        try:
            conn = sqlite3.connect(str(checkpoints_db))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [r[0] for r in cursor.fetchall()]
            print(f"✅ LangGraph SQLite checkpoints database is accessible. Found tables: {tables}")
            conn.close()
        except Exception as e:
            print(f"❌ LangGraph checkpoints database connection failed: {e}")
    else:
        print("ℹ️ LangGraph checkpoints database does not exist yet. It will be created on first state execution.")

async def main():
    print("==================================================")
    print("VOYAGER AI: SYSTEM CONFIGURATION & API KEY CHECK")
    print("==================================================")
    
    results = {}
    results["Groq"] = await test_groq()
    results["Unsplash"] = await test_unsplash()
    results["Amadeus"] = await test_amadeus()
    results["Visa (TravelBuddy)"] = await test_visa()
    test_databases()
    
    print("\n==================================================")
    print("SUMMARY RESULTS:")
    print("==================================================")
    for service, status in results.items():
        status_str = "✅ WORKING" if status else "❌ FAILED"
        print(f"  {service:<20}: {status_str}")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
