import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

plt.rcParams['font.size'] = 10
plt.rcParams['figure.figsize'] = (11, 9)

class SimpleFraudAnalyzer:
    def __init__(self):
        self.results = {}
        
    def check_files(self):
        """Проверка файлов простым языком"""
        print(" ПРОВЕРЯЕМ ФАЙЛЫ...")
        
        files = {
            "dummy_transactions.csv": "Тестовые транзакции",
            "prepared_transactions.csv": "Обработанные данные"
        }
        
        all_ok = True
        for file, description in files.items():
            if Path(file).exists():
                size = Path(file).stat().st_size
                if size > 100:  # файл не пустой
                    print(f"    {description} - ГОТОВ")
                else:
                    print(f"    {description} - ПУСТОЙ!")
                    all_ok = False
            else:
                print(f"    {description} - НЕТ ФАЙЛА!")
                all_ok = False
                
        if not all_ok:
            print("\n ПРОБЛЕМА: Нужно создать данные!")
            print("    Запусти: python dummy_data_gen.py")
            print("    Затем: python prepare_dataset.py")
            return False
            
        print(" ВСЕ ФАЙЛЫ ГОТОВЫ К АНАЛИЗУ!")
        return True
    
    def load_data(self):
        """Загрузка данных простым способом"""
        print("\n ЗАГРУЗКА ДАННЫХ...")
        
        try:
            self.df = pd.read_csv("prepared_transactions.csv")
            print(f" Загружено {len(self.df):,} транзакций")
            return True
        except:
            print(" Ошибка загрузки файла")
            return False
    
    def analyze_simple(self):
        """Анализ простыми словами"""
        print("\n АНАЛИЗИРУЕМ ДАННЫЕ...")
        
        total = len(self.df)
        fraud_count = self.df['is_fraud'].sum()
        fraud_percent = (fraud_count / total) * 100
        
        avg_amount = self.df['amount'].mean()
        max_amount = self.df['amount'].max()
        total_money = self.df['amount'].sum()
        fraud_money = self.df[self.df['is_fraud'] == 1]['amount'].sum()
        
        self.results = {
            'total_transactions': total,
            'fraud_count': fraud_count,
            'fraud_percent': fraud_percent,
            'avg_amount': avg_amount,
            'max_amount': max_amount,
            'total_money': total_money,
            'fraud_money': fraud_money
        }
        
        print(" ОСНОВНЫЕ ЦИФРЫ:")
        print(f"   • Всего транзакций: {total:,} шт.")
        print(f"   • Общая сумма: {total_money:,.0f} UZS")
        print(f"   • Средний чек: {avg_amount:,.0f} UZS")
        print(f"   • Самая крупная: {max_amount:,.0f} UZS")
        
        print(f"\n ВЫЯВЛЕНО МОШЕННИЧЕСТВО:")
        print(f"   • Подозрительных операций: {fraud_count:,} шт.")
        print(f"   • Это {fraud_percent:.1f}% от всех транзакций")
        print(f"   • Сумма риска: {fraud_money:,.0f} UZS")
        
        if fraud_percent > 5:
            print("     ВЫСОКИЙ УРОВЕНЬ РИСКА!")
        elif fraud_percent > 2:
            print("     СРЕДНИЙ УРОВЕНЬ РИСКА")
        else:
            print("    НИЗКИЙ УРОВЕНЬ РИСКА")
    
    def create_simple_charts(self):
        """Создание простых и понятных графиков"""
        print("\n СОЗДАЕМ ГРАФИКИ...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('АНАЛИЗ МОШЕННИЧЕСКИХ ОПЕРАЦИЙ\nПростой отчет для руководства', 
                    fontsize=16, fontweight='bold')
        
        fraud_count = self.results['fraud_count']
        normal_count = self.results['total_transactions'] - fraud_count
        
        ax1.pie([normal_count, fraud_count], 
               labels=['НОРМАЛЬНЫЕ', 'ПОДОЗРИТЕЛЬНЫЕ'],
               colors=['lightgreen', 'red'],
               autopct='%1.1f%%',
               startangle=90)
        ax1.set_title(' Соотношение транзакций')
        
        categories = ['Всего транзакций', 'Подозрительные', 'Средний чек', 'Макс. сумма']
        values = [
            self.results['total_transactions'] / 1000,  # в тысячах
            self.results['fraud_count'],
            self.results['avg_amount'] / 1000000,  # в миллионах
            self.results['max_amount'] / 1000000   # в миллионах
        ]
        colors = ['blue', 'red', 'green', 'orange']
        
        bars = ax2.bar(categories, values, color=colors, alpha=0.7)
        ax2.set_title(' Основные показатели')
        ax2.set_ylabel('Тыс.шт / млн.UZS')
        
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                    f'{value:.1f}', ha='center', va='bottom')
        
        normal_trans = self.df[self.df['is_fraud'] == 0]['amount']
        fraud_trans = self.df[self.df['is_fraud'] == 1]['amount']
        
        normal_show = normal_trans[normal_trans <= 10000000]
        fraud_show = fraud_trans[fraud_trans <= 10000000]
        
        ax3.hist(normal_show, bins=50, alpha=0.7, color='lightblue', label='НОРМАЛЬНЫЕ')
        ax3.hist(fraud_show, bins=50, alpha=0.7, color='red', label='ПОДОЗРИТЕЛЬНЫЕ')
        ax3.set_title(' Распределение сумм транзакций')
        ax3.set_xlabel('Сумма (UZS)')
        ax3.set_ylabel('Количество')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        if 'timestamp' in self.df.columns:
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df['date'] = self.df['timestamp'].dt.date
            
            daily_fraud = self.df[self.df['is_fraud'] == 1].groupby('date').size()
            daily_normal = self.df[self.df['is_fraud'] == 0].groupby('date').size()
            
            ax4.plot(daily_normal.index, daily_normal.values, label='Нормальные', linewidth=2)
            ax4.plot(daily_fraud.index, daily_fraud.values, label='Подозрительные', 
                    color='red', linewidth=2, marker='o')
            ax4.set_title(' Транзакции по дням')
            ax4.set_xlabel('Дата')
            ax4.set_ylabel('Количество транзакций')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
        else:
            top_fraud = self.df[self.df['is_fraud'] == 1].nlargest(10, 'amount')
            ax4.barh(range(len(top_fraud)), top_fraud['amount'] / 1000000, color='red')
            ax4.set_yticks(range(len(top_fraud)))
            ax4.set_yticklabels([f'Транз. {i+1}' for i in range(len(top_fraud))])
            ax4.set_title(' Топ-10 подозрительных транзакций')
            ax4.set_xlabel('Сумма (млн UZS)')
        
        plt.tight_layout()
        plt.savefig('Reports/simple_report.png', dpi=150, bbox_inches='tight')
        print(" Графики сохранены в файл: 'simple_report.png'")
        plt.show()
    
    def generate_simple_report(self):
        """Генерация простого текстового отчета"""
        print("\n СОЗДАЕМ ПРОСТОЙ ОТЧЕТ...")
        
        report = f"""
=== ПРОСТОЙ ОТЧЕТ ПО МОШЕННИЧЕСТВУ ===

 ОСНОВНЫЕ ЦИФРЫ:
• Всего проверено транзакций: {self.results['total_transactions']:,} шт.
• Выявлено подозрительных: {self.results['fraud_count']:,} шт.
• Уровень риска: {self.results['fraud_percent']:.1f}%

 ФИНАНСОВЫЕ ПОКАЗАТЕЛИ:
• Общая сумма операций: {self.results['total_money']:,.0f} UZS
• Сумма подозрительных операций: {self.results['fraud_money']:,.0f} UZS
• Средняя сумма транзакции: {self.results['avg_amount']:,.0f} UZS

 РЕКОМЕНДАЦИИ:
"""
        
        if self.results['fraud_percent'] > 5:
            report += "•   КРИТИЧЕСКИЙ УРОВЕНЬ! Срочно проверьте систему безопасности\n"
            report += "•  Провести детальный анализ всех подозрительных операций\n"
            report += "•  Усилить верификацию для крупных транзакций\n"
        elif self.results['fraud_percent'] > 2:
            report += "•   Повышенный уровень риска. Рекомендуется:\n"
            report += "•  Анализировать подозрительные транзакции ежедневно\n"
            report += "•  Усилить мониторинг нестандартных операций\n"
        else:
            report += "•  Система работает стабильно. Рекомендуется:\n"
            report += "•  Продолжать регулярный мониторинг\n"
            report += "•  Обновлять правила обнаружения ежемесячно\n"
        
        report += f"\n Отчет создан: {pd.Timestamp.now().strftime('%d.%m.%Y %H:%M')}"
        
        with open('ПРОСТОЙ_ОТЧЕТ_ТЕКСТ.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(" Текстовый отчет сохранен: 'ПРОСТОЙ_ОТЧЕТ_ТЕКСТ.txt'")
    
    def run_complete_analysis(self):
        """Полный анализ в одном методе"""
        print("=" * 60)
        print(" ЗАПУСК ПРОСТОГО АНАЛИЗА МОШЕННИЧЕСТВА")
        print("=" * 60)
        
        if not self.check_files():
            return
        
        if not self.load_data():
            return
        
        self.analyze_simple()
        
        self.create_simple_charts()
        
        self.generate_simple_report()
        
        print("\n" + "=" * 60)
        print(" АНАЛИЗ ЗАВЕРШЕН!")
        print(" Созданы файлы:")
        print("   • ПРОСТОЙ_ОТЧЕТ_МОШЕННИЧЕСТВО.png")
        print("   • ПРОСТОЙ_ОТЧЕТ_ТЕКСТ.txt")
        print("=" * 60)

if __name__ == "__main__":
    analyzer = SimpleFraudAnalyzer()
    analyzer.run_complete_analysis()