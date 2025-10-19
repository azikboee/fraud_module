"""
ГЕНЕРАТОР ТЕСТОВЫХ ДАННЫХ ДЛЯ БАНКА
Создает реалистичные транзакции для тестирования системы безопасности
"""

import pandas as pd
import random
import datetime

print(" СОЗДАЕМ ТЕСТОВЫЕ ДАННЫЕ ДЛЯ БАНКА...")

banks = ["KapitalBank", "XalqBank", "IpakYuli", "AnorBank"]
cities = ["Ташкент", "Самарканд", "Бухара", "Андижан", "Наманган", "Фергана"]
merchants = ["Korzinka.uz", "Makro", "Rossiya", "Small", "DOK", "Artel", "Uzmobile"]

def generate_phone():
    return f"+998{random.choice(['90','91','93','94'])}{random.randint(1000000,9999999)}"

def generate_card(bank):
    return f"{random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}"

def generate_transaction(user_id):
    """Создает одну транзакцию"""
    if random.random() < 0.9:
        amount = random.randint(50000, 2000000)  # 50K - 2M
    elif random.random() < 0.95:
        amount = random.randint(2000000, 10000000)  # 2M - 10M
    else:
        amount = random.choice([
            random.randint(100, 1000),        # Очень мелкие
            random.randint(15000000, 50000000) # Очень крупные
        ])
    
    return {
        "user_id": user_id,
        "amount": amount,
        "merchant": random.choice(merchants),
        "city": random.choice(cities),
        "timestamp": (datetime.datetime.now() - 
                     datetime.timedelta(
                         days=random.randint(0, 30),
                         hours=random.randint(0, 23)
                     )).strftime("%Y-%m-%d %H:%M:%S")
    }

print(" СОЗДАЕМ БАЗУ КЛИЕНТОВ...")
users = []
for i in range(100):
    user = {
        "user_id": f"user_{i+1:03d}",
        "name": f"Client_{i+1}",
        "bank": random.choice(banks),
        "card_number": generate_card("bank"),
        "phone": generate_phone(),
        "city": random.choice(cities),
        "age": random.randint(18, 65)
    }
    users.append(user)

print(" СОЗДАЕМ ТРАНЗАКЦИИ...")
transactions = []
for user in users:
    for _ in range(random.randint(3, 20)):
        transactions.append(generate_transaction(user['user_id']))

users_df = pd.DataFrame(users)
transactions_df = pd.DataFrame(transactions)

print(f"\n ДАННЫЕ СОЗДАНЫ:")
print(f"   • Клиентов: {len(users_df):,} чел.")
print(f"   • Транзакций: {len(transactions_df):,} шт.")
print(f"   • Общая сумма: {transactions_df['amount'].sum():,.0f} UZS")

print(f"\n СОХРАНЯЕМ ФАЙЛЫ...")
users_df.to_csv("dummy_users.csv", index=False)
transactions_df.to_csv("dummy_transactions.csv", index=False)

print("\n СТАТИСТИКА ТРАНЗАКЦИЙ:")
print(f"   • Средний чек: {transactions_df['amount'].mean():,.0f} UZS")
print(f"   • Самая крупная: {transactions_df['amount'].max():,.0f} UZS")
print(f"   • Самая мелкая: {transactions_df['amount'].min():,.0f} UZS")

print("\n ДЛЯ ПРОДОЛЖЕНИЯ ЗАПУСТИТЕ:")
print("   python prepare_dataset.py")