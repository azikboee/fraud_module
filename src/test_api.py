import requests
import json
from datetime import datetime

def test_api():
    """Тестирует все endpoints API"""
    
    BASE_URL = "http://localhost:8000"
    
    print(" ТЕСТИРУЕМ FRAUD DETECTION API")
    print("=" * 40)
    
    print("1. Проверяем health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.json()}")
    except:
        print("API не доступен! Запустите сначала fraud_api.py")
        return
    
    print("\n2. Тестируем проверку транзакций...")
    
    test_transactions = [
        {"user_id": "user_001", "amount": 50000, "merchant": "Korzinka"},
        {"user_id": "user_002", "amount": 15000000, "merchant": "AutoShop"},
        {"user_id": "user_003", "amount": 500, "merchant": "Online"},
        {"user_id": "vip_client", "amount": 500000, "merchant": "Restaurant"},
    ]
    
    for i, tx in enumerate(test_transactions, 1):
        response = requests.post(f"{BASE_URL}/check", json=tx)
        result = response.json()
        
        print(f"\n Транзакция {i}:")
        print(f"{tx['user_id']} |  {tx['amount']:,.0f} UZS")
        print(f"Риск: {result['risk_level']} ({result['risk_score']:.3f})")
        print(f"Подозрительная: {'Да' if result['is_suspicious'] else 'Нет'}")
        
        reasons = result.get('reasons') or []
        if reasons:
            print(f"Причины: {', '.join(reasons)}")
    
    print("\n3. Тестируем пакетную проверку...")
    
    batch_data = [
        {"user_id": "user_101", "amount": 100000},
        {"user_id": "user_102", "amount": 25000000},
        {"user_id": "user_103", "amount": 1500000},
    ]
    
    response = requests.post(f"{BASE_URL}/batch-check", json=batch_data)
    try:
        batch_result = response.json()
    except ValueError:
        print("Невалидный JSON в ответе от /batch-check")
        print(f"Status: {response.status_code}, Body: {response.text}")
        batch_result = {}

    if isinstance(batch_result, list):
        checked = len(batch_result)
        suspicious = sum(1 for r in batch_result if isinstance(r, dict) and r.get('is_suspicious'))
    else:
        checked = batch_result.get('checked_count', 0)
        suspicious = batch_result.get('suspicious_count', 0)

    print(f"Проверено: {checked} транзакций")
    print(f"Подозрительных: {suspicious}")
    
    print("\n ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print(f" Полная документация: {BASE_URL}/docs")

if __name__ == "__main__":
    test_api()