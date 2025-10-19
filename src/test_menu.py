import pandas as pd
import sys
import os
from pathlib import Path
import subprocess
import time


def main():
    print(" ТЕСТОВОЕ МЕНЮ")
    
    while True:
        print("\n1 - Обновить данные")
        print("2 - Быстрый анализ")
        print("3 - Запуск ИИ")
        print("0 - Выход")
        
        choice = input("Выберите команду: ").strip()
        
        if choice == "1":
            print(" Запускаем обновление данных...")
            import subprocess
            subprocess.run(["python", "dummy_data_gen.py"])
            
        elif choice == "2":
            print(" Запускаем анализ...")
            import subprocess  
            subprocess.run(["python", "analize_data.py"])
            
        elif choice == "3":
            print(" Запускаем ИИ...")
            import subprocess
            subprocess.run(["python", "fraud_module.py"])
            
        elif choice == "0":
            print(" Выход")
            break
        else:
            print(" Неверная команда! Используйте 1, 2, 3 или 0")

if __name__ == "__main__":
    main()