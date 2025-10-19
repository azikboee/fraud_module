import pandas as pd
import joblib
import numpy as np
from datetime import datetime

class RealTimeFraudDetector:
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Загружает обученную модель"""
        try:
            self.model = joblib.load("ai_fraud_model.pkl")
            print(" Модель ИИ загружена для реального времени")
        except:
            print(" Модель не найдена, используем простые правила")
            self.model = None
    
    def check_transaction(self, user_id, amount, timestamp=None):
        """Проверяет одну транзакцию в реальном времени"""
        print(f"\n ПРОВЕРЯЕМ ТРАНЗАКЦИЮ:")
        print(f"    Клиент: {user_id}")
        print(f"    Сумма: {amount:,.0f} UZS")
        print(f"    Время: {timestamp or datetime.now()}")

        risk_level = "НИЗКИЙ"
        reasons = []
        
        if amount > 10_000_000:
            risk_level = "ВЫСОКИЙ"
            reasons.append(" Очень крупная сумма")
        elif amount > 5_000_000:
            risk_level = "СРЕДНИЙ" 
            reasons.append(" Крупная сумма")
        
        if amount < 1000:
            risk_level = "ВЫСОКИЙ"
            reasons.append(" Подозрительно мелкая сумма")

        if self.model is not None:
            features = self._prepare_features(amount)
            prediction = self.model.predict([features])[0]
            score = self.model.decision_function([features])[0]
            
            if prediction == -1:
                risk_level = "ВЫСОКИЙ"
                reasons.append(f" Обнаружено ИИ (score: {score:.2f})")
        
        print(f"\n РЕЗУЛЬТАТ ПРОВЕРКИ:")
        print(f"   УРОВЕНЬ РИСКА: {risk_level}")
        
        if reasons:
            print("   ПРИЧИНЫ:")
            for reason in reasons:
                print(f"     {reason}")
        else:
            print("    Транзакция выглядит нормально")
        
        return risk_level

def demo_real_time():
    """Демонстрация работы в реальном времени"""
    detector = RealTimeFraudDetector()
    
    print(" ДЕМО РЕЖИМА РЕАЛЬНОГО ВРЕМЕНИ")
    print("=" * 40)
    
    test_transactions = [
        ("user_001", 50000),      
        ("user_002", 15000000),
        ("user_003", 500),
        ("user_004", 7500000),
    ]
    
    for user_id, amount in test_transactions:
        detector.check_transaction(user_id, amount)
        print("-" * 30)

if __name__ == "__main__":
    demo_real_time()