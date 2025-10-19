import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

print(" СОЗДАЕМ УНИВЕРСАЛЬНУЮ AI МОДЕЛЬ...")

def create_universal_model():
    """Создает простую и надежную модель"""
    
    try:
        data = pd.read_csv("prepared_transactions.csv")
        print(f" Загружено {len(data):,} транзакций")
        
        features = data[['amount']].copy()
        
        for col in ['total_1h', 'count_1h', 'time_diff_sec', 'hour', 'day_of_week']:
            if col in data.columns:
                features[col] = data[col].fillna(0)
        
        features = features.fillna(0)
        
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        print(" ОБУЧАЕМ МОДЕЛИ...")
        
        iso_forest = IsolationForest(
            n_estimators=100,
            contamination=0.05,
            random_state=42
        )
        iso_forest.fit(features_scaled)
        
        rf_model = None
        if 'is_fraud' in data.columns and data['is_fraud'].sum() > 5:
            rf_model = RandomForestClassifier(
                n_estimators=50,
                max_depth=10,
                random_state=42
            )
            rf_model.fit(features_scaled, data['is_fraud'])
        
        model_package = {
            'iso_forest': iso_forest,
            'rf_model': rf_model,
            'scaler': scaler,
            'feature_names': features.columns.tolist(),
            'model_type': 'universal_fraud_detector',
            'version': '2.0'
        }
        
        joblib.dump(model_package, "universal_ai_model.pkl")
        
        print(" УНИВЕРСАЛЬНАЯ МОДЕЛЬ СОХРАНЕНА!")
        print(f" Использовано фич: {len(features.columns)}")
        print(f" Файл: universal_ai_model.pkl")
        
        return model_package
        
    except Exception as e:
        print(f" Ошибка: {e}")
        return None

def predict_fraud(model_package, transaction_data):
    """Простое предсказание для API"""
    try:
        features = pd.DataFrame([{
            'amount': transaction_data['amount']
        }])
        
        for col in ['total_1h', 'count_1h', 'time_diff_sec', 'hour', 'day_of_week']:
            if col in transaction_data:
                features[col] = transaction_data[col]
            else:
                features[col] = 0
        
        features = features.fillna(0)
        
        features_scaled = model_package['scaler'].transform(features)
        
        predictions = []
        
        iso_pred = model_package['iso_forest'].predict(features_scaled)
        predictions.append((iso_pred == -1).astype(int)[0])
        
        if model_package['rf_model'] is not None:
            rf_pred = model_package['rf_model'].predict(features_scaled)
            predictions.append(rf_pred[0])
        
        fraud_score = np.mean(predictions) if predictions else 0
        fraud_prediction = fraud_score > 0.3
        
        return fraud_score, fraud_prediction
        
    except Exception as e:
        print(f" Ошибка предсказания: {e}")
        return 0, False

if __name__ == "__main__":
    model = create_universal_model()
    if model:
        print("\n ТЕСТИРУЕМ МОДЕЛЬ...")
        
        test_tx = {
            'amount': 15000000,
            'total_1h': 0,
            'count_1h': 1,
            'time_diff_sec': 3600,
            'hour': 14,
            'day_of_week': 1
        }
        
        score, is_fraud = predict_fraud(model, test_tx)
        print(f" Тестовая транзакция: {test_tx['amount']:,.0f} UZS")
        print(f" Результат: риск {score:.3f}, мошенничество: {is_fraud}")