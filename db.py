import os
import psycopg
from decimal import Decimal
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL")


def db():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL غير موجود في Render")

    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row,
        connect_timeout=15
    )


def init_db():
    queries = [
        """
        CREATE TABLE IF NOT EXISTS customers (
            id BIGSERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            username TEXT,
            full_name TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS orders (
            id BIGSERIAL PRIMARY KEY,
            telegram_id BIGINT NOT NULL,
            service TEXT NOT NULL,
            duration TEXT,
            sale_price NUMERIC(12,2) NOT NULL DEFAULT 0,
            cost_price NUMERIC(12,2) NOT NULL DEFAULT 0,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS subscriptions (
            id BIGSERIAL PRIMARY KEY,
            telegram_id BIGINT NOT NULL,
            service TEXT NOT NULL,
            account_info TEXT,
            start_date TIMESTAMPTZ DEFAULT NOW(),
            end_date TIMESTAMPTZ,
            status TEXT DEFAULT 'active'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS financial_transactions (
            id BIGSERIAL PRIMARY KEY,
            transaction_type TEXT NOT NULL,
            fund_source TEXT NOT NULL,
            amount NUMERIC(12,2) NOT NULL CHECK(amount > 0),
            description TEXT NOT NULL,
            reference_id BIGINT,
            created_by BIGINT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS inventory (
            id BIGSERIAL PRIMARY KEY,
            item_name TEXT UNIQUE NOT NULL,
            quantity NUMERIC(12,2) NOT NULL DEFAULT 0,
            unit_cost NUMERIC(12,2) NOT NULL DEFAULT 0,
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS inventory_movements (
            id BIGSERIAL PRIMARY KEY,
            item_id BIGINT REFERENCES inventory(id),
            movement_type TEXT NOT NULL,
            quantity NUMERIC(12,2) NOT NULL,
            unit_cost NUMERIC(12,2) NOT NULL DEFAULT 0,
            description TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id BIGSERIAL PRIMARY KEY,
            category TEXT NOT NULL,
            amount NUMERIC(12,2) NOT NULL,
            fund_source TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS capital (
            id BIGSERIAL PRIMARY KEY,
            fund_source TEXT NOT NULL,
            amount NUMERIC(12,2) NOT NULL,
            operation TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id BIGSERIAL PRIMARY KEY,
            admin_id BIGINT,
            action TEXT NOT NULL,
            details TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    ]

    with db() as conn:
        with conn.cursor() as cur:
            for query in queries:
                cur.execute(query)


def money(value):
    value = Decimal(str(value))
    if value <= 0:
        raise ValueError("المبلغ يجب أن يكون أكبر من صفر")
    return value.quantize(Decimal("0.01"))


def check_source(source):
    if source not in ("owner", "shared", "operating"):
        raise ValueError("مصدر الأموال غير صحيح")


def save_customer(telegram_id, username, full_name):
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO customers
                (telegram_id, username, full_name)
                VALUES (%s, %s, %s)
                ON CONFLICT (telegram_id)
                DO UPDATE SET
                    username = EXCLUDED.username,
                    full_name = EXCLUDED.full_name
            """, (telegram_id, username, full_name))


def save_order(telegram_id, service, duration, sale_price):
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO orders
                (telegram_id, service, duration, sale_price)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (
                telegram_id, service, duration, money(sale_price)
            ))
            return cur.fetchone()["id"]


def add_transaction(transaction_type, fund_source, amount,
                    description, created_by=None, reference_id=None):
    check_source(fund_source)

    allowed = (
        "income",
        "subscription_cost",
        "expense",
        "capital_in",
        "capital_out",
        "inventory_purchase"
    )

    if transaction_type not in allowed:
        raise ValueError("نوع العملية غير صحيح")

    amount = money(amount)

    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO financial_transactions
                (transaction_type, fund_source, amount,
                 description, created_by, reference_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                transaction_type, fund_source, amount,
                description, created_by, reference_id
            ))
            return cur.fetchone()["id"]


