import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def create_executive_dashboard():
    """Создает дашборд для руководства"""
    print(" СОЗДАЕМ ДАШБОРД ДЛЯ РУКОВОДСТВА...")
    
    try:
        data = pd.read_csv("prepared_transactions.csv")
    except:
        print(" Нет данных для дашборда")
        return
    
    
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('ДАШБОРД БЕЗОПАСНОСТИ БАНКА\nАнализ мошеннических операций', 
                fontsize=16, fontweight='bold')
    
    fraud_count = data['is_fraud'].sum() if 'is_fraud' in data.columns else 0
    normal_count = len(data) - fraud_count
    
    axes[0,0].pie([normal_count, fraud_count], 
                 labels=['НОРМАЛЬНЫЕ', 'ПОДОЗРИТЕЛЬНЫЕ'],
                 colors=['#2ecc71', '#e74c3c'],
                 autopct='%1.1f%%',
                 startangle=90)
    axes[0,0].set_title('РАСПРЕДЕЛЕНИЕ ТРАНЗАКЦИЙ')
    
    if 'user_id' in data.columns:
        user_risk = data.groupby('user_id').agg({
            'amount': ['count', 'sum'],
            'is_fraud': 'sum'
        }).round(2)
        
        user_risk.columns = ['count', 'total_amount', 'fraud_count']
        user_risk['risk_percent'] = (user_risk['fraud_count'] / user_risk['count'] * 100)
        top_risky = user_risk.nlargest(5, 'risk_percent')
        
        axes[0,1].bar(range(len(top_risky)), top_risky['risk_percent'], color='#e74c3c')
        axes[0,1].set_title(' ТОП-5 КЛИЕНТОВ ПО РИСКУ')
        axes[0,1].set_ylabel('Процент риска (%)')
        axes[0,1].set_xticks(range(len(top_risky)))
        axes[0,1].set_xticklabels([f'Клиент {i+1}' for i in range(len(top_risky))])
    
    axes[1,0].hist(data['amount'], bins=50, alpha=0.7, color='#3498db')
    axes[1,0].set_title(' РАСПРЕДЕЛЕНИЕ СУММ ТРАНЗАКЦИЙ')
    axes[1,0].set_xlabel('Сумма (UZS)')
    axes[1,0].set_ylabel('Количество')
    
    if 'timestamp' in data.columns:
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['hour'] = data['timestamp'].dt.hour
        hourly_activity = data.groupby('hour').size()
        
        axes[1,1].plot(hourly_activity.index, hourly_activity.values, 
                      marker='o', linewidth=2, color='#9b59b6')
        axes[1,1].set_title(' АКТИВНОСТЬ ПО ЧАСАМ')
        axes[1,1].set_xlabel('Час суток')
        axes[1,1].set_ylabel('Количество транзакций')
        axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('ДАШБОРД_РУКОВОДСТВА.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print(" ДАШБОРД СОХРАНЕН: ДАШБОРД_РУКОВОДСТВА.png")

if __name__ == "__main__":
    create_executive_dashboard()