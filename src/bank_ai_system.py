import pandas as pd
import sys
import os
import subprocess
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from config import setup_directories, get_data_path, PATHS

class BankAISystem:
    def __init__(self):
        self.version = "2.0"
        self.results = {}
        setup_directories()
    
    def clear_screen(self):
        """Очищает экран консоли"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_menu(self):
        """Главное меню системы"""
        self.clear_screen()
        print(f"""
🏦 УМНАЯ СИСТЕМА БЕЗОПАСНОСТИ БАНКА v{self.version}
==================================================
         Структура проекта: /src | /Reports
==================================================

1️   ПОЛНЫЙ ЦИКЛ (данные → AI → отчеты)
2️   БЫСТРЫЙ АНАЛИЗ (текущая ситуация)  
3️   ПРОДВИНУТЫЙ AI (нейросети + ансамбли)
4️   REST API (режим реального времени)
5️   ДАШБОРДЫ (визуализация)
6️   ТЕСТ API (проверка интеграции)
7️   ОТКРЫТЬ ОТЧЕТЫ (папка Reports)

0️   ВЫХОД

==================================================
        """)
    
    def wait_for_enter(self):
        """Ждет нажатия Enter"""
        input("\n Нажмите Enter чтобы продолжить...")
    
    def run_script(self, script_name, args=None):
        """Запускает Python скрипт из папки src"""
        try:
            script_path = Path("src") / script_name
            if not script_path.exists():
                print(f" Файл {script_path} не найден!")
                return False
                
            print(f" Запускаем {script_name}...")
            cmd = [sys.executable, str(script_path)]
            if args:
                cmd.extend(args)
                
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            if result.returncode == 0:
                print(f" {script_name} выполнен успешно!")
                if result.stdout:
                    print(result.stdout)
            else:
                print(f" Ошибка в {script_name}:")
                if result.stderr:
                    print(result.stderr)
            return True
        except Exception as e:
            print(f" Не могу запустить {script_name}: {e}")
            return False
    
    def run_full_pipeline(self):
        """Полный цикл от данных до результатов"""
        print("\n ЗАПУСК ПОЛНОГО ЦИКЛА АНАЛИЗА...")
        
        steps = [
            ("dummy_data_gen.py", "СОЗДАЕМ ТЕСТОВЫЕ ДАННЫЕ"),
            ("prepare_dataset.py", "ПОДГОТАВЛИВАЕМ ДАННЫЕ"), 
            ("fraud_module.py", "ЗАПУСКАЕМ БАЗОВЫЙ AI"),
            ("analize_data.py", "ГЕНЕРИРУЕМ ОТЧЕТЫ")
        ]
        
        for script, description in steps:
            print(f"\n {description}...")
            if not self.run_script(script):
                print(f" Прервано на {script}")
                return
        
        print("\n ПОЛНЫЙ ЦИКЛ ЗАВЕРШЕН!")
        print(" Все отчеты созданы в папке Reports/")
    
    def quick_analysis(self):
        """Быстрый анализ текущей ситуации"""
        print("\n БЫСТРЫЙ АНАЛИЗ ТЕКУЩЕЙ СИТУАЦИИ...")
        
        try:
            data_path = get_data_path('prepared_data')
            if not data_path.exists():
                print(" Файл с данными не найден!")
                print(" Сначала запустите 'Полный цикл'")
                return
            
            data = pd.read_csv(data_path)
            total = len(data)
            
            if 'is_fraud' in data.columns:
                fraud = data['is_fraud'].sum()
                fraud_percent = (fraud / total * 100) if total > 0 else 0
                fraud_amount = data[data['is_fraud'] == 1]['amount'].sum()
            else:
                fraud = 0
                fraud_percent = 0
                fraud_amount = 0
            
            print(f"   • Активных транзакций: {total:,} шт.")
            print(f"   • Выявлено подозрительных: {fraud:,} шт.")
            print(f"   • Уровень риска: {fraud_percent:.1f}%")
            print(f"   • Сумма риска: {fraud_amount:,.0f} UZS")
            print(f"   • Средний чек: {data['amount'].mean():,.0f} UZS")
            
            # Анализ риска
            if fraud_percent > 5:
                risk = " ВЫСОКИЙ"
            elif fraud_percent > 2:
                risk = " СРЕДНИЙ" 
            else:
                risk = " НИЗКИЙ"
                
            print(f"   • УРОВЕНЬ РИСКА: {risk}")
                
        except Exception as e:
            print(f" Ошибка при анализе: {e}")
    
    def run_advanced_ai(self):
        """Запуск продвинутого AI"""
        print("\n ЗАПУСК ПРОДВИНУТОГО AI С НЕЙРОСЕТЯМИ...")
        self.run_script("advanced_ai.py")
    
    def run_api_server(self):
        """Запуск API сервера"""
        print("\n ЗАПУСК REST API СЕРВЕРА...")
        print("   Сервер запустится на http://localhost:8000")
        print("    Документация: http://localhost:8000/docs")
        print("    Для остановки: Ctrl+C")
        print("\n   Откройте новое окно терминала для тестирования...")
        self.wait_for_enter()
        self.run_script("fraud_api.py")
    
    def run_dashboard(self):
        """Запуск дашбордов"""
        print("\n ЗАПУСК ВИЗУАЛИЗАЦИИ...")
        self.run_script("dashboard.py")
    
    def test_api(self):
        """Тестирование API"""
        print("\n ТЕСТИРОВАНИЕ REST API...")
        self.run_script("test_api.py")
    
    def open_reports(self):
        """Открывает папку с отчетами"""
        reports_dir = PATHS['reports']
        print(f"\n ОТКРЫВАЕМ ПАПКУ С ОТЧЕТАМИ...")
        print(f"   Путь: {reports_dir}")
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(reports_dir)
            elif os.name == 'posix':  # macOS, Linux
                subprocess.run(['open', reports_dir] if sys.platform == 'darwin' else ['xdg-open', reports_dir])
            print(" Папка открыта!")
        except Exception as e:
            print(f" Не удалось открыть папку: {e}")
            print(f" Откройте вручную: {reports_dir}")
    
    def handle_choice(self, choice):
        """Обрабатывает выбор пользователя"""
        if choice == "1":
            self.run_full_pipeline()
        elif choice == "2":
            self.quick_analysis()
        elif choice == "3":
            self.run_advanced_ai()
        elif choice == "4":
            self.run_api_server()
        elif choice == "5":
            self.run_dashboard()
        elif choice == "6":
            self.test_api()
        elif choice == "7":
            self.open_reports()
        elif choice == "0":
            print("\n До свидания!")
            return False
        else:
            print(" Неверный выбор! Пожалуйста, выберите число от 0 до 7")
        
        return True
    
    def run(self):
        """Запускает главное меню"""
        print("Загрузка системы...")
        time.sleep(1)
        
        running = True
        while running:
            self.show_menu()
            
            try:
                choice = input(" Введите номер команды (0-7): ").strip()
                running = self.handle_choice(choice)
                
                if running:
                    self.wait_for_enter()
                    
            except KeyboardInterrupt:
                print("\n\n Программа прервана пользователем")
                break
            except Exception as e:
                print(f"\n Неожиданная ошибка: {e}")
                self.wait_for_enter()

if __name__ == "__main__":
    system = BankAISystem()
    system.run()