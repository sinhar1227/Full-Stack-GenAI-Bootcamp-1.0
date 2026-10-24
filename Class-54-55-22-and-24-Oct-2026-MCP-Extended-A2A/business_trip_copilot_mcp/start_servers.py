import subprocess
import sys
from pathlib import Path


# Folder jahan start_servers.py rakha hai
BASE_DIR = Path(__file__).resolve().parent


servers = [
    (
        "Travel MCP",
        BASE_DIR / "http_servers" / "travel_http_server.py",
        8001,
    ),
    (
        "Policy MCP",
        BASE_DIR / "http_servers" / "policy_http_server.py",
        8002,
    ),
    (
        "Work MCP",
        BASE_DIR / "http_servers" / "work_http_server.py",
        8003,
    ),
]


processes = []


for name, server_file, port in servers:

    print(f"Starting {name}...")

    process = subprocess.Popen(
        [
            sys.executable,
            str(server_file),
        ],
        cwd=str(BASE_DIR),
    )

    processes.append(process)

    print(
        f"{name} started at "
        f"http://127.0.0.1:{port}/mcp"
    )


print("\nAll MCP servers are running.")


try:

    for process in processes:
        process.wait()

except KeyboardInterrupt:

    print("\nStopping all MCP servers...")

    for process in processes:
        process.terminate()

    print("All MCP servers stopped.")