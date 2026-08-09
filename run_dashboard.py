import sys
from streamlit.web.cli import main

if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        "dashboard.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--server.headless=true"
    ]
    main()

