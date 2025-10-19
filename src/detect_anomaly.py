# detect_anomaly.py
"""
АВТОМАТИЧЕСКИЙ ПОИСК ПОДОЗРИТЕЛЬНЫХ ОПЕРАЦИЙ
Использует искусственный интеллект для обнаружения аномалий
"""

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

print(" ЗАПУСК ИСКУССТВЕННОГО ИНТЕЛЛЕКТА ДЛЯ ПОИСКА АНОМАЛИЙ...")

try:
    df = pd.read_csv("dummy_transactions.csv")
    print(f" Загружено {len(df):,} транзакций для анализа")
except:
    print(" Файл dummy_transactions.csv не найден!")
    print(" Сначала запустите: python dummy_data_gen.py")
    exit()

print(" ИЩЕМ ПОДОЗРИТЕЛЬНЫЕ ОПЕРАЦИИ...")
model = IsolationForest(contamination=0.05, random_state=42)  # 5% аномалий

X = df[['amount']]
df['ai_anomaly'] = model.fit_predict(X)

df['is_suspicious'] = (df['ai_anomaly'] == -1).astype(int)

suspicious_count = df['is_suspicious'].sum()
total_amount = df['amount'].sum()
suspicious_amount = df[df['is_suspicious'] == 1]['amount'].sum()

print(f"\n РЕЗУЛЬТАТЫ РАБОТЫ ИИ:")
print(f"   • Найдено подозрительных операций: {suspicious_count:,} шт.")
print(f"   • Сумма подозрительных операций: {suspicious_amount:,.0f} UZS")
print(f"   • Это {(suspicious_count/len(df)*100):.1f}% от всех транзакций")

suspicious_ops = df[df['is_suspicious'] == 1].copy()
suspicious_ops = suspicious_ops.sort_values('amount', ascending=False)

print(f"\n СОХРАНЯЕМ РЕЗУЛЬТАТЫ...")
suspicious_ops.to_csv("founded_anomalu.csv", index=False)
print(f" Сохранено {len(suspicious_ops)} подозрительных операций")

print("\n САМЫЕ КРУПНЫЕ НАЙДЕННЫЕ АНОМАЛИИ:")
top_suspicious = suspicious_ops.head(5)
for i, row in top_suspicious.iterrows():
    print(f"   {i+1}. {row['amount']:,.0f} UZS")

print("\n СОЗДАЕМ ГРАФИК РЕЗУЛЬТАТОВ...")
plt.figure(figsize=(12, 6))

normal = df[df['is_suspicious'] == 0]
suspicious = df[df['is_suspicious'] == 1]

plt.scatter(normal.index, normal['amount'], 
           alpha=0.6, label='НОРМАЛЬНЫЕ', color='green', s=20)
plt.scatter(suspicious.index, suspicious['amount'], 
           color='red', label='ПОДОЗРИТЕЛЬНЫЕ', marker='X', s=60)

plt.title('РЕЗУЛЬТАТЫ РАБОТЫ ИСКУССТВЕННОГО ИНТЕЛЛЕКТА\nОбнаружение подозрительных операций')
plt.xlabel('Номер транзакции')
plt.ylabel('Сумма транзакции (UZS)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('Reports/graphic_of_ai.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n ПОИСК АНОМАЛИЙ ЗАВЕРШЕН!")
print("Созданы файлы:")
print("   • Reports/founded_anomaly.csv")
print("   • Reports/graphic_of_ai.png")