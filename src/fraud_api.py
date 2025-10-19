"""
 REST API ДЛЯ ИНТЕГРАЦИИ С БАНКОВСКИМИ СИСТЕМАМИ
Обновленная версия с исправлением путей
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import numpy as np
from datetime import datetime
import uvicorn
from pathlib import Path
import sys

print(" ЗАПУСК REST API СЕРВЕРА...")

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

app = FastAPI(
    title="Bank Fraud Detection API",
    description="API для обнаружения мошеннических транзакций в реальном времени",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

ai_system = None
model_loaded = False

class TransactionRequest(BaseModel):
    user_id: str
    amount: float
    timestamp: str = None
    merchant: str = None
    location: str = None

class FraudResponse(BaseModel):
    transaction_id: str
    is_suspicious: bool
    risk_score: float
    risk_level: str
    reasons: list
    timestamp: str
    model_used: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    total_checks: int = 0
    models_available: list = []

class BatchResponse(BaseModel):
    checked_count: int
    suspicious_count: int
    results: list

total_checks = 0

def load_ai_system():
    """Загружает AI систему"""
    global ai_system, model_loaded
    
    model_paths = [
        PROJECT_ROOT / "advanced_ai_system.pkl",
        PROJECT_ROOT / "ai_fraud_model.pkl"
    ]
    
    for model_path in model_paths:
        if model_path.exists():
            try:
                ai_system = joblib.load(model_path)
                model_loaded = True
                print(f" AI система загружена: {model_path.name}")
                return True
            except Exception as e:
                print(f" Ошибка загрузки {model_path}: {e}")
    
    print("  AI системы не найдены, используем базовые правила")
    return False

@app.on_event("startup")
async def startup_event():
    """Загружает модель при запуске"""
    load_ai_system()

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "Bank Fraud Detection API v2.0",
        "version": "2.0.0",
        "model_loaded": model_loaded,
        "endpoints": {
            "health": "/health",
            "check_transaction": "/check",
            "batch_check": "/batch-check",
            "reload_model": "/reload-model"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка здоровья API"""
    models = []
    if model_loaded:
        models = list(ai_system.models.keys()) if hasattr(ai_system, 'models') else ['advanced_ai']
    
    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        model_loaded=model_loaded,
        total_checks=total_checks,
        models_available=models
    )

@app.post("/check", response_model=FraudResponse)
async def check_transaction(transaction: TransactionRequest):
    """Проверяет одну транзакцию на мошенничество"""
    global total_checks
    total_checks += 1
    
    print(f" Проверяем транзакцию: {transaction.user_id} - {transaction.amount:,.0f} UZS")
    
    transaction_data = pd.DataFrame([{
        'user_id': transaction.user_id,
        'amount': transaction.amount,
        'timestamp': transaction.timestamp or datetime.now().isoformat(),
        'merchant': transaction.merchant or 'unknown',
        'city': transaction.location or 'unknown'
    }])
    
    risk_score = 0.0
    is_suspicious = False
    model_used = "basic_rules"
    
    if model_loaded and ai_system is not None:
        try:
            result = ai_system.predict_ensemble(transaction_data)
            risk_score = float(result.iloc[0]['ai_fraud_score'])
            is_suspicious = bool(result.iloc[0]['ai_fraud_prediction'])
            model_used = "advanced_ai"
            print(f"    Использована AI модель, риск: {risk_score:.3f}")
        except Exception as e:
            print(f"     Ошибка AI модели: {e}, используем базовые правила")
            risk_score, is_suspicious = simple_rules_check(transaction)
    else:
        risk_score, is_suspicious = simple_rules_check(transaction)
    
    if risk_score > 0.7:
        risk_level = "HIGH"
    elif risk_score > 0.3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    reasons = generate_reasons(transaction, risk_score, risk_level)
    
    response = FraudResponse(
        transaction_id=f"tx_{total_checks:06d}",
        is_suspicious=is_suspicious,
        risk_score=risk_score,
        risk_level=risk_level,
        reasons=reasons,
        timestamp=datetime.now().isoformat(),
        model_used=model_used
    )
    
    print(f" Результат: {risk_level} риск (score: {risk_score:.3f}, модель: {model_used})")
    
    return response

@app.post("/batch-check", response_model=BatchResponse)
async def batch_check_transactions(transactions: list[TransactionRequest]):
    """Проверяет несколько транзакций одновременно"""
    results = []
    
    for transaction in transactions:
        result = await check_transaction(transaction)
        results.append(result.dict())
    
    suspicious_count = sum(1 for r in results if r['is_suspicious'])
    
    return BatchResponse(
        checked_count=len(results),
        suspicious_count=suspicious_count,
        results=results
    )

@app.post("/reload-model")
async def reload_model():
    """Перезагружает AI модель"""
    global ai_system, model_loaded
    success = load_ai_system()
    
    return {
        "success": success,
        "message": "Model reloaded successfully" if success else "Failed to reload model",
        "model_loaded": model_loaded
    }

def simple_rules_check(transaction):
    """Простая проверка по правилам если AI недоступен"""
    risk_score = 0.0
    
    if transaction.amount > 10000000:  # > 10 млн
        risk_score += 0.6
    elif transaction.amount < 1000:    # < 1 тыс
        risk_score += 0.4
    elif transaction.amount > 5000000: # > 5 млн
        risk_score += 0.3
    
    if transaction.timestamp:
        try:
            hour = pd.to_datetime(transaction.timestamp).hour
            if 2 <= hour <= 6:
                risk_score += 0.2
        except:
            pass
    
    is_suspicious = risk_score > 0.5
    return min(risk_score, 1.0), is_suspicious

def generate_reasons(transaction, risk_score, risk_level):
    """Генерирует причины подозрительности"""
    reasons = []
    
    if transaction.amount > 10000000:
        reasons.append("Очень крупная сумма транзакции")
    elif transaction.amount < 1000:
        reasons.append("Подозрительно мелкая сумма")
    
    if risk_level == "HIGH":
        reasons.append("Высокий совокупный риск по AI модели")
    elif risk_level == "MEDIUM":
        reasons.append("Средний уровень риска")
    
    if risk_score > 0.8:
        reasons.append("Критический уровень риска - требуется верификация")
    
    return reasons

def main():
    """Запускает API сервер"""
    print("=" * 50)
    print(" BANK FRAUD DETECTION API v2.0")
    print("=" * 50)
    print(" Документация: http://localhost:8000/docs")
    print(" Health check: http://localhost:8000/health")
    print(" Reload model: POST http://localhost:8000/reload-model")
    print("  Остановка: Ctrl+C")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()