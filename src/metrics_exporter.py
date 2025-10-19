from prometheus_client import start_http_server, Gauge, Counter, Histogram
import pandas as pd
import time
import threading
from datetime import datetime
import logging

class FraudMetricsExporter:
    def __init__(self, port=8000):
        self.port = port
        
        self.transactions_total = Counter(
            'fraud_transactions_total', 
            'Total number of transactions',
            ['status']
        )
        
        self.fraud_transactions = Gauge(
            'fraud_suspicious_transactions', 
            'Number of suspicious transactions'
        )
        
        self.fraud_amount = Gauge(
            'fraud_suspicious_amount_total',
            'Total amount of suspicious transactions'
        )
        
        self.risk_level = Gauge(
            'fraud_risk_level_percent',
            'Current fraud risk level in percent'
        )
        
        self.transaction_amount = Histogram(
            'fraud_transaction_amount',
            'Transaction amount distribution',
            buckets=[1000, 10000, 100000, 500000, 1000000, 5000000, 10000000, 50000000]
        )
        
        self.model_accuracy = Gauge(
            'fraud_model_accuracy',
            'AI model accuracy score'
        )
        
        self.last_update = Gauge(
            'fraud_last_update_timestamp',
            'Timestamp of last data update'
        )
        
    def start_metrics_server(self):
        """Запускает сервер метрик"""
        print(f" Starting Prometheus metrics server on port {self.port}...")
        start_http_server(self.port)
        print(" Metrics server is running!")
        
    def update_metrics(self):
        """Обновляет все метрики из данных"""
        try:
            data = pd.read_csv("prepared_transactions.csv")
            
            total_transactions = len(data)
            fraud_count = data['is_fraud'].sum() if 'is_fraud' in data.columns else 0
            normal_count = total_transactions - fraud_count
            
            self.transactions_total.labels(status='normal').inc(normal_count)
            self.transactions_total.labels(status='suspicious').inc(fraud_count)
            
            self.fraud_transactions.set(fraud_count)
            
            if fraud_count > 0:
                fraud_amount = data[data['is_fraud'] == 1]['amount'].sum()
                self.fraud_amount.set(fraud_amount)
            
            risk_percent = (fraud_count / total_transactions * 100) if total_transactions > 0 else 0
            self.risk_level.set(risk_percent)
            
            for amount in data['amount'].head(1000):  # Ограничил для производительности
                self.transaction_amount.observe(amount)
            
            self.last_update.set_to_current_time()
            
            logging.info(f" Metrics updated: {fraud_count} fraud transactions ({risk_percent:.1f}%)")
            
        except Exception as e:
            logging.error(f" Error updating metrics: {e}")
    
    def run_continuous_export(self):
        """Запускает непрерывный экспорт метрик"""
        def update_loop():
            while True:
                self.update_metrics()
                time.sleep(30)  # Обновляем каждые 30 секунд
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
        print(" Continuous metrics export started...")

def demo_metrics():
    """Демонстрация работы метрик"""
    exporter = FraudMetricsExporter(port=8000)
    exporter.start_metrics_server()
    exporter.run_continuous_export()
    
    print(" Demo metrics are being generated...")
    print(" View metrics at: http://localhost:8000")
    print("  Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n Metrics server stopped")

if __name__ == "__main__":
    demo_metrics()