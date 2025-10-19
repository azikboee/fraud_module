# src/database.py
"""
🗄️ БЕЗОПАСНАЯ РАБОТА С POSTGRESQL
С защитой от SQL инъекций
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from contextlib import contextmanager
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost:5432/fraud_db')
    
    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для подключения к БД"""
        conn = None
        try:
            conn = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def log_transaction(self, user_id, amount, is_fraud, fraud_score, risk_level, merchant=None):
        """Безопасное логирование транзакции в БД"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Используем параметризованные запросы для защиты от SQL инъекций
                    query = """
                    INSERT INTO transactions 
                    (user_id, amount, merchant, is_fraud, fraud_score, risk_level) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """
                    cur.execute(query, (user_id, amount, merchant, is_fraud, fraud_score, risk_level))
                    conn.commit()
                    return cur.fetchone()['id']
        except Exception as e:
            logger.error(f"Error logging transaction: {e}")
            return None
    
    def log_api_request(self, endpoint, method, user_id, amount, response_time, status_code, is_suspicious):
        """Логирование API запросов"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                    INSERT INTO api_logs 
                    (endpoint, method, user_id, amount, response_time, status_code, is_suspicious) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cur.execute(query, (endpoint, method, user_id, amount, response_time, status_code, is_suspicious))
                    conn.commit()
        except Exception as e:
            logger.error(f"Error logging API request: {e}")
    
    def get_fraud_patterns(self):
        """Получение паттернов мошенничества из БД"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    query = "SELECT pattern_name, sql_condition FROM fraud_patterns WHERE is_active = true"
                    cur.execute(query)
                    return cur.fetchall()
        except Exception as e:
            logger.error(f"Error getting fraud patterns: {e}")
            return []
    
    def get_user_transaction_stats(self, user_id):
        """Получение статистики по пользователю (безопасно)"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                    SELECT 
                        COUNT(*) as total_transactions,
                        AVG(amount) as avg_amount,
                        MAX(amount) as max_amount,
                        SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) as fraud_count
                    FROM transactions 
                    WHERE user_id = %s
                    """
                    cur.execute(query, (user_id,))
                    return cur.fetchone()
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return None
    
    def detect_sql_pattern_fraud(self, user_id, amount):
        """Обнаружение мошенничества через SQL паттерны"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    patterns = self.get_fraud_patterns()
                    fraud_reasons = []
                    
                    for pattern in patterns:
                        # БЕЗОПАСНО: используем параметризованные запросы
                        if pattern['pattern_name'] == 'large_amount':
                            if amount > 10000000:
                                fraud_reasons.append("large_amount")
                        elif pattern['pattern_name'] == 'small_amount':
                            if amount < 1000:
                                fraud_reasons.append("small_amount")
                        elif pattern['pattern_name'] == 'multiple_transactions':
                            query = """
                            SELECT COUNT(*) as recent_count 
                            FROM transactions 
                            WHERE user_id = %s AND timestamp > NOW() - INTERVAL '1 hour'
                            """
                            cur.execute(query, (user_id,))
                            result = cur.fetchone()
                            if result and result['recent_count'] > 5:
                                fraud_reasons.append("multiple_transactions")
                    
                    return fraud_reasons
        except Exception as e:
            logger.error(f"Error in SQL pattern detection: {e}")
            return []
    
    def get_dashboard_data(self):
        """Данные для дашборда"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Общая статистика
                    cur.execute("""
                    SELECT 
                        COUNT(*) as total_transactions,
                        SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) as fraud_count,
                        AVG(amount) as avg_amount,
                        MAX(amount) as max_amount
                    FROM transactions
                    """)
                    stats = cur.fetchone()
                    
                    # Статистика по часам
                    cur.execute("""
                    SELECT 
                        EXTRACT(HOUR FROM timestamp) as hour,
                        COUNT(*) as transaction_count,
                        SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) as fraud_count
                    FROM transactions
                    GROUP BY hour
                    ORDER BY hour
                    """)
                    hourly_stats = cur.fetchall()
                    
                    return {
                        'overall': stats,
                        'hourly': hourly_stats
                    }
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return None

# Синглтон для использования во всем приложении
db = DatabaseManager()