# main.py
import sys
from core.engine import VigiLoEngine


def main():
    mode = "service"
    if len(sys.argv) > 1:
        if "--commander" in sys.argv:
            mode = "commander"
        elif "--service" in sys.argv:
            mode = "service"

    # Instantiate orchestrator engine
    engine = VigiLoEngine()

    if mode == "commander":
        engine.run_commander()
    else:
        engine.run_service()


if __name__ == "__main__":
    main()
