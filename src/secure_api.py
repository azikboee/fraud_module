from fastapi import FastAPI, Response
from pydantic import BaseModel
import psycopg2
from datetime import datetime
import uvicorn
import os
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
from prometheus_client import CONTENT_TYPE_LATEST

print(" ЗАПУСК API С МЕТРИКАМИ...")

app = FastAPI(
    title="Fraud Detection API",
    description="API для обнаружения мошенничества с метриками Prometheus",
    version="2.0"
)

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status_code'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
FRAUD_TRANSACTIONS = Counter('fraud_transactions_total', 'Total fraud transactions', ['risk_level'])

class TransactionRequest(BaseModel):
    amount: float
    user_id: str

class FraudResponse(BaseModel):
    is_suspicious: bool
    risk_score: float
    risk_level: str
    message: str
    timestamp: str

def get_db_connection():
    """Подключение к базе данных"""
    try:
        conn = psycopg2.connect(
            dbname="fraud_db",
            user="admin",
            password="password",
            host="db",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f" Ошибка подключения к БД: {e}")
        return None

@app.get("/metrics")
def metrics():
    """Endpoint для метрик Prometheus"""
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def root():
    REQUEST_COUNT.labels(method='GET', endpoint='/', status_code='200').inc()
    return {
        "message": "Fraud Detection API с метриками ", 
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "metrics": "http://localhost:8000/metrics"
    }

@app.get("/health")
def health_check():
    REQUEST_COUNT.labels(method='GET', endpoint='/health', status_code='200').inc()
    
    db_status = "connected" if get_db_connection() else "disconnected"
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/stats")
def get_stats():
    REQUEST_COUNT.labels(method='GET', endpoint='/stats', status_code='200').inc()
    
    conn = get_db_connection()
    if not conn:
        return {"error": "Database not available"}
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) as fraud_count,
                    AVG(amount) as avg_amount
                FROM transactions
            """)
            result = cur.fetchone()
            
            return {
                "total_transactions": result[0],
                "fraud_count": result[1],
                "avg_amount": float(result[2]) if result[2] else 0
            }
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@app.post("/check", response_model=FraudResponse)
def check_transaction(transaction: TransactionRequest):
    with REQUEST_DURATION.time():
        REQUEST_COUNT.labels(method='POST', endpoint='/check', status_code='200').inc()
        
        print(f" Проверяем транзакцию: {transaction.user_id} - {transaction.amount:,.0f} UZS")
        
        # Простые правила
        risk_score = 0.0
        
        if transaction.amount > 10000000:
            risk_score = 0.8
            message = "ВЫСОКИЙ РИСК - очень крупная сумма"
        elif transaction.amount < 1000:
            risk_score = 0.6
            message = "СРЕДНИЙ РИСК - подозрительно мелкая сумма"
        elif transaction.amount > 5000000:
            risk_score = 0.4
            message = "ПОВЫШЕННЫЙ РИСК - крупная сумма"
        else:
            risk_score = 0.1
            message = "НИЗКИЙ РИСК - операция нормальная"
        
        is_suspicious = risk_score > 0.5
        
        if risk_score > 0.7:
            risk_level = "HIGH"
        elif risk_score > 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        FRAUD_TRANSACTIONS.labels(risk_level=risk_level).inc()
        
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO transactions 
                        (user_id, amount, is_fraud, fraud_score, risk_level) 
                        VALUES (%s, %s, %s, %s, %s)
                    """, (transaction.user_id, transaction.amount, is_suspicious, risk_score, risk_level))
                    conn.commit()
                    print(" Данные сохранены в БД")
            except Exception as e:
                print(f" Ошибка сохранения в БД: {e}")
            finally:
                conn.close()
        
        response = FraudResponse(
            is_suspicious=is_suspicious,
            risk_score=round(risk_score, 3),
            risk_level=risk_level,
            message=message,
            timestamp=datetime.now().isoformat()
        )
        
        print(f" Результат: {risk_level} риск (score: {risk_score:.3f})")
        
        return response

def main():
    """Запускает API сервер"""
    print("=" * 50)
    print(" FRAUD DETECTION API WITH METRICS")
    print("=" * 50)
    print(" Host: 0.0.0.0:8000")
    print(" Документация: http://localhost:8000/docs")
    print(" Метрики: http://localhost:8000/metrics")
    print(" Health: http://localhost:8000/health")
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