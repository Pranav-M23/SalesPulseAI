from src.db.session import get_db
from src.core.logging import logger


async def store_message(phone_number, role, message, channel="whatsapp"):
    """Store a conversation message (user or assistant)."""
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO conversations (phone_number, role, message, channel) VALUES (?, ?, ?, ?)",
            (phone_number, role, message, channel),
        )
        await db.commit()
        logger.info(f"Stored {role} message for {phone_number} ({channel})")
    except Exception as e:
        logger.error(f"Failed to store message: {e}")
    finally:
        await db.close()


async def get_recent_messages(phone_number, limit=10):
    """Get recent conversation history for a phone number."""
    clean_number = phone_number.replace("whatsapp:", "").replace("+", "")
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT role, message FROM conversations 
            WHERE phone_number LIKE ? 
            ORDER BY created_at DESC LIMIT ?""",
            (f"%{clean_number}%", limit),
        )
        rows = await cursor.fetchall()
        # Reverse to get chronological order
        messages = [{"role": row[0], "content": row[1]} for row in reversed(rows)]
        return messages
    except Exception as e:
        logger.error(f"Failed to get messages: {e}")
        return []
    finally:
        await db.close()


async def store_sent_message(recipient, channel, body, subject=None, external_id=None, status="sent"):
    """Store a record of a sent message."""
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO sent_messages (recipient, channel, subject, body, status, external_id) VALUES (?, ?, ?, ?, ?, ?)",
            (recipient, channel, subject, body, status, external_id),
        )
        await db.commit()
        logger.info(f"Stored sent message to {recipient} ({channel}) status={status}")
    except Exception as e:
        logger.error(f"Failed to store sent message: {e}")
    finally:
        await db.close()


async def store_generated_message(lead_name, lead_company, stage, subject, message, cta, score=None):
    """Store a generated sales message."""
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO generated_messages 
            (lead_name, lead_company, stage, subject, message, cta, score) 
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (lead_name, lead_company, stage, subject, message, cta, score),
        )
        await db.commit()
        logger.info(f"Stored generated message for {lead_name} at {lead_company}")
    except Exception as e:
        logger.error(f"Failed to store generated message: {e}")
    finally:
        await db.close()


async def get_all_contacts(limit=100):
    """Return unique contacts derived from conversations, with last message & metadata."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT
                c.phone_number,
                c.message        AS last_message,
                c.role           AS last_role,
                c.channel        AS channel,
                c.created_at     AS last_at,
                (SELECT COUNT(*) FROM conversations WHERE phone_number = c.phone_number AND role = 'user') AS user_msg_count,
                (SELECT COUNT(*) FROM conversations WHERE phone_number = c.phone_number) AS total_msg_count
            FROM conversations c
            INNER JOIN (
                SELECT phone_number, MAX(created_at) AS max_at
                FROM conversations
                GROUP BY phone_number
            ) latest ON c.phone_number = latest.phone_number AND c.created_at = latest.max_at
            GROUP BY c.phone_number
            ORDER BY c.created_at DESC
            LIMIT ?""",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [
            {
                "phone_number": row[0],
                "last_message": row[1],
                "last_role": row[2],
                "channel": row[3],
                "last_at": row[4],
                "user_msg_count": row[5],
                "total_msg_count": row[6],
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Failed to get contacts: {e}")
        return []
    finally:
        await db.close()


async def get_conversation_history(phone_number, limit=20):
    """Get full conversation history for display."""
    clean_number = phone_number.replace("whatsapp:", "").replace("+", "")
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT role, message, channel, created_at FROM conversations 
            WHERE phone_number LIKE ? 
            ORDER BY created_at DESC LIMIT ?""",
            (f"%{clean_number}%", limit),
        )
        rows = await cursor.fetchall()
        return [
            {
                "role": row[0],
                "message": row[1],
                "channel": row[2],
                "timestamp": row[3],
            }
            for row in reversed(rows)
        ]
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        return []
    finally:
        await db.close()
