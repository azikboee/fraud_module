# prepare_dataset.py
"""
🛠️ ПОДГОТОВКА ДАННЫХ ДЛЯ AI СИСТЕМЫ
Обновленная версия с созданием всех необходимых колонок
"""

import pandas as pd
import numpy as np
from pathlib import Path

print(" ПОДГОТАВЛИВАЕМ ДАННЫЕ ДЛЯ ПРОДВИНУТОГО AI...")

def prepare_dataset():
    """Основная функция подготовки данных"""
    
    if not Path("dummy_transactions.csv").exists():
        print(" Файл dummy_transactions.csv не найден!")
        print(" Сначала запустите: python dummy_data_gen.py")
        return False
    
    try:
        transactions = pd.read_csv("dummy_transactions.csv")
        print(f" Загружено {len(transactions):,} транзакций")
        
        if 'user_id' not in transactions.columns:
            print("  Колонка user_id не найдена, создаем...")
            transactions['user_id'] = [f'user_{i%100+1:03d}' for i in range(len(transactions))]
        
        if 'timestamp' in transactions.columns:
            transactions["timestamp"] = pd.to_datetime(transactions["timestamp"])
            transactions = transactions.sort_values(["user_id", "timestamp"]).reset_index(drop=True)
        else:
            print("  Колонка timestamp не найдена, создаем фиктивные даты...")
            transactions["timestamp"] = pd.date_range(start='2024-01-01', periods=len(transactions), freq='H')
        
        print(" СОЗДАЕМ ПРИЗНАКИ ДЛЯ AI...")
        
        print("1. Базовые статистики по пользователям...")
        user_stats = transactions.groupby('user_id').agg({
            'amount': ['mean', 'std', 'min', 'max', 'count']
        }).round(2)
        user_stats.columns = ['user_mean', 'user_std', 'user_min', 'user_max', 'user_count']
        transactions = transactions.merge(user_stats, on='user_id', how='left')
        
        print("2. Временные особенности...")
        transactions["hour"] = transactions["timestamp"].dt.hour
        transactions["day_of_week"] = transactions["timestamp"].dt.dayofweek
        transactions["is_weekend"] = transactions["day_of_week"].isin([5, 6]).astype(int)
        transactions["month"] = transactions["timestamp"].dt.month
        
        print("3. Поведенческие паттерны...")
        
        transactions["total_1h"] = (
            transactions.groupby("user_id", group_keys=False)
            .apply(lambda g: g.rolling("1h", on="timestamp")["amount"].sum())
        ).fillna(0)
        
        transactions["count_1h"] = (
            transactions.groupby("user_id", group_keys=False)
            .apply(lambda g: g.rolling("1h", on="timestamp")["amount"].count())
        ).fillna(0)
        
        for lag in range(1, 4):
            transactions[f"prev_amount_{lag}"] = (
                transactions.groupby("user_id")["amount"].shift(lag).fillna(0)
            )
        
        transactions["amount_ratio"] = (
            transactions["amount"] / transactions.groupby("user_id")["amount"].shift(1)
        ).replace([np.inf, -np.inf], 1).fillna(1)
        
        transactions["time_diff_sec"] = (
            transactions.groupby("user_id")["timestamp"].diff().dt.total_seconds().fillna(0)
        )
        
        print("4. Статистические аномалии...")
        transactions["amount_zscore"] = np.abs(
            (transactions["amount"] - transactions["amount"].mean()) / transactions["amount"].std()
        ).fillna(0)
        
        transactions["user_amount_zscore"] = transactions.groupby("user_id")["amount"].transform(
            lambda x: np.abs((x - x.mean()) / x.std()) if x.std() > 0 else 0
        ).fillna(0)
        
        print("5. Определяем целевые переменные...")
        
        transactions["is_fraud"] = (
            (transactions["amount"] > 10_000_000) |                           # Очень крупные суммы
            (transactions["amount"] < 1000) |                                # Очень мелкие суммы
            (transactions["count_1h"] > 8) |                                 # Слишком много операций в час
            (transactions["total_1h"] > 15_000_000) |                        # Большие суммы за час
            (transactions["time_diff_sec"] < 60) |                           # Операции менее чем за минуту
            (transactions["amount_zscore"] > 3)                              # Статистические аномалии
        ).astype(int)
        
        output_path = "prepared_transactions.csv"
        transactions.to_csv(output_path, index=False)
        
        fraud_count = transactions["is_fraud"].sum()
        fraud_percent = (fraud_count / len(transactions)) * 100
        
        print(f"\n✅ ДАННЫЕ ПОДГОТОВЛЕНЫ!")
        print(f"📊 СТАТИСТИКА БЕЗОПАСНОСТИ:")
        print(f"   • Всего транзакций: {len(transactions):,} шт.")
        print(f"   • Выявлено подозрительных: {fraud_count:,} шт.") 
        print(f"   • Уровень риска: {fraud_percent:.1f}%")
        print(f"   • Создано признаков: {len(transactions.columns)}")
        
        print(f"\n📋 СОЗДАННЫЕ КОЛОНКИ:")
        for i, col in enumerate(transactions.columns, 1):
            print(f"   {i:2d}. {col}")
        
        print(f"\n💾 Файл сохранен: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при подготовке данных: {e}")
        return False

if __name__ == "__main__":
    success = prepare_dataset()
    
    if success:
        print("\n🎯 ДЛЯ ПРОДОЛЖЕНИЯ ЗАПУСТИТЕ:")
        print("   python src/advanced_ai.py")
    else:
        print("\n💡 Проверьте наличие файла dummy_transactions.csv")