from prometheus_client import start_http_server, Gauge, Counter
import pandas as pd
import time
import threading
import webbrowser

class SimpleMonitor:
    def __init__(self, port=8000):
        self.port = port
        
        # Простые метрики
        self.total_transactions = Gauge('fraud_total_tx', 'Total transactions')
        self.suspicious_transactions = Gauge('fraud_suspicious_tx', 'Suspicious transactions') 
        self.risk_percent = Gauge('fraud_risk_percent', 'Risk percentage')
        self.suspicious_amount = Gauge('fraud_suspicious_amount', 'Suspicious amount')
        
    def start(self):
        """Запускает мониторинг"""
        print(" Starting simple monitoring...")
        start_http_server(self.port)
        
        def update_loop():
            while True:
                self.update_metrics()
                time.sleep(10)
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
        
        print(f" Monitoring running on http://localhost:{self.port}")
        webbrowser.open(f"http://localhost:{self.port}")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n Monitoring stopped")
    
    def update_metrics(self):
        """Обновляет метрики из данных"""
        try:
            data = pd.read_csv("prepared_transactions.csv")
            
            total = len(data)
            fraud = data['is_fraud'].sum() if 'is_fraud' in data.columns else 0
            risk = (fraud / total * 100) if total > 0 else 0
            
            self.total_transactions.set(total)
            self.suspicious_transactions.set(fraud) 
            self.risk_percent.set(risk)
            
            if fraud > 0:
                amount = data[data['is_fraud'] == 1]['amount'].sum()
                self.suspicious_amount.set(amount)
                
            print(f" Metrics updated: {fraud}/{total} suspicious ({risk:.1f}%)")
            
        except Exception as e:
            print(f" Error updating metrics: {e}")

if __name__ == "__main__":
    monitor = SimpleMonitor(8000)
    monitor.start()