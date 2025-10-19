# tests/test_api.py
import pytest
import sys
import os
from pathlib import Path

# Добавляем корень проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.secure_api import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_health_check():
    """Тест health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

def test_root_endpoint():
    """Тест корневого endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_metrics_endpoint():
    """Тест metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200

def test_low_risk_transaction():
    """Тест нормальной транзакции"""
    response = client.post(
        "/check",
        json={"amount": 50000, "user_id": "test_user"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "risk_level" in data

def test_high_risk_transaction():
    """Тест подозрительной транзакции"""
    response = client.post(
        "/check", 
        json={"amount": 15000000, "user_id": "test_user"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_suspicious"] == True