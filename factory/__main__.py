from factory.env_loader import load_dotenv
from factory.cli import main

if __name__ == "__main__":
    load_dotenv()
    raise SystemExit(main())
