from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

DATAJUD_API_KEY = os.getenv("DATAJUD_API_KEY", "").strip()

if not DATAJUD_API_KEY:
    raise ValueError("A variável DATAJUD_API_KEY não foi definida no .env")