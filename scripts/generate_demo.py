"""
Скрипт для генерации демо данных
"""
import pandas as pd
import random
from datetime import datetime, timedelta

def generate_demo_transactions(n=1000):
    transactions = []
    
    for i in range(n):
        # 90% нормальных, 10% подозрительных
        if random.random() < 0.9:
            amount = random.randint(1000, 1000000)  # Нормальные суммы
            is_fraud = False
        else:
            # Подозрительные: либо очень мелкие, либо очень крупные
            amount = random.choice([
                random.randint(100, 1000),        # Очень мелкие
                random.randint(5000000, 10000000) # Очень крупные
            ])
            is_fraud = True
            
        transactions.append({
            "user_id": f"user_{random.randint(1, 100):03d}",
            "amount": amount,
            "is_fraud": is_fraud,
            "timestamp": datetime.now() - timedelta(hours=random.randint(0, 720))
        })
    
    df = pd.DataFrame(transactions)
    df.to_csv("data/demo_transactions.csv", index=False)
    print(f"✅ Сгенерировано {n} демо транзакций")

if __name__ == "__main__":
    generate_demo_transactions()