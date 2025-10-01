from pathlib import Path

# === Общие настройки проекта ===
BASE_DIR = Path(__file__).resolve().parent.parent  # папка parserMOEX
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# === ISS MOEX API ===
ISS_BASE_URL = "https://iss.moex.com"

# Основные режимы (борды) по рынкам
STOCK_ENGINE = "stock"
STOCK_MARKET = "shares"
STOCK_BOARD = "TQBR"      # Т+ Акции и ДР

FUTURES_ENGINE = "futures"
FUTURES_MARKET = "forts"
FUTURES_BOARD = "RFUD"    # Основной режим ФОРТС

# HTTP параметры
HTTP_TIMEOUT = 15.0  # секунды