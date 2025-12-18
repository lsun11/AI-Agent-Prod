# server.py
from dotenv import load_dotenv
load_dotenv()

import uvicorn
from src.advanced_agent.api.app import create_app

advanced_agent = create_app()


def main():
    # Normal dev run (no auto reload; use uvicorn CLI if you want reload)
    uvicorn.run(advanced_agent, host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
