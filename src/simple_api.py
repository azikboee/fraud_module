from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import numpy as np
from datetime import datetime
import uvicorn
from pathlib import Path

print(" ЗАПУСК ПРОСТОГО API...")

app = FastAPI(
    title="Simple Fraud API",
    description="Простой и надежный API для обнаружения мошенничества",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

ai_model = None
model_loaded = False

class TransactionRequest(BaseModel):
    amount: float
    user_id: str = "unknown"
    timestamp: str = None

class FraudResponse(BaseModel):
    is_suspicious: bool
    risk_score: float
    risk_level: str
    message: str
    timestamp: str

def load_simple_model():
    """Загружает простую модель"""
    global ai_model, model_loaded
    
    try:
        model_path = Path("universal_ai_model.pkl")
        if model_path.exists():
            ai_model = joblib.load(model_path)
            model_loaded = True
            print(" Универсальная модель загружена!")
            return True
        else:
            print("  Универсальная модель не найдена, используем правила")
            return False
    except Exception as e:
        print(f" Ошибка загрузки модели: {e}")
        return False

@app.on_event("startup")
def startup_event():
    """Загружает модель при запуске"""
    load_simple_model()

@app.get("/")
def root():
    return {
        "message": "Simple Fraud Detection API", 
        "status": "running",
        "model_loaded": model_loaded,
        "endpoints": {
            "health": "/health",
            "check": "/check",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy" if model_loaded else "no_model",
        "model_loaded": model_loaded,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/check", response_model=FraudResponse)
def check_transaction(transaction: TransactionRequest):
    """Проверяет транзакцию на мошенничество"""
    
    print(f" Проверяем: {transaction.amount:,.0f} UZS")
    
    risk_score = 0.0
    
    if transaction.amount > 10000000:  # > 10 млн
        risk_score += 0.7
    elif transaction.amount < 1000:    # < 1 тыс
        risk_score += 0.5
    elif transaction.amount > 5000000: # > 5 млн
        risk_score += 0.3
    
    if model_loaded and ai_model is not None:
        try:
            tx_data = {
                'amount': transaction.amount,
                'total_1h': 0,  # дефолтные значения
                'count_1h': 1,
                'time_diff_sec': 3600,
                'hour': datetime.now().hour,
                'day_of_week': datetime.now().weekday()
            }
            
            from simple_ai_model import predict_fraud
            ai_score, ai_fraud = predict_fraud(ai_model, tx_data)
            
            risk_score = max(risk_score, ai_score)
            print(f" AI оценка: {ai_score:.3f}")
            
        except Exception as e:
            print(f"  Ошибка AI: {e}, используем только правила")
    
    if risk_score > 0.7:
        risk_level = "HIGH"
        message = " ВЫСОКИЙ РИСК - требуется верификация"
    elif risk_score > 0.4:
        risk_level = "MEDIUM" 
        message = "  СРЕДНИЙ РИСК - рекомендуется проверка"
    else:
        risk_level = "LOW"
        message = " НИЗКИЙ РИСК - операция нормальная"
    
    is_suspicious = risk_score > 0.5
    
    response = FraudResponse(
        is_suspicious=is_suspicious,
        risk_score=round(risk_score, 3),
        risk_level=risk_level,
        message=message,
        timestamp=datetime.now().isoformat()
    )
    
    print(f" Результат: {risk_level} (score: {risk_score:.3f})")
    
    return response

@app.post("/batch-check")
def batch_check(transactions: list[TransactionRequest]):
    """Проверяет несколько транзакций"""
    results = []
    
    for tx in transactions:
        result = check_transaction(tx)
        results.append(result.dict())
    
    suspicious_count = sum(1 for r in results if r['is_suspicious'])
    
    return {
        "checked_count": len(results),
        "suspicious_count": suspicious_count,
        "success_rate": f"{(suspicious_count/len(results)*100):.1f}%",
        "results": results
    }

def main():
    """Запускает API сервер"""
    print("=" * 50)
    print(" SIMPLE FRAUD DETECTION API")
    print("=" * 50)
    print(" Документация: http://localhost:8000/docs")
    print(" Health check: http://localhost:8000/health")
    print(" Остановка: Ctrl+C")
    print("=" * 50)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main()