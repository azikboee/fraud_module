import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

try:
    import tensorflow as tf
    from tensorflow import keras
    layers = tf.keras.layers
    TENSORFLOW_AVAILABLE = True
    print(" TensorFlow доступен")
except ImportError:
    print("  TensorFlow не установлен, используем только sklearn модели")
    TENSORFLOW_AVAILABLE = False

print(" ЗАПУСК ИИ...")

class AdvancedFraudAI:
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        self.required_columns = ['amount']  # Мин колонки
        
    def validate_data(self, data):

        print(" ПРОВЕРЯЕМ...")
        
        missing_columns = [col for col in self.required_columns if col not in data.columns]
        if missing_columns:
            print(f" Отсутствуют обязательные колонки: {missing_columns}")
            return False
        
        print(f" Доступные колонки: {list(data.columns)}")
        return True
    
    def create_features(self, data):
        print(" СОЗДАЕМ ПРИЗНАКИ...")
        features = data[['amount']].copy()

        if 'user_id' in data.columns:
            print("    Добавляем статистики по пользователям...")
            try:
                user_stats = data.groupby('user_id')['amount'].agg([
                    'mean', 'std', 'min', 'max', 'count'
                ]).add_prefix('user_').fillna(0)
                
                features = features.merge(user_stats, left_on='user_id', right_index=True, how='left')
                features = features.fillna(0) 
            except Exception as e:
                print(f"     Ошибка при создании user stats: {e}")
        
        if 'timestamp' in data.columns:
            print("    Добавляем временные признаки...")
            try:
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                features['hour'] = data['timestamp'].dt.hour
                features['day_of_week'] = data['timestamp'].dt.dayofweek
                features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
            except Exception as e:
                print(f"     Ошибка при создании временных признаков: {e}")
        
        if 'user_id' in data.columns and 'timestamp' in data.columns:
            print("    Добавляем поведенческие паттерны...")
            try:
                data['prev_amount'] = data.groupby('user_id')['amount'].shift(1)
                features['amount_ratio'] = data['amount'] / data['prev_amount']
                features['amount_ratio'] = features['amount_ratio'].replace([np.inf, -np.inf], 1).fillna(1)
            except Exception as e:
                print(f"     Ошибка при создании поведенческих признаков: {e}")
        print("    Добавляем статистические аномалии...")
        try:
            features['amount_zscore'] = np.abs(
                (data['amount'] - data['amount'].mean()) / data['amount'].std()
            ).fillna(0)
        except:
            features['amount_zscore'] = 0

        additional_columns = ['total_1h', 'count_1h', 'time_diff_sec', 'user_mean', 'user_std']
        for col in additional_columns:
            if col in data.columns:
                features[col] = data[col].fillna(0)
        
        features = features.fillna(0)
        
        self.feature_names = features.columns.tolist()
        print(f" Создано {len(features.columns)} признаков: {self.feature_names}")
        
        return features
    
    def train_models(self, data):
        """Обучает несколько AI моделей с обработкой ошибок"""
        print(" ОБУЧАЕМ АНСАМБЛЬ МОДЕЛЕЙ...")
        
        # Проверка данных
        if not self.validate_data(data):
            return None
        
        X = self.create_features(data)
        X_scaled = self.scaler.fit_transform(X)
        
        y = data['is_fraud'] if 'is_fraud' in data.columns else None
        
        trained_models = 0
        
        print("1. Обучаем Isolation Forest...")
        try:
            iso_forest = IsolationForest(
                n_estimators=100,
                contamination=0.05,
                random_state=42
            )
            iso_forest.fit(X_scaled)
            self.models['isolation_forest'] = iso_forest
            trained_models += 1
            print("    Isolation Forest обучен")
        except Exception as e:
            print(f"    Ошибка при обучении Isolation Forest: {e}")
        
        if y is not None and y.sum() > 5 and TENSORFLOW_AVAILABLE:
            print("2. Обучаем нейронную сеть...")
            try:
                from sklearn.utils import class_weight
                class_weights = class_weight.compute_class_weight(
                    'balanced',
                    classes=np.unique(y),
                    y=y
                )

                model = keras.Sequential([
                    layers.Dense(64, activation='relu', input_shape=(X_scaled.shape[1],)),
                    layers.Dropout(0.3),
                    layers.Dense(32, activation='relu'),
                    layers.Dropout(0.3),
                    layers.Dense(1, activation='sigmoid')
                ])
                
                model.compile(
                    optimizer='adam',
                    loss='binary_crossentropy',
                    metrics=['accuracy']
                )

                history = model.fit(
                    X_scaled, y,
                    epochs=30,  
                    batch_size=32,
                    validation_split=0.2,
                    class_weight=dict(enumerate(class_weights)),
                    verbose=0
                )
                
                self.models['neural_network'] = model
                trained_models += 1
                print(f"   Нейросеть обучена (точность: {history.history['accuracy'][-1]:.3f})")
            except Exception as e:
                print(f"    Ошибка при обучении нейросети: {e}")
        else:
            if not TENSORFLOW_AVAILABLE:
                print("     TensorFlow не доступен, пропускаем нейросеть")
            elif y is None or y.sum() <= 5:
                print("     Недостаточно размеченных данных для нейросети")
        
        if y is not None:
            print("3. Обучаем Random Forest...")
            try:
                rf = RandomForestClassifier(
                    n_estimators=50,
                    max_depth=10,
                    random_state=42
                )
                rf.fit(X_scaled, y)
                self.models['random_forest'] = rf
                trained_models += 1
                print(f"    Random Forest обучен (точность: {rf.score(X_scaled, y):.3f})")
            except Exception as e:
                print(f"    Ошибка при обучении Random Forest: {e}")
        
        print(f" Обучено {trained_models} моделей из {len(self.models)} попыток")
        return self.models
    
    def predict_ensemble(self, data):
        """Предсказание с помощью ансамбля моделей"""
        print(" ЗАПУСК АНСАМБЛЯ МОДЕЛЕЙ...")
        
        if not self.models:
            print(" Нет обученных моделей!")
            return data
        
        X = self.create_features(data)
        X_scaled = self.scaler.transform(X)
        
        predictions = {}
        
        if 'isolation_forest' in self.models:
            try:
                iso_pred = self.models['isolation_forest'].predict(X_scaled)
                predictions['isolation'] = (iso_pred == -1).astype(int)
            except Exception as e:
                print(f" Ошибка в Isolation Forest: {e}")
        
        if 'neural_network' in self.models and TENSORFLOW_AVAILABLE:
            try:
                nn_pred = self.models['neural_network'].predict(X_scaled, verbose=0)
                predictions['neural_net'] = (nn_pred > 0.5).astype(int).flatten()
            except Exception as e:
                print(f" Ошибка в нейросети: {e}")
        
        if 'random_forest' in self.models:
            try:
                rf_pred = self.models['random_forest'].predict(X_scaled)
                predictions['random_forest'] = rf_pred
            except Exception as e:
                print(f" Ошибка в Random Forest: {e}")
        
        if predictions:
            ensemble_pred = np.mean(list(predictions.values()), axis=0)
            data['ai_fraud_score'] = ensemble_pred
            data['ai_fraud_prediction'] = (ensemble_pred > 0.3).astype(int)
            print(f" Ансамбль предсказаний создан ({len(predictions)} моделей)")
        else:
            print("Не удалось получить предсказания от моделей")
            data['ai_fraud_score'] = 0
            data['ai_fraud_prediction'] = 0
        
        return data

