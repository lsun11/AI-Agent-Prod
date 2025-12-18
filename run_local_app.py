# run_local_app.py
from dotenv import load_dotenv
load_dotenv()

import threading
import time
import webbrowser

import uvicorn
from server import advanced_agent  # FastAPI app created in server.py


def start_server():
    uvicorn.run(
        advanced_agent,
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


def main():
    # Start FastAPI/uvicorn in a background thread
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    # Give the server a moment to boot
    time.sleep(1.5)

    # Open the browser
    webbrowser.open("http://127.0.0.1:8000")

    # Keep the process alive so the server keeps running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
