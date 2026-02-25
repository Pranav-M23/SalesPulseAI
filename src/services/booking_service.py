import random
import string
from datetime import datetime
from src.db.session import get_db
from src.core.logging import logger


def _generate_confirmation_code(length=6):
    """Generate a random alphanumeric confirmation code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


async def create_booking(phone_number, title, booking_type="general",
                         customer_name=None, description=None,
                         date=None, time=None, amount=None, currency="INR",
                         notes=None):
    """Create a new pending booking/order."""
    confirmation_code = _generate_confirmation_code()
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO bookings 
            (phone_number, customer_name, booking_type, title, description,
             date, time, amount, currency, status, confirmation_code, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)""",
            (phone_number, customer_name, booking_type, title, description,
             date, time, amount, currency, confirmation_code, notes),
        )
        await db.commit()
        booking_id = cursor.lastrowid
        logger.info(f"Booking created: id={booking_id} code={confirmation_code} for {phone_number}")
        return {
            "booking_id": booking_id,
            "confirmation_code": confirmation_code,
            "title": title,
            "booking_type": booking_type,
            "status": "pending",
            "customer_name": customer_name,
            "date": date,
            "time": time,
            "amount": amount,
            "currency": currency,
        }
    except Exception as e:
        logger.error(f"Failed to create booking: {e}")
        raise
    finally:
        await db.close()


async def get_pending_bookings(phone_number):
    """Get all pending bookings for a phone number."""
    clean_number = phone_number.replace("whatsapp:", "").replace("+", "")
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT id, phone_number, customer_name, booking_type, title, description,
                      date, time, amount, currency, status, confirmation_code, notes, created_at
            FROM bookings 
            WHERE phone_number LIKE ? AND status = 'pending'
            ORDER BY created_at DESC""",
            (f"%{clean_number}%",),
        )
        rows = await cursor.fetchall()
        return [_row_to_dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to get pending bookings: {e}")
        return []
    finally:
        await db.close()


async def get_booking_by_code(confirmation_code):
    """Get a booking by its confirmation code."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT id, phone_number, customer_name, booking_type, title, description,
                      date, time, amount, currency, status, confirmation_code, notes, created_at
            FROM bookings WHERE confirmation_code = ?""",
            (confirmation_code.upper(),),
        )
        row = await cursor.fetchone()
        return _row_to_dict(row) if row else None
    except Exception as e:
        logger.error(f"Failed to get booking by code: {e}")
        return None
    finally:
        await db.close()


async def get_booking_by_id(booking_id):
    """Get a booking by its ID."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT id, phone_number, customer_name, booking_type, title, description,
                      date, time, amount, currency, status, confirmation_code, notes, created_at
            FROM bookings WHERE id = ?""",
            (booking_id,),
        )
        row = await cursor.fetchone()
        return _row_to_dict(row) if row else None
    except Exception as e:
        logger.error(f"Failed to get booking: {e}")
        return None
    finally:
        await db.close()


async def confirm_booking(booking_id=None, confirmation_code=None):
    """Confirm a booking by ID or confirmation code."""
    db = await get_db()
    try:
        now = datetime.utcnow().isoformat()
        if confirmation_code:
            await db.execute(
                """UPDATE bookings SET status = 'confirmed', confirmed_at = ?, updated_at = ?
                WHERE confirmation_code = ? AND status = 'pending'""",
                (now, now, confirmation_code.upper()),
            )
        elif booking_id:
            await db.execute(
                """UPDATE bookings SET status = 'confirmed', confirmed_at = ?, updated_at = ?
                WHERE id = ? AND status = 'pending'""",
                (now, now, booking_id),
            )
        await db.commit()
        logger.info(f"Booking confirmed: id={booking_id} code={confirmation_code}")
        return True
    except Exception as e:
        logger.error(f"Failed to confirm booking: {e}")
        return False
    finally:
        await db.close()


async def cancel_booking(booking_id=None, confirmation_code=None):
    """Cancel a booking by ID or confirmation code."""
    db = await get_db()
    try:
        now = datetime.utcnow().isoformat()
        if confirmation_code:
            await db.execute(
                """UPDATE bookings SET status = 'cancelled', cancelled_at = ?, updated_at = ?
                WHERE confirmation_code = ? AND status = 'pending'""",
                (now, now, confirmation_code.upper()),
            )
        elif booking_id:
            await db.execute(
                """UPDATE bookings SET status = 'cancelled', cancelled_at = ?, updated_at = ?
                WHERE id = ? AND status = 'pending'""",
                (now, now, booking_id),
            )
        await db.commit()
        logger.info(f"Booking cancelled: id={booking_id} code={confirmation_code}")
        return True
    except Exception as e:
        logger.error(f"Failed to cancel booking: {e}")
        return False
    finally:
        await db.close()


async def get_all_bookings(phone_number=None, status=None, limit=50):
    """Get bookings with optional filters."""
    db = await get_db()
    try:
        query = """SELECT id, phone_number, customer_name, booking_type, title, description,
                          date, time, amount, currency, status, confirmation_code, notes, created_at
                   FROM bookings WHERE 1=1"""
        params = []
        if phone_number:
            clean = phone_number.replace("whatsapp:", "").replace("+", "")
            query += " AND phone_number LIKE ?"
            params.append(f"%{clean}%")
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [_row_to_dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to get bookings: {e}")
        return []
    finally:
        await db.close()


async def confirm_all_pending(phone_number):
    """Confirm all pending bookings for a phone number."""
    clean_number = phone_number.replace("whatsapp:", "").replace("+", "")
    db = await get_db()
    try:
        now = datetime.utcnow().isoformat()
        cursor = await db.execute(
            """UPDATE bookings SET status = 'confirmed', confirmed_at = ?, updated_at = ?
            WHERE phone_number LIKE ? AND status = 'pending'""",
            (now, now, f"%{clean_number}%"),
        )
        await db.commit()
        count = cursor.rowcount
        logger.info(f"Confirmed {count} pending bookings for {phone_number}")
        return count
    except Exception as e:
        logger.error(f"Failed to confirm all: {e}")
        return 0
    finally:
        await db.close()


async def cancel_all_pending(phone_number):
    """Cancel all pending bookings for a phone number."""
    clean_number = phone_number.replace("whatsapp:", "").replace("+", "")
    db = await get_db()
    try:
        now = datetime.utcnow().isoformat()
        cursor = await db.execute(
            """UPDATE bookings SET status = 'cancelled', cancelled_at = ?, updated_at = ?
            WHERE phone_number LIKE ? AND status = 'pending'""",
            (now, now, f"%{clean_number}%"),
        )
        await db.commit()
        count = cursor.rowcount
        logger.info(f"Cancelled {count} pending bookings for {phone_number}")
        return count
    except Exception as e:
        logger.error(f"Failed to cancel all: {e}")
        return 0
    finally:
        await db.close()


def _row_to_dict(row):
    """Convert a DB row to a booking dict."""
    if not row:
        return None
    return {
        "id": row[0],
        "phone_number": row[1],
        "customer_name": row[2],
        "booking_type": row[3],
        "title": row[4],
        "description": row[5],
        "date": row[6],
        "time": row[7],
        "amount": row[8],
        "currency": row[9],
        "status": row[10],
        "confirmation_code": row[11],
        "notes": row[12],
        "created_at": row[13],
    }
