import os
import psycopg2
import psycopg2.extras

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    # جدول الزبائن
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            telegram_id BIGINT PRIMARY KEY,
            full_name TEXT,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول الطلبات البسيط والمحفوظ دائماً
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT,
            service TEXT,
            duration TEXT,
            sale_price DECIMAL(10, 2),
            receipt_file_id TEXT,
            status TEXT DEFAULT 'pending',
            claimed_by BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def save_customer(user):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO customers (telegram_id, full_name, username)
        VALUES (%s, %s, %s)
        ON CONFLICT (telegram_id) 
        DO UPDATE SET full_name = EXCLUDED.full_name, username = EXCLUDED.username
    """, (user.id, user.full_name, user.username))
    conn.commit()
    cur.close()
    conn.close()

def create_order(telegram_id, service, duration, price, receipt_file_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (telegram_id, service, duration, sale_price, receipt_file_id, status)
        VALUES (%s, %s, %s, %s, %s, 'pending')
        RETURNING id
    """, (telegram_id, service, duration, price, receipt_file_id))
    order_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return order_id

def claim_order(order_id, admin_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE orders 
        SET status = 'claimed', claimed_by = %s 
        WHERE id = %s AND status = 'pending'
    """, (admin_id, order_id))
    affected = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return affected > 0

def complete_order(order_id, admin_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE orders 
        SET status = 'completed', claimed_by = %s 
        WHERE id = %s AND status != 'completed'
    """, (admin_id, order_id))
    affected = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return affected > 0
