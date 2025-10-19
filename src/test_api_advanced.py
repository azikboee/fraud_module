import requests
import json
import time
from datetime import datetime
import pandas as pd

class APITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    def test_health(self):
        """Тестирует health endpoint"""
        print("1.  ТЕСТИРУЕМ HEALTH CHECK...")
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"    Status: {data['status']}")
                print(f"    Model loaded: {data['model_loaded']}")
                print(f"    Total checks: {data['total_checks']}")
                if data['models_available']:
                    print(f"    Models: {', '.join(data['models_available'])}")
                return True
            else:
                print(f"    Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"    API not available: {e}")
            return False
    
    def test_single_transactions(self):
        """Тестирует одиночные транзакции"""
        print("\n2.  ТЕСТИРУЕМ ОДИНОЧНЫЕ ТРАНЗАКЦИИ...")
        
        test_cases = [
            {
                "user_id": "user_001", 
                "amount": 50000, 
                "merchant": "Korzinka",
                "description": "Нормальная покупка"
            },
            {
                "user_id": "user_002", 
                "amount": 15000000, 
                "merchant": "AutoShop",
                "description": "Очень крупная покупка"
            },
            {
                "user_id": "user_003", 
                "amount": 500, 
                "merchant": "Online",
                "description": "Подозрительно мелкая сумма"
            },
            {
                "user_id": "vip_client", 
                "amount": 500000, 
                "merchant": "Restaurant",
                "description": "Средняя сумма, VIP клиент"
            },
            {
                "user_id": "nocturnal_user", 
                "amount": 2000000, 
                "merchant": "NightClub",
                "timestamp": "2024-01-01T03:00:00",
                "description": "Ночная операция"
            }
        ]
        
        for i, tx in enumerate(test_cases, 1):
            print(f"\n    Тест {i}: {tx['description']}")
            print(f"       {tx['user_id']} |  {tx['amount']:,.0f} UZS")
            
            response = requests.post(f"{self.base_url}/check", json=tx)
            
            if response.status_code == 200:
                result = response.json()
                self.results.append(result)
                
                status_icon = "🔴" if result['is_suspicious'] else "🟢"
                print(f"      {status_icon} Риск: {result['risk_level']} ({result['risk_score']:.3f})")
                print(f"       Модель: {result['model_used']}")
                
                if result['reasons']:
                    print(f"       Причины: {', '.join(result['reasons'])}")
            else:
                print(f"       Ошибка: {response.status_code}")
    
    def test_batch_processing(self):
        """Тестирует пакетную обработку"""
        print("\n3.  ТЕСТИРУЕМ ПАКЕТНУЮ ОБРАБОТКУ...")
        
        batch_data = [
            {"user_id": "user_101", "amount": 100000, "merchant": "Shop1"},
            {"user_id": "user_102", "amount": 25000000, "merchant": "Luxury"},
            {"user_id": "user_103", "amount": 1500000, "merchant": "Electronics"},
            {"user_id": "user_104", "amount": 800, "merchant": "Online"},
            {"user_id": "user_105", "amount": 5000000, "merchant": "Travel"}
        ]
        
        response = requests.post(f"{self.base_url}/batch-check", json=batch_data)
        
        if response.status_code == 200:
            batch_result = response.json()
            print(f"    Проверено: {batch_result['checked_count']} транзакций")
            print(f"    Подозрительных: {batch_result['suspicious_count']}")
            
            suspicious_tx = [tx for tx in batch_result['results'] if tx['is_suspicious']]
            print(f"    Эффективность: {(len(suspicious_tx)/len(batch_result['results'])*100):.1f}%")
            
            self.results.extend(batch_result['results'])
        else:
            print(f"    Ошибка пакетной обработки: {response.status_code}")
    
    def test_model_reload(self):
        """Тестирует перезагрузку модели"""
        print("\n4.  ТЕСТИРУЕМ ПЕРЕЗАГРУЗКУ МОДЕЛИ...")
        
        response = requests.post(f"{self.base_url}/reload-model")
        
        if response.status_code == 200:
            result = response.json()
            print(f"    Перезагрузка: {result['message']}")
            print(f"    Модель загружена: {result['model_loaded']}")
        else:
            print(f"    Ошибка перезагрузки: {response.status_code}")
    
    def generate_report(self):
        """Генерирует отчет по тестированию"""
        print("\n5.  ГЕНЕРИРУЕМ ОТЧЕТ...")
        
        if not self.results:
            print("   Нет данных для отчета")
            return
        
        df = pd.DataFrame(self.results)
        
        total_tx = len(df)
        suspicious_tx = df['is_suspicious'].sum()
        avg_risk_score = df['risk_score'].mean()
        
        risk_distribution = df['risk_level'].value_counts()
        
        print(f"\n СВОДКА ТЕСТИРОВАНИЯ:")
        print(f"   • Всего проверено: {total_tx} транзакций")
        print(f"   • Подозрительных: {suspicious_tx} ({suspicious_tx/total_tx*100:.1f}%)")
        print(f"   • Средний риск: {avg_risk_score:.3f}")
        print(f"   • Распределение рисков:")
        for level, count in risk_distribution.items():
            print(f"     - {level}: {count} tx")
        
        report_filename = f"API_Test_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(report_filename, index=False)
        print(f"    Детальный отчет сохранен: {report_filename}")
        
        return df
    
    def run_full_test(self):
        """Запускает полное тестирование"""
        print(" РАСШИРЕННОЕ ТЕСТИРОВАНИЕ API")
        print("=" * 50)
        
        if not self.test_health():
            print(" API недоступен, тестирование прервано")
            return
        
        self.test_single_transactions()
        self.test_batch_processing()
        self.test_model_reload()
        
        self.generate_report()
        
        print("\n ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
        print(f" Документация: {self.base_url}/docs")

def main():
    """Основная функция"""
    tester = APITester()
    tester.run_full_test()

if __name__ == "__main__":
    main()