import aiosqlite
import os
from src.core.logging import logger

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "salespulse.db")


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db() -> None:
    logger.info("Initializing database...")
    db = await get_db()
    try:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                message TEXT NOT NULL,
                channel TEXT NOT NULL DEFAULT 'whatsapp',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_phone
            ON conversations(phone_number, created_at DESC)
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sent_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient TEXT NOT NULL,
                channel TEXT NOT NULL,
                subject TEXT,
                body TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'sent',
                external_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS generated_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_name TEXT,
                lead_company TEXT,
                stage TEXT,
                subject TEXT,
                message TEXT NOT NULL,
                cta TEXT,
                score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS triggers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                trigger_type TEXT NOT NULL,
                channel TEXT NOT NULL,
                recipient TEXT NOT NULL,
                recipient_name TEXT,
                message TEXT NOT NULL,
                subject TEXT,
                delay_minutes INTEGER NOT NULL DEFAULT 60,
                max_retries INTEGER NOT NULL DEFAULT 3,
                retries_done INTEGER NOT NULL DEFAULT 0,
                stop_on_reply INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'active',
                campaign_name TEXT,
                step_number INTEGER DEFAULT 0,
                scheduled_at TIMESTAMP,
                executed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_triggers_status
            ON triggers(status, scheduled_at)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_triggers_recipient
            ON triggers(recipient, status)
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT NOT NULL,
                customer_name TEXT,
                booking_type TEXT NOT NULL DEFAULT 'general',
                title TEXT NOT NULL,
                description TEXT,
                date TEXT,
                time TEXT,
                amount REAL,
                currency TEXT DEFAULT 'INR',
                status TEXT NOT NULL DEFAULT 'pending',
                confirmation_code TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confirmed_at TIMESTAMP,
                cancelled_at TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_bookings_phone
            ON bookings(phone_number, status)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_bookings_code
            ON bookings(confirmation_code)
        """)
        await db.commit()
        logger.info("Database initialized successfully.")
    finally:
        await db.close()
