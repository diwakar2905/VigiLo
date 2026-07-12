# service/monitor.py (Backward Compatibility Wrapper)
import sys
import os

# Adjust path and delegate to main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

if __name__ == "__main__":
    main()