def add_expense(category, amount, fund_source,
                description="", created_by=None):
    check_source(fund_source)
    amount = money(amount)

    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO expenses
                (category, amount, fund_source, description)
                VALUES (%s, %s, %s, %s)
            """, (category, amount, fund_source, description))

            cur.execute("""
                INSERT INTO financial_transactions
                (transaction_type, fund_source, amount,
                 description, created_by)
                VALUES ('expense', %s, %s, %s, %s)
            """, (
                fund_source, amount,
                description or category, created_by
            ))


def add_capital(amount, fund_source, operation,
                description="", created_by=None):
    check_source(fund_source)
    amount = money(amount)

    if operation not in ("in", "out"):
        raise ValueError("العملية يجب أن تكون in أو out")

    transaction_type = (
        "capital_in" if operation == "in" else "capital_out"
    )

    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO capital
                (fund_source, amount, operation, description)
                VALUES (%s, %s, %s, %s)
            """, (fund_source, amount, operation, description))

            cur.execute("""
                INSERT INTO financial_transactions
                (transaction_type, fund_source, amount,
                 description, created_by)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                transaction_type, fund_source, amount,
                description or "حركة رأس مال", created_by
            ))


def transfer_money(amount, from_source, to_source,
                   description="", created_by=None):
    check_source(from_source)
    check_source(to_source)
    amount = money(amount)

    if from_source == to_source:
        raise ValueError("لا يمكن التحويل لنفس المحفظة")

    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO financial_transactions
                (transaction_type, fund_source, amount,
                 description, created_by)
                VALUES
                ('transfer_out', %s, %s, %s, %s),
                ('transfer_in', %s, %s, %s, %s)
            """, (
                from_source, amount,
                description or "تحويل صادر", created_by,
                to_source, amount,
                description or "تحويل وارد", created_by
            ))


def add_inventory_item(item_name, quantity, unit_cost,
                       fund_source="operating", paid=True,
                       created_by=None):
    check_source(fund_source)

    quantity = Decimal(str(quantity))
    unit_cost = Decimal(str(unit_cost))

    if quantity <= 0 or unit_cost < 0:
        raise ValueError("الكمية أو التكلفة غير صحيحة")

    total_cost = (quantity * unit_cost).quantize(
        Decimal("0.01")
    )

    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO inventory
                (item_name, quantity, unit_cost)
                VALUES (%s, %s, %s)
                ON CONFLICT (item_name)
                DO UPDATE SET
                    quantity = inventory.quantity + EXCLUDED.quantity,
                    unit_cost = (
                        (inventory.quantity * inventory.unit_cost)
                        + (EXCLUDED.quantity * EXCLUDED.unit_cost)
                    ) / NULLIF(
                        inventory.quantity + EXCLUDED.quantity, 0
                    ),
                    updated_at = NOW()
                RETURNING id
            """, (item_name, quantity, unit_cost))

            item_id = cur.fetchone()["id"]

            cur.execute("""
                INSERT INTO inventory_movements
                (item_id, movement_type, quantity,
                 unit_cost, description)
                VALUES (%s, 'in', %s, %s, %s)
            """, (
                item_id, quantity, unit_cost, "إضافة مخزون"
            ))

            if paid and total_cost > 0:
                cur.execute("""
                    INSERT INTO financial_transactions
                    (transaction_type, fund_source, amount,
                     description, created_by)
                    VALUES ('inventory_purchase', %s, %s, %s, %s)
                """, (
                    fund_source, total_cost,
                    "شراء مخزون: " + item_name, created_by
                ))

            return item_id


def inventory_out(item_id, quantity, description="صرف مخزون"):
    quantity = Decimal(str(quantity))

    if quantity <= 0:
        raise ValueError("الكمية غير صحيحة")

    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT quantity, unit_cost
                FROM inventory
                WHERE id = %s
                FOR UPDATE
            """, (item_id,))

            item = cur.fetchone()

            if not item or item["quantity"] < quantity:
                raise ValueError("المخزون غير كافٍ")

            cur.execute("""
                UPDATE inventory
                SET quantity = quantity - %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (quantity, item_id))

            cur.execute("""
                INSERT INTO inventory_movements
                (item_id, movement_type, quantity,
                 unit_cost, description)
                VALUES (%s, 'out', %s, %s, %s)
            """, (
                item_id, quantity, item["unit_cost"], description
            ))

            return (quantity * item["unit_cost"]).quantize(
                Decimal("0.01")
            )


def complete_order(telegram_id, service, duration,
                   sale_price, cost_price, income_source,
                   cost_source, created_by=None):
    check_source(income_source)
    check_source(cost_source)

    sale_price = money(sale_price)
    cost_price = Decimal(str(cost_price)).quantize(
        Decimal("0.01")
    )

    if cost_price < 0:
        raise ValueError("التكلفة غير صحيحة")

    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO orders
                (telegram_id, service, duration,
                 sale_price, cost_price, status)
                VALUES (%s, %s, %s, %s, %s, 'completed')
                RETURNING id
            """, (
                telegram_id, service, duration,
                sale_price, cost_price
            ))

            order_id = cur.fetchone()["id"]

            cur.execute("""
                INSERT INTO financial_transactions
                (transaction_type, fund_source, amount,
                 description, reference_id, created_by)
                VALUES
                ('income', %s, %s, %s, %s, %s),
                ('subscription_cost', %s, %s, %s, %s, %s)
            """, (
                income_source, sale_price,
                "مبيعات " + service, order_id, created_by,
                cost_source, cost_price,
                "تكلفة " + service, order_id, created_by
            ))

            return order_id


