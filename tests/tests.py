import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.secure_api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_fraud_detection():
    # Нормальная транзакция
    response = client.post("/check", json={"amount": 50000, "user_id": "test_user"})
    assert response.status_code == 200
    assert response.json()["risk_level"] == "LOW"

def test_high_risk_transaction():
    # Подозрительная транзакция
    response = client.post("/check", json={"amount": 15000000, "user_id": "test_user"})
    assert response.status_code == 200
    assert response.json()["is_suspicious"] == True
    assert response.json()["risk_level"] == "HIGH"