"""
ОСНОВНАЯ МОДЕЛЬ ИСКУССТВЕННОГО ИНТЕЛЛЕКТА
Для обнаружения мошеннических операций в банке
"""

import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
import numpy as np

print(" ЗАГРУЗКА МОДЕЛИ ИСКУССТВЕННОГО ИНТЕЛЛЕКТА...")

def check_columns_and_create_features(data):
    """Проверяет какие колонки есть и создает фичи"""
    print(" ПРОВЕРЯЕМ ДОСТУПНЫЕ ДАННЫЕ...")
    print(f"   Доступные колонки: {list(data.columns)}")
    
    features = data[['amount']].copy()  # Сумма всегда есть
    
    if 'total_1h' in data.columns:
        features['total_1h'] = data['total_1h'].fillna(0)
        print("    Используем: total_1h")
    else:
        features['recent_total'] = data.groupby('user_id')['amount'].rolling(5, min_periods=1).sum().reset_index(level=0, drop=True).fillna(0)
        print("    Создаем: recent_total")
    
    if 'count_1h' in data.columns:
        features['count_1h'] = data['count_1h'].fillna(0)
        print("    Используем: count_1h")
    else:
        features['recent_count'] = data.groupby('user_id')['amount'].rolling(5, min_periods=1).count().reset_index(level=0, drop=True).fillna(0)
        print("    Создаем: recent_count")
    
    if 'timestamp' in data.columns:
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        features['hour'] = data['timestamp'].dt.hour
        features['day_of_week'] = data['timestamp'].dt.dayofweek
        print("    Добавляем: hour, day_of_week")
    
    features = features.fillna(0)
    
    print(f"    Итоговые фичи: {list(features.columns)}")
    return features

def train_ai_model():
    """Обучает модель ИИ находить мошенничество"""
    print(" ОБУЧАЕМ МОДЕЛЬ НА ИСТОРИЧЕСКИХ ДАННЫХ...")
    
    try:
        data = pd.read_csv("prepared_transactions.csv")
        print(f" Используем {len(data):,} транзакций для обучения")
        
        features = check_columns_and_create_features(data)
        
        model = IsolationForest(
            n_estimators=100,  # Упростил для скорости
            contamination=0.05,  # Ожидаем 5% мошенничества
            random_state=42,
            max_samples=256  # Для стабильности
        )
        
        print(" ОБУЧАЕМ МОДЕЛЬ...")
        model.fit(features)
        
        joblib.dump(model, "ai_fraud_model.pkl") #.pkl Для моделей. Они есть и в остальных файлах
        print(" МОДЕЛЬ СОХРАНЕНА: ai_fraud_model.pkl")
        
        return model, features.columns.tolist()
        
    except Exception as e:
        print(f" ОШИБКА ПРИ ОБУЧЕНИИ: {e}")
        print(" Проверьте что prepared_transactions.csv создан правильно")
        return None, None