def get_inventory():
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, item_name, quantity, unit_cost,
                       quantity * unit_cost AS stock_value
                FROM inventory
                ORDER BY item_name
            """)
            return cur.fetchall()


def get_financial_report():
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    fund_source,

                    COALESCE(SUM(
                        CASE WHEN transaction_type = 'income'
                        THEN amount ELSE 0 END
                    ), 0) AS revenue,

                    COALESCE(SUM(
                        CASE WHEN transaction_type IN
                        ('subscription_cost', 'expense')
                        THEN amount ELSE 0 END
                    ), 0) AS costs,

                    COALESCE(SUM(
                        CASE
                            WHEN transaction_type IN
                            ('income', 'capital_in', 'transfer_in')
                            THEN amount

                            WHEN transaction_type IN
                            ('subscription_cost', 'expense',
                             'capital_out', 'inventory_purchase',
                             'transfer_out')
                            THEN -amount

                            ELSE 0
                        END
                    ), 0) AS wallet_balance

                FROM financial_transactions
                GROUP BY fund_source
                ORDER BY fund_source
            """)
            return cur.fetchall()


def get_profit_report():
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COALESCE(SUM(
                        CASE WHEN transaction_type = 'income'
                        THEN amount ELSE 0 END
                    ), 0) AS sales,

                    COALESCE(SUM(
                        CASE WHEN transaction_type = 'subscription_cost'
                        THEN amount ELSE 0 END
                    ), 0) AS subscription_costs,

                    COALESCE(SUM(
                        CASE WHEN transaction_type = 'expense'
                        THEN amount ELSE 0 END
                    ), 0) AS expenses

                FROM financial_transactions
            """)

            result = cur.fetchone()
            result["net_profit"] = (
                result["sales"]
                - result["subscription_costs"]
                - result["expenses"]
            )

            return result


def get_recent_transactions(limit=20):
    limit = max(1, min(int(limit), 100))

    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT *
                FROM financial_transactions
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
            return cur.fetchall()


def add_audit_log(admin_id, action, details=""):
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO audit_logs
                (admin_id, action, details)
                VALUES (%s, %s, %s)
            """, (admin_id, action, details))