def main():
    """Основная функция"""
    print("=" * 60)
    print(" ПРОДВИНУТАЯ СИСТЕМА ИСКУССТВЕННОГО ИНТЕЛЛЕКТА")
    print("=" * 60)
    
    try:
        data = pd.read_csv("data/prepared_transactions.csv")
        print(f"Загружено {len(data):,} транзакций")
        
        ai_system = AdvancedFraudAI()
        models = ai_system.train_models(data)
        
        if not models:
            print(" Не удалось обучить модели!")
            return
    
        results = ai_system.predict_ensemble(data)

        fraud_count = results['ai_fraud_prediction'].sum()
        total_count = len(results)
        
        print(f"\n РЕЗУЛЬТАТЫ ПРОДВИНУТОГО AI:")
        print(f"   • Обнаружено подозрительных: {fraud_count:,} операций")
        print(f"   • Уровень риска: {(fraud_count/total_count*100):.1f}%")
        print(f"   • Использовано моделей: {len(models)}")
        
        results.to_csv("data/ADVANCED_AI_RESULTS.csv", index=False)
        joblib.dump(ai_system, 'advanced_ai_system.pkl')
        
        print(f"\n Результаты сохранены:")
        print("   • ADVANCED_AI_RESULTS.csv - полные данные")
        print("   • advanced_ai_system.pkl - обученная система AI")
        
    except Exception as e:
        print(f" Ошибка: {e}")
        print(" Убедитесь что prepared_transactions.csv существует и содержит данные")

if __name__ == "__main__":
    main()