import os
from decimal import Decimal, InvalidOperation

import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL")

SOURCES = {"owner", "shared", "operating"}


def connect():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing")

    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row,
        connect_timeout=15
    )


def amount(value, allow_zero=False):
    try:
        result = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError):
        raise ValueError("المبلغ غير صحيح")

    if result < 0 or (not allow_zero and result == 0):
        raise ValueError("المبلغ يجب أن يكون أكبر من صفر")

    return result


def check_source(source):
    if source not in SOURCES:
        raise ValueError("مصدر الأموال غير صحيح")


def init_db():
    ddl = [
        """CREATE TABLE IF NOT EXISTS customers (
            telegram_id BIGINT PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )""",

        """CREATE TABLE IF NOT EXISTS orders (
            id BIGSERIAL PRIMARY KEY,
            telegram_id BIGINT NOT NULL,
            service TEXT NOT NULL,
            duration TEXT,
            sale_price NUMERIC(12,2) NOT NULL DEFAULT 0,
            cost_price NUMERIC(12,2) NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'pending',
            receipt_file_id TEXT,
            claimed_by BIGINT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            completed_at TIMESTAMPTZ
        )""",

        """CREATE TABLE IF NOT EXISTS financial_transactions (
            id BIGSERIAL PRIMARY KEY,
            transaction_type TEXT NOT NULL,
            fund_source TEXT NOT NULL
                CHECK (fund_source IN ('owner','shared','operating')),
            amount NUMERIC(12,2) NOT NULL CHECK (amount > 0),
            description TEXT NOT NULL,
            reference_id BIGINT,
            created_by BIGINT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )""",

        """CREATE TABLE IF NOT EXISTS inventory (
            id BIGSERIAL PRIMARY KEY,
            item_name TEXT UNIQUE NOT NULL,
            quantity NUMERIC(12,2) NOT NULL DEFAULT 0
                CHECK (quantity >= 0),
            unit_cost NUMERIC(12,2) NOT NULL DEFAULT 0,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )""",

        """CREATE TABLE IF NOT EXISTS inventory_movements (
            id BIGSERIAL PRIMARY KEY,
            item_id BIGINT REFERENCES inventory(id),
            movement_type TEXT NOT NULL,
            quantity NUMERIC(12,2) NOT NULL,
            unit_cost NUMERIC(12,2) NOT NULL DEFAULT 0,
            description TEXT,
            created_by BIGINT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )""",

        """CREATE TABLE IF NOT EXISTS expenses (
            id BIGSERIAL PRIMARY KEY,
            category TEXT NOT NULL,
            amount NUMERIC(12,2) NOT NULL,
            fund_source TEXT NOT NULL,
            description TEXT,
            created_by BIGINT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )""",

        """CREATE TABLE IF NOT EXISTS cash_counts (
            id BIGSERIAL PRIMARY KEY,
            fund_source TEXT NOT NULL,
            expected_amount NUMERIC(12,2) NOT NULL,
            actual_amount NUMERIC(12,2) NOT NULL,
            difference NUMERIC(12,2) NOT NULL,
            notes TEXT,
            counted_by BIGINT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )""",

        """CREATE TABLE IF NOT EXISTS audit_logs (
            id BIGSERIAL PRIMARY KEY,
            admin_id BIGINT,
            action TEXT NOT NULL,
            details TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )"""
    ]

    with connect() as conn:
        with conn.cursor() as cur:
            for statement in ddl:
                cur.execute(statement)


def save_customer(user):
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO customers (telegram_id, username, full_name)
            VALUES (%s,%s,%s)
            ON CONFLICT (telegram_id) DO UPDATE SET
            username=EXCLUDED.username,
            full_name=EXCLUDED.full_name""",
            (user.id, user.username, user.full_name)
        )


def create_order(
    telegram_id,
    service,
    duration,
    sale_price,
    receipt_file_id=None
):
    price = amount(sale_price)

    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO orders
            (telegram_id,service,duration,sale_price,receipt_file_id)
            VALUES (%s,%s,%s,%s,%s)
            RETURNING id""",
            (telegram_id, service, duration, price, receipt_file_id)
        )

        return cur.fetchone()["id"]


