import inspect
import sys
from pathlib import Path

# Add project root to path
SCRIPT_DIR = Path(__file__).parent.resolve()
AGENT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(AGENT_ROOT))

def main():
    try:
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
        print("=== AsyncSqliteSaver.from_conn_string Source ===")
        print(inspect.getsource(AsyncSqliteSaver.from_conn_string))
        
        print("\n=== AsyncSqliteSaver.__init__ Source ===")
        print(inspect.getsource(AsyncSqliteSaver.__init__))
    except Exception as e:
        print(f"Error inspecting AsyncSqliteSaver: {e}")

    try:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        print("\n=== AsyncPostgresSaver.from_conn_string Source ===")
        print(inspect.getsource(AsyncPostgresSaver.from_conn_string))
    except Exception as e:
        print(f"Error inspecting AsyncPostgresSaver: {e}")

if __name__ == "__main__":
    main()