def detect_fraud_with_ai():
    """Использует ИИ для обнаружения мошенничества"""
    print(" ИЩЕМ МОШЕННИЧЕСТВО С ПОМОЩЬЮ ИИ...")
    
    try:
        model = joblib.load("ai_fraud_model.pkl")
        data = pd.read_csv("prepared_transactions.csv")
        print(f" Загружено {len(data):,} транзакций для проверки")
        
    except Exception as e:
        print(f" Ошибка загрузки: {e}")
        print(" Сначала обучите модель!")
        return None
    
    features = check_columns_and_create_features(data)
    
    print(" АНАЛИЗИРУЕМ ТРАНЗАКЦИИ...")
    predictions = model.predict(features)
    data['ai_fraud_prediction'] = [1 if x == -1 else 0 for x in predictions]
    
    data['fraud_score'] = model.decision_function(features)
    
    fraud_count = data['ai_fraud_prediction'].sum()
    fraud_money = data[data['ai_fraud_prediction'] == 1]['amount'].sum()
    total_money = data['amount'].sum()
    
    print(f"\n РЕЗУЛЬТАТЫ РАБОТЫ ИИ:")
    print(f"   • Найдено подозрительных: {fraud_count:,} операций")
    print(f"   • Сумма риска: {fraud_money:,.0f} UZS")
    print(f"   • Уровень риска: {(fraud_count/len(data)*100):.1f}% транзакций")
    print(f"   • Финансовый риск: {(fraud_money/total_money*100):.1f}% от оборота")
    
    fraud_ops = data[data['ai_fraud_prediction'] == 1].copy()
    fraud_ops = fraud_ops.sort_values(['fraud_score', 'amount'], ascending=[True, False])
    
    print(f"\n ТОП-5 САМЫХ ПОДОЗРИТЕЛЬНЫХ ОПЕРАЦИЙ:")
    top_fraud = fraud_ops.head(5)
    for i, (idx, row) in enumerate(top_fraud.iterrows(), 1):
        print(f"   {i}. {row['amount']:,.0f} UZS (опасность: {row['fraud_score']:.2f})")
    
    fraud_ops.to_csv("Reports/ai_fraud_result.csv", index=False)
    
    report = fraud_ops[['user_id', 'amount', 'fraud_score', 'timestamp']].head(20)
    report.to_excel("short_report_sus.xlsx", index=False)
    
    print(f"\n СОХРАНЕНО:")
    print(f"   • Полный отчет: ai_fraud_prediction.csv")
    print(f"   • Для руководства: short_brief_sus.xlsx")
    print(f"   • Всего записей: {len(fraud_ops)} подозрительных операций")
    
    return data

def simple_fraud_detection():
    """Простой метод если ИИ не работает"""
    print(" ЗАПУСК ПРОСТОГО МЕТОДА ОБНАРУЖЕНИЯ...")
    
    try:
        data = pd.read_csv("prepared_transactions.csv")
    except:
        print(" Не могу загрузить данные!")
        return
    
    Q1 = data['amount'].quantile(0.25)
    Q3 = data['amount'].quantile(0.75)
    IQR = Q3 - Q1
    
    upper_bound = Q3 + 3 * IQR
    
    data['simple_fraud'] = (data['amount'] > upper_bound).astype(int)
    
    fraud_count = data['simple_fraud'].sum()
    fraud_money = data[data['simple_fraud'] == 1]['amount'].sum()
    
    print(f"\n РЕЗУЛЬТАТЫ ПРОСТОГО МЕТОДА:")
    print(f"   • Найдено аномалий: {fraud_count:,} операций")
    print(f"   • Сумма аномалий: {fraud_money:,.0f} UZS")
    print(f"   • Граница аномалий: {upper_bound:,.0f} UZS")
    
    simple_fraud = data[data['simple_fraud'] == 1].copy()
    simple_fraud.to_csv("Reports/simple_anomaly.csv", index=False)
    
    return data

if __name__ == "__main__":
    print("=" * 50)
    print(" СИСТЕМА ОБНАРУЖЕНИЯ МОШЕННИЧЕСТВА")
    print("=" * 50)
    
    model, feature_names = train_ai_model()
    
    if model is not None:
        print("\n" + "=" * 40)
        results = detect_fraud_with_ai()
        print("\n РАБОТА ИИ ЗАВЕРШЕНА!")
    else:
        print("\n ИИ НЕ СРАБОТАЛ, ИСПОЛЬЗУЕМ ПРОСТОЙ МЕТОД...")
        results = simple_fraud_detection()
        print("\n ПРОСТОЙ АНАЛИЗ ЗАВЕРШЕН!")
    
    print(" ДЛЯ ПРОСМОТРА РЕЗУЛЬТАТОВ:")
    print("   • Откройте файлы с результатами")
    print("   • Запустите:  analize_data.py для визуализации")