import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
REPORTS_DIR = PROJECT_ROOT / "Reports"
DATA_DIR = PROJECT_ROOT

PATHS = {
    'transactions': DATA_DIR / "dummy_transactions.csv",
    'users': DATA_DIR / "dummy_users.csv", 
    'prepared_data': DATA_DIR / "prepared_transactions.csv",
    'model': DATA_DIR / "ai_fraud_model.pkl",
    'reports': REPORTS_DIR
}

MODEL_CONFIG = {
    'isolation_forest': {
        'n_estimators': 100,
        'contamination': 0.05,
        'random_state': 42
    },
    'neural_network': {
        'epochs': 50,
        'batch_size': 32,
        'hidden_layers': [64, 32]
    },
    'random_forest': {
        'n_estimators': 50,
        'max_depth': 10
    }
}

FRAUD_RULES = {
    'high_risk_amount': 10_000_000,  # > 10 млн
    'suspicious_small_amount': 1000,  # < 1 тыс
    'max_transactions_per_hour': 5,
    'time_window_minutes': 60
}

API_CONFIG = {
    'host': '0.0.0.0',
    'port': 8000,
    'debug': True
}

def setup_directories():
    """Создает необходимые директории"""
    REPORTS_DIR.mkdir(exist_ok=True)
    print(" Директории настроены")

def get_data_path(file_type):
    """Возвращает путь к файлу данных"""
    return PATHS.get(file_type)

PROJECT_ROOT = Path(__file__).parent.parent
MODEL_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"

API_CONFIG = {
    "host": os.getenv("API_HOST", "0.0.0.0"),
    "port": int(os.getenv("API_PORT", "8000")),
    "debug": os.getenv("DEBUG", "False").lower() == "true"
}

DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "fraud_db"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "password")
}