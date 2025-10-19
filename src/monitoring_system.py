
import subprocess
import sys
import time
from pathlib import Path
import webbrowser

class MonitoringSystem:
    def __init__(self):
        self.metrics_exporter = None
        
    def check_dependencies(self):
        """Проверяет установлены ли нужные пакеты"""
        try:
            import prometheus_client
            print(" prometheus_client installed")
        except ImportError:
            print(" Installing prometheus_client...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "prometheus-client"])
            
    def setup_docker(self):
        """Настраивает Docker окружение"""
        print(" Setting up Docker monitoring stack...")
        
        self.create_config_files()
        
        print(" Starting Docker containers...")
        try:
            subprocess.run(["docker-compose", "up", "-d"], check=True)
            print(" Docker containers started successfully!")
        except subprocess.CalledProcessError:
            print(" Docker Compose failed. Make sure Docker is installed and running.")
            return False
            
        return True
    
    def create_config_files(self):
        """Создает конфигурационные файлы"""
        print(" Creating configuration files...")
        
        prometheus_config = """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'fraud-detection'
    static_configs:
      - targets: ['host.docker.internal:8000']
    scrape_interval: 10s
    scrape_timeout: 5s
    metrics_path: /
"""
        with open('prometheus.yml', 'w') as f:
            f.write(prometheus_config)
        
        print(" Configuration files created")
    
    def start_metrics_export(self):
        """Запускает экспорт метрик"""
        print(" Starting metrics exporter...")
        
        from metrics_exporter import FraudMetricsExporter
        self.metrics_exporter = FraudMetricsExporter(port=8000)
        self.metrics_exporter.start_metrics_server()
        self.metrics_exporter.run_continuous_export()
        
        print(" Metrics exporter running on http://localhost:8000")
    
    def open_dashboards(self):
        """Открывает веб-интерфейсы"""
        print(" Opening monitoring dashboards...")
        
        time.sleep(10)
        
        webbrowser.open("http://localhost:3000")
        print(" Grafana: http://localhost:3000 (admin/admin123)")
        
        webbrowser.open("http://localhost:9090")
        print(" Prometheus: http://localhost:9090")
        
        webbrowser.open("http://localhost:8000")
        print(" Metrics: http://localhost:8000")
    
    def show_instructions(self):
        """Показывает инструкции"""
        print("""
 MONITORING SYSTEM READY!

 DASHBOARDS:
  • Grafana:     http://localhost:3000
  • Prometheus:  http://localhost:9090  
  • Metrics:     http://localhost:8000

 GRAFANA SETUP:
  1. Open http://localhost:3000
  2. Login with admin/admin123
  3. Add Prometheus datasource:
     - URL: http://prometheus:9090
     - Access: Server (default)
  4. Import dashboard using JSON

 TO STOP:
  docker-compose down
""")
    
    def run(self):
        """Запускает всю систему мониторинга"""
        print(" BANK FRAUD DETECTION MONITORING")
        print("=" * 50)
        
        self.check_dependencies()
        
        if self.setup_docker():
            self.start_metrics_export()
            self.open_dashboards()
            self.show_instructions()
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n Shutting down monitoring system...")
        else:
            print(" Failed to start monitoring system")

if __name__ == "__main__":
    monitor = MonitoringSystem()
    monitor.run()