def claim_order(order_id, admin_id):
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """UPDATE orders
            SET claimed_by=%s, status='claimed'
            WHERE id=%s AND status='pending'
            RETURNING id""",
            (admin_id, order_id)
        )

        return cur.fetchone() is not None


def complete_order(
    order_id,
    admin_id,
    cost_price,
    income_source,
    cost_source
):
    check_source(income_source)
    check_source(cost_source)

    cost = amount(cost_price, allow_zero=True)

    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM orders WHERE id=%s FOR UPDATE",
            (order_id,)
        )

        order = cur.fetchone()

        if not order:
            raise ValueError("الطلب غير موجود")

        if order["status"] == "completed":
            raise ValueError("تم إغلاق هذا الطلب مسبقاً")

        cur.execute(
            """UPDATE orders
            SET status='completed',
                cost_price=%s,
                completed_at=NOW()
            WHERE id=%s""",
            (cost, order_id)
        )

        cur.execute(
            """INSERT INTO financial_transactions
            (transaction_type,fund_source,amount,description,reference_id,created_by)
            VALUES ('income',%s,%s,%s,%s,%s)""",
            (
                income_source,
                order["sale_price"],
                "مبيعات الطلب رقم " + str(order_id),
                order_id,
                admin_id
            )
        )

        if cost > 0:
            cur.execute(
                """INSERT INTO financial_transactions
                (transaction_type,fund_source,amount,description,reference_id,created_by)
                VALUES ('subscription_cost',%s,%s,%s,%s,%s)""",
                (
                    cost_source,
                    cost,
                    "تكلفة الطلب رقم " + str(order_id),
                    order_id,
                    admin_id
                )
            )

        cur.execute(
            """INSERT INTO audit_logs(admin_id,action,details)
            VALUES (%s,'complete_order',%s)""",
            (admin_id, str(order_id))
        )


def add_income(value, source, description, admin_id):
    check_source(source)
    value = amount(value)

    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO financial_transactions
            (transaction_type,fund_source,amount,description,created_by)
            VALUES ('income',%s,%s,%s,%s)""",
            (source, value, description, admin_id)
        )


def add_expense(category, value, source, description, admin_id):
    check_source(source)
    value = amount(value)

    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO expenses
            (category,amount,fund_source,description,created_by)
            VALUES (%s,%s,%s,%s,%s)""",
            (category, value, source, description, admin_id)
        )

        cur.execute(
            """INSERT INTO financial_transactions
            (transaction_type,fund_source,amount,description,created_by)
            VALUES ('expense',%s,%s,%s,%s)""",
            (source, value, description or category, admin_id)
        )


def add_capital(value, source, operation, description, admin_id):
    check_source(source)
    value = amount(value)

    if operation not in ("in", "out"):
        raise ValueError("نوع حركة رأس المال غير صحيح")

    tx_type = "capital_in" if operation == "in" else "capital_out"

    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO financial_transactions
            (transaction_type,fund_source,amount,description,created_by)
            VALUES (%s,%s,%s,%s,%s)""",
            (
                tx_type,
                source,
                value,
                description or "حركة رأس مال",
                admin_id
            )
        )


def transfer(value, source_from, source_to, description, admin_id):
    check_source(source_from)
    check_source(source_to)

    value = amount(value)

    if source_from == source_to:
        raise ValueError("اختر محفظتين مختلفتين")

    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO financial_transactions
            (transaction_type,fund_source,amount,description,created_by)
            VALUES
            ('transfer_out',%s,%s,%s,%s),
            ('transfer_in',%s,%s,%s,%s)""",
            (
                source_from,
                value,
                description or "تحويل صادر",
                admin_id,
                source_to,
                value,
                description or "تحويل وارد",
                admin_id
            )
        )


