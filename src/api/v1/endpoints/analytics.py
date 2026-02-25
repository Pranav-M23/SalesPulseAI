from fastapi import APIRouter
from src.db.session import get_db
from src.core.logging import logger

router = APIRouter()


@router.get("/analytics", tags=["Analytics"])
async def get_analytics():
    """Overview stats for the dashboard."""
    db = await get_db()
    try:
        stats = {}

        # Total messages sent
        row = await (await db.execute("SELECT COUNT(*) FROM sent_messages")).fetchone()
        stats["total_sent"] = row[0] if row else 0

        # Messages sent today
        row = await (await db.execute(
            "SELECT COUNT(*) FROM sent_messages WHERE DATE(created_at) = DATE('now')"
        )).fetchone()
        stats["sent_today"] = row[0] if row else 0

        # Active triggers
        row = await (await db.execute(
            "SELECT COUNT(*) FROM triggers WHERE status = 'active'"
        )).fetchone()
        stats["active_triggers"] = row[0] if row else 0

        # Total triggers
        row = await (await db.execute("SELECT COUNT(*) FROM triggers")).fetchone()
        stats["total_triggers"] = row[0] if row else 0

        # Pending bookings
        row = await (await db.execute(
            "SELECT COUNT(*) FROM bookings WHERE status = 'pending'"
        )).fetchone()
        stats["pending_bookings"] = row[0] if row else 0

        # Confirmed bookings
        row = await (await db.execute(
            "SELECT COUNT(*) FROM bookings WHERE status = 'confirmed'"
        )).fetchone()
        stats["confirmed_bookings"] = row[0] if row else 0

        # Total bookings
        row = await (await db.execute("SELECT COUNT(*) FROM bookings")).fetchone()
        stats["total_bookings"] = row[0] if row else 0

        # Unique contacts
        row = await (await db.execute(
            "SELECT COUNT(DISTINCT phone_number) FROM conversations"
        )).fetchone()
        stats["total_contacts"] = row[0] if row else 0

        # Total conversation messages
        row = await (await db.execute("SELECT COUNT(*) FROM conversations")).fetchone()
        stats["total_messages"] = row[0] if row else 0

        # Channel breakdown for sent_messages
        cursor = await db.execute(
            "SELECT channel, COUNT(*) FROM sent_messages GROUP BY channel"
        )
        rows = await cursor.fetchall()
        stats["by_channel"] = {row[0]: row[1] for row in rows}

        # Recent activity: last 7 days messages sent per day
        cursor = await db.execute(
            """SELECT DATE(created_at) as day, COUNT(*) as cnt
            FROM sent_messages
            WHERE created_at >= DATE('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY day ASC"""
        )
        rows = await cursor.fetchall()
        stats["sent_last_7_days"] = [{"date": row[0], "count": row[1]} for row in rows]

        return {"success": True, "stats": stats}

    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return {"success": False, "stats": {}, "detail": str(e)}
    finally:
        await db.close()