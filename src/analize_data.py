import pandas as pd
import matplotlib.pyplot as plt
import mplcursors
from pathlib import Path

print(" ЗАПУСК АНАЛИЗА БЕЗОПАСНОСТИ ТРАНЗАКЦИЙ...")

if not Path("prepared_transactions.csv").exists():
    print(" Файл с транзакциями не найден!")
    print(" Сначала запустите: python prepare_dataset.py")
    exit()

print(" ЗАГРУЗКА ДАННЫХ...")
df = pd.read_csv("prepared_transactions.csv")
print(f" Загружено {len(df):,} транзакций")

if "is_fraud" not in df.columns:
    print(" Нет данных о мошенничестве!")
    print(" Запустите подготовку данных сначала")
    exit()

total = len(df)
fraud_count = df['is_fraud'].sum()
fraud_percent = (fraud_count / total) * 100
total_money = df['amount'].sum()
fraud_money = df[df['is_fraud'] == 1]['amount'].sum()

print("\n ОСНОВНЫЕ РЕЗУЛЬТАТЫ:")
print(f"   • Всего транзакций: {total:,} шт.")
print(f"   • Выявлено подозрительных: {fraud_count:,} шт.")
print(f"   • Уровень риска: {fraud_percent:.1f}%")
print(f"   • Сумма подозрительных операций: {fraud_money:,.0f} UZS")

suspicious = df[df['is_fraud'] == 1].copy()
suspicious = suspicious.sort_values('amount', ascending=False)

print(f"\n СОХРАНЯЕМ ОТЧЕТ...")
suspicious.to_excel("Reports/report_of_sus_operations.xlsx", index=False)
print(f" Сохранено {len(suspicious)} подозрительных транзакций")

print("\n ТОП-5 САМЫХ КРУПНЫХ ПОДОЗРИТЕЛЬНЫХ ОПЕРАЦИЙ:")
top_fraud = suspicious.head(5)
for i, row in top_fraud.iterrows():
    print(f"   {i+1}. {row['amount']:,.0f} UZS - клиент {row.get('user_id', 'N/A')}")

print("\n СОЗДАЕМ ГРАФИК...")
plt.figure(figsize=(12, 6))

colors = ['green' if x == 0 else 'red' for x in df['is_fraud']]

plt.scatter(df.index, df['amount'], c=colors, alpha=0.6, s=30)
plt.title('ВИЗУАЛИЗАЦИЯ ТРАНЗАКЦИЙ\n Нормальные  Подозрительные')
plt.xlabel('Номер транзакции')
plt.ylabel('Сумма (UZS)')
plt.grid(True, alpha=0.3)

scatter = plt.scatter(df.index, df['amount'], c=colors, alpha=0.6, s=30, picker=True)
cursor = mplcursors.cursor(scatter, hover=True)

@cursor.connect("add")
def on_hover(sel):
    idx = sel.index
    row = df.iloc[idx]
    status = " ПОДОЗРИТЕЛЬНАЯ" if row['is_fraud'] == 1 else " НОРМАЛЬНАЯ"
    sel.annotation.set_text(
        f"{status}\n"
        f"Сумма: {row['amount']:,.0f} UZS\n"
        f"Клиент: {row.get('user_id', 'N/A')}"
    )

plt.tight_layout()
plt.savefig('Reports/sec_graphic.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n АНАЛИЗ ЗАВЕРШЕН!")
print(" Созданы файлы:")
print("   • Reports/anomaly_report.xlsx")
print("   • Reports/sec_graphic.png")