def add_stock(
    name,
    qty,
    unit_cost,
    admin_id,
    fund_source="operating"
):
    check_source(fund_source)

    qty = amount(qty)
    cost = amount(unit_cost, allow_zero=True)

    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO inventory(item_name,quantity,unit_cost)
            VALUES (%s,%s,%s)
            ON CONFLICT(item_name) DO UPDATE SET
            unit_cost=(
                (inventory.quantity*inventory.unit_cost)+
                (EXCLUDED.quantity*EXCLUDED.unit_cost)
            )/
            NULLIF(inventory.quantity+EXCLUDED.quantity,0),
            quantity=inventory.quantity+EXCLUDED.quantity,
            updated_at=NOW()
            RETURNING id""",
            (name, qty, cost)
        )

        item_id = cur.fetchone()["id"]

        cur.execute(
            """INSERT INTO inventory_movements
            (item_id,movement_type,quantity,unit_cost,description,created_by)
            VALUES (%s,'in',%s,%s,'إضافة مخزون',%s)""",
            (item_id, qty, cost, admin_id)
        )

        total = (qty * cost).quantize(Decimal("0.01"))

        if total > 0:
            cur.execute(
                """INSERT INTO financial_transactions
                (transaction_type,fund_source,amount,description,created_by)
                VALUES ('inventory_purchase',%s,%s,%s,%s)""",
                (
                    fund_source,
                    total,
                    "شراء مخزون: " + name,
                    admin_id
                )
            )

        return item_id


def remove_stock(item_id, qty, description, admin_id):
    qty = amount(qty)

    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT quantity,unit_cost
            FROM inventory
            WHERE id=%s
            FOR UPDATE""",
            (item_id,)
        )

        item = cur.fetchone()

        if not item or item["quantity"] < qty:
            raise ValueError("الصنف غير موجود أو الكمية غير كافية")

        cur.execute(
            """UPDATE inventory
            SET quantity=quantity-%s, updated_at=NOW()
            WHERE id=%s""",
            (qty, item_id)
        )

        cur.execute(
            """INSERT INTO inventory_movements
            (item_id,movement_type,quantity,unit_cost,description,created_by)
            VALUES (%s,'out',%s,%s,%s,%s)""",
            (
                item_id,
                qty,
                item["unit_cost"],
                description,
                admin_id
            )
        )


def inventory_list():
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT id,item_name,quantity,unit_cost,
            quantity*unit_cost AS stock_value
            FROM inventory
            ORDER BY item_name"""
        )

        return cur.fetchall()


def financial_report():
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT fund_source,
            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type IN
                        ('income','capital_in','transfer_in')
                        THEN amount

                        WHEN transaction_type IN
                        ('expense','subscription_cost','capital_out','transfer_out')
                        THEN -amount

                        ELSE 0
                    END
                ),0
            ) AS balance
            FROM financial_transactions
            GROUP BY fund_source
            ORDER BY fund_source"""
        )

        return cur.fetchall()


def profit_report():
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT
            COALESCE(
                SUM(amount) FILTER (
                    WHERE transaction_type='income'
                ),0
            ) AS sales,

            COALESCE(
                SUM(amount) FILTER (
                    WHERE transaction_type='subscription_cost'
                ),0
            ) AS costs,

            COALESCE(
                SUM(amount) FILTER (
                    WHERE transaction_type='expense'
                ),0
            ) AS expenses

            FROM financial_transactions"""
        )

        row = cur.fetchone()

        row["net_profit"] = (
            row["sales"] - row["costs"] - row["expenses"]
        )

        return row


def recent_transactions(limit=15):
    limit = max(1, min(int(limit), 50))

    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT id,transaction_type,fund_source,amount,
            description,created_at
            FROM financial_transactions
            ORDER BY id DESC
            LIMIT %s""",
            (limit,)
        )

        return cur.fetchall()


def record_cash_count(source, actual, notes, admin_id):
    check_source(source)

    actual = amount(actual, allow_zero=True)

    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type IN
                        ('income','capital_in','transfer_in')
                        THEN amount

                        WHEN transaction_type IN
                        ('expense','subscription_cost','capital_out',
                         'transfer_out','inventory_purchase')
                        THEN -amount

                        ELSE 0
                    END
                ),0
            ) AS balance
            FROM financial_transactions
            WHERE fund_source=%s""",
            (source,)
        )

        expected = cur.fetchone()["balance"]
        difference = actual - expected

        cur.execute(
            """INSERT INTO cash_counts
            (fund_source,expected_amount,actual_amount,
             difference,notes,counted_by)
            VALUES (%s,%s,%s,%s,%s,%s)""",
            (
                source,
                expected,
                actual,
                difference,
                notes,
                admin_id
            )
        )

        return expected, difference


def audit(admin_id, action, details=""):
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """INSERT INTO audit_logs(admin_id,action,details)
            VALUES (%s,%s,%s)""",
            (admin_id, action, details)
        )
