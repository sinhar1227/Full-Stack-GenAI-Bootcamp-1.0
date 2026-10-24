import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from servers.travel_server import server

if __name__ == "__main__":
    server.run(transport="streamable-http", host="127.0.0.1", port=8001, stateless_http=True, json_response=True)
