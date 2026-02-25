import asyncio
import re
from datetime import datetime, timedelta
from src.db.session import get_db
from src.config.settings import settings
from src.services.twilio_service import send_sms
from src.services.email_service import send_email
from src.services.openai_service import chat_completion
from src.services.conversation_service import store_message, store_sent_message, get_recent_messages
from src.services.booking_service import (
    create_booking, get_pending_bookings, confirm_all_pending,
    cancel_all_pending, get_booking_by_code, confirm_booking, cancel_booking,
)
from src.core.logging import logger
from src.core.exceptions import DatabaseError


def _get_whatsapp_sender():
    """Return the appropriate WhatsApp send function based on config."""
    if settings.WHATSAPP_PROVIDER == "meta":
        from src.services.meta_whatsapp_service import send_whatsapp
        return send_whatsapp
    else:
        from src.services.twilio_service import send_whatsapp
        return send_whatsapp

# Background task reference
_trigger_task = None
_reply_listener_task = None

# Check triggers every 10 seconds instead of 30
SCHEDULER_INTERVAL = 10
# Check for new replies every 5 seconds
REPLY_CHECK_INTERVAL = 5


async def create_trigger(name, trigger_type, channel, recipient, message,
                         recipient_name=None, subject=None, delay_minutes=1,
                         max_retries=3, stop_on_reply=True, campaign_name=None, step_number=0):
    """Create a new trigger in the database."""
    scheduled_at = datetime.utcnow() + timedelta(minutes=delay_minutes)
    db = await get_db()
    try:
        cursor = await db.execute(
            """INSERT INTO triggers 
            (name, trigger_type, channel, recipient, recipient_name, message, subject,
             delay_minutes, max_retries, stop_on_reply, status, campaign_name, step_number, scheduled_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?)""",
            (name, trigger_type, channel, recipient, recipient_name, message, subject,
             delay_minutes, max_retries, int(stop_on_reply), campaign_name, step_number,
             scheduled_at.isoformat()),
        )
        await db.commit()
        trigger_id = cursor.lastrowid
        logger.info(f"Trigger created: id={trigger_id} name={name} scheduled_at={scheduled_at}")

        # --- Generate Groq AI reply and send as initial message ---
        context_messages = [
            {"role": "system", "content": "You are a helpful sales assistant. Start the conversation naturally."},
            {"role": "user", "content": message}
        ]
        try:
            ai_reply = await chat_completion(messages=context_messages)
            logger.info(f"Groq initial reply: {ai_reply[:100]}")
        except Exception as e:
            logger.error(f"Groq failed, using fallback: {e}")
            ai_reply = (
                "Thanks for your reply! I'd love to continue our conversation. "
                "A member of our team will be in touch shortly."
            )

        # Send the AI reply as the initial message
        send_whatsapp = _get_whatsapp_sender()
        await send_whatsapp(to=recipient, message=ai_reply)

        # Store the AI reply in conversation
        await store_message(
            phone_number=recipient,
            role="assistant",
            message=ai_reply,
            channel=channel,
        )

        return {
            "trigger_id": trigger_id,
            "name": name,
            "trigger_type": trigger_type,
            "channel": channel,
            "recipient": recipient,
            "status": "active",
            "delay_minutes": delay_minutes,
            "scheduled_at": scheduled_at.isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to create trigger: {e}")
        raise DatabaseError(f"Failed to create trigger: {str(e)}")
    finally:
        await db.close()


async def get_all_triggers(status=None):
    """Get all triggers, optionally filtered by status."""
    db = await get_db()
    try:
        if status:
            cursor = await db.execute(
                "SELECT * FROM triggers WHERE status = ? ORDER BY created_at DESC", (status,)
            )
        else:
            cursor = await db.execute("SELECT * FROM triggers ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        triggers = []
        for row in rows:
            triggers.append({
                "id": row[0],
                "name": row[1],
                "trigger_type": row[2],
                "channel": row[3],
                "recipient": row[4],
                "recipient_name": row[5],
                "message": row[6][:100] + "..." if len(row[6]) > 100 else row[6],
                "subject": row[7],
                "delay_minutes": row[8],
                "max_retries": row[9],
                "retries_done": row[10],
                "stop_on_reply": bool(row[11]),
                "status": row[12],
                "campaign_name": row[13],
                "step_number": row[14],
                "scheduled_at": row[15],
                "executed_at": row[16],
                "created_at": row[17],
            })
        return triggers
    except Exception as e:
        logger.error(f"Failed to fetch triggers: {e}")
        raise DatabaseError(f"Failed to fetch triggers: {str(e)}")
    finally:
        await db.close()


async def update_trigger_status(trigger_id, status):
    """Update a trigger's status."""
    db = await get_db()
    try:
        await db.execute(
            "UPDATE triggers SET status = ?, updated_at = ? WHERE id = ?",
            (status, datetime.utcnow().isoformat(), trigger_id),
        )
        await db.commit()
        logger.info(f"Trigger {trigger_id} status updated to {status}")
    except Exception as e:
        logger.error(f"Failed to update trigger: {e}")
    finally:
        await db.close()


async def cancel_trigger(trigger_id):
    """Cancel a trigger."""
    await update_trigger_status(trigger_id, "cancelled")
    return {"success": True, "detail": f"Trigger {trigger_id} cancelled"}


async def cancel_campaign(campaign_name):
    """Cancel all triggers in a campaign."""
    db = await get_db()
    try:
        await db.execute(
            "UPDATE triggers SET status = 'cancelled', updated_at = ? WHERE campaign_name = ? AND status = 'active'",
            (datetime.utcnow().isoformat(), campaign_name),
        )
        await db.commit()
        logger.info(f"Campaign '{campaign_name}' cancelled")
        return {"success": True, "detail": f"Campaign '{campaign_name}' cancelled"}
    except Exception as e:
        logger.error(f"Failed to cancel campaign: {e}")
        raise DatabaseError(f"Failed to cancel campaign: {str(e)}")
    finally:
        await db.close()


async def check_recipient_replied(recipient):
    """Check if recipient has replied recently."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT COUNT(*) FROM conversations 
            WHERE phone_number LIKE ? AND role = 'user' 
            AND created_at > datetime('now', '-24 hours')""",
            (f"%{recipient.replace('+', '')}%",),
        )
        row = await cursor.fetchone()
        return row[0] > 0
    except Exception:
        return False
    finally:
        await db.close()


async def get_active_triggers_for_recipient(recipient):
    """Get active triggers for a specific recipient."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT * FROM triggers 
            WHERE recipient LIKE ? AND status = 'active' 
            ORDER BY scheduled_at ASC""",
            (f"%{recipient.replace('+', '')}%",),
        )
        rows = await cursor.fetchall()
        return rows
    except Exception:
        return []
    finally:
        await db.close()


async def handle_lead_reply(phone_number, message_text, channel="whatsapp"):
    """
    When a lead replies to a triggered message:
    1. Store their message
    2. Cancel remaining triggers (stop_on_reply)
    3. Use Groq to generate a smart reply
    4. Store the AI reply
    5. Return reply (TwiML will send it — NOT us)
    """
    logger.info(f"Lead reply from {phone_number} on {channel}: {message_text[:80]}")

    # 1. Store the lead's reply
    await store_message(
        phone_number=phone_number,
        role="user",
        message=message_text,
        channel=channel,
    )

    # 2. Cancel active triggers with stop_on_reply
    clean_number = phone_number.replace("whatsapp:", "").replace("+", "")
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT id, name FROM triggers 
            WHERE recipient LIKE ? AND status = 'active' AND stop_on_reply = 1""",
            (f"%{clean_number}%",),
        )
        cancelled_triggers = await cursor.fetchall()
        if cancelled_triggers:
            await db.execute(
                """UPDATE triggers SET status = 'completed', updated_at = ?
                WHERE recipient LIKE ? AND status = 'active' AND stop_on_reply = 1""",
                (datetime.utcnow().isoformat(), f"%{clean_number}%"),
            )
            await db.commit()
            for t in cancelled_triggers:
                logger.info(f"Auto-completed trigger {t[0]} ({t[1]}) — lead replied")
    except Exception as e:
        logger.error(f"Error cancelling triggers: {e}")
    finally:
        await db.close()

    # 3. Get conversation history for context
    history = await get_recent_messages(phone_number=phone_number, limit=10)

    # 4. Build context-aware prompt with booking info
    trigger_context = await _get_trigger_context(phone_number)
    pending_bookings = await get_pending_bookings(phone_number)

    context_messages = []

    # Add booking context if there are pending bookings
    if pending_bookings:
        booking_summary = "\n".join([
            f"  - #{b['confirmation_code']}: {b['title']} "
            f"({'₹' + str(b['amount']) if b['amount'] else 'no amount'}) "
            f"[{b['status']}]"
            for b in pending_bookings
        ])
        context_messages.append({
            "role": "system",
            "content": (
                f"The customer has {len(pending_bookings)} pending booking(s)/order(s):\n"
                f"{booking_summary}\n\n"
                f"If they say CONFIRM/YES, confirm these bookings. "
                f"If they say CANCEL/NO, cancel them. "
                f"If they mention a specific confirmation code, act on that one only."
            ),
        })

    if trigger_context:
        context_messages.append({
            "role": "system",
            "content": (
                f"The lead is replying to a triggered sales message. "
                f"Original trigger: '{trigger_context['name']}'. "
                f"Original message sent: '{trigger_context['message'][:200]}'. "
                f"Lead name: {trigger_context.get('recipient_name', 'Unknown')}. "
                f"Be helpful, continue the sales conversation naturally. "
                f"Keep your response concise (2-3 sentences max). "
                f"If they show interest, suggest a next step. "
                f"If they want to opt out, be respectful and confirm."
            ),
        })

    context_messages.extend(history)

    # 5. Generate AI reply using Groq
    try:
        ai_reply = await chat_completion(messages=context_messages)
        logger.info(f"Groq generated reply: {ai_reply[:100]}")
    except Exception as e:
        logger.error(f"Groq failed, using fallback: {e}")
        ai_reply = (
            "Thanks for your reply! I'd love to continue our conversation. "
            "A member of our team will be in touch shortly."
        )

    # 5b. Parse booking actions from AI reply
    ai_reply = await _process_booking_actions(ai_reply, phone_number)

    # 6. Store AI reply in conversation
    await store_message(
        phone_number=phone_number,
        role="assistant",
        message=ai_reply,
        channel=channel,
    )

    # 7. Store in sent_messages for tracking
    await store_sent_message(
        recipient=phone_number.replace("whatsapp:", ""),
        channel=channel,
        body=ai_reply,
        subject=None,
        external_id="twiml_reply",
        status="auto_reply",
    )

    # 8. Return the reply — TwiML in webhook will send it
    #    DO NOT call send_whatsapp/send_sms here to avoid double message
    logger.info(f"Returning AI reply for TwiML delivery to {phone_number}")
    return ai_reply


async def _get_trigger_context(phone_number):
    """Get the most recent trigger context for this recipient."""
    clean_number = phone_number.replace("whatsapp:", "").replace("+", "")
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT name, message, recipient_name, trigger_type, channel 
            FROM triggers 
            WHERE recipient LIKE ? AND status IN ('completed', 'active')
            ORDER BY executed_at DESC, created_at DESC 
            LIMIT 1""",
            (f"%{clean_number}%",),
        )
        row = await cursor.fetchone()
        if row:
            return {
                "name": row[0],
                "message": row[1],
                "recipient_name": row[2],
                "trigger_type": row[3],
                "channel": row[4],
            }
        return None
    except Exception:
        return None
    finally:
        await db.close()


async def _process_booking_actions(ai_reply, phone_number):
    """Parse AI response for booking action tags and execute them.
    
    Tags parsed:
    - [CREATE_BOOKING] with [TITLE:], [TYPE:], [DATE:], [TIME:], [AMOUNT:]
    - [ACTION: CONFIRM]
    - [ACTION: CANCEL]
    - [ACTION: STATUS]
    
    Returns cleaned reply with tags removed.
    """
    clean_reply = ai_reply

    # --- Handle CREATE_BOOKING ---
    if "[CREATE_BOOKING]" in ai_reply:
        title = _extract_tag(ai_reply, "TITLE") or "New Booking"
        booking_type = _extract_tag(ai_reply, "TYPE") or "general"
        date = _extract_tag(ai_reply, "DATE")
        time_val = _extract_tag(ai_reply, "TIME")
        amount_str = _extract_tag(ai_reply, "AMOUNT")
        amount = None
        if amount_str:
            # Extract numeric value
            nums = re.findall(r'[\d,.]+', amount_str)
            if nums:
                amount = float(nums[0].replace(',', ''))

        try:
            booking = await create_booking(
                phone_number=phone_number,
                title=title,
                booking_type=booking_type,
                date=date,
                time=time_val,
                amount=amount,
            )
            code = booking["confirmation_code"]
            logger.info(f"Auto-created booking {code} for {phone_number}")

            # Remove all tags from the reply
            clean_reply = _remove_booking_tags(clean_reply)

            # Append booking details
            booking_info = f"\n\n📋 *Booking Created*\n"
            booking_info += f"📌 {title}\n"
            if date:
                booking_info += f"📅 Date: {date}\n"
            if time_val:
                booking_info += f"🕐 Time: {time_val}\n"
            if amount:
                booking_info += f"💰 Amount: ₹{amount:,.2f}\n"
            booking_info += f"🔖 Code: *{code}*\n\n"
            booking_info += "Reply *CONFIRM* to confirm or *CANCEL* to cancel."

            clean_reply += booking_info

        except Exception as e:
            logger.error(f"Failed to auto-create booking: {e}")

    # --- Handle ACTION: CONFIRM ---
    elif "[ACTION: CONFIRM]" in ai_reply:
        clean_reply = _remove_action_tags(clean_reply)

        # Check if a specific code is mentioned
        code_match = re.search(r'\b([A-Z0-9]{6})\b', ai_reply)
        pending = await get_pending_bookings(phone_number)

        if code_match and await get_booking_by_code(code_match.group(1)):
            code = code_match.group(1)
            await confirm_booking(confirmation_code=code)
            booking = await get_booking_by_code(code)
            clean_reply += f"\n\n✅ Booking *{code}* confirmed!"
        elif pending:
            count = await confirm_all_pending(phone_number)
            clean_reply += f"\n\n✅ {count} booking(s) confirmed successfully!"
        else:
            clean_reply += "\n\nℹ️ No pending bookings found to confirm."

    # --- Handle ACTION: CANCEL ---
    elif "[ACTION: CANCEL]" in ai_reply:
        clean_reply = _remove_action_tags(clean_reply)

        code_match = re.search(r'\b([A-Z0-9]{6})\b', ai_reply)
        pending = await get_pending_bookings(phone_number)

        if code_match and await get_booking_by_code(code_match.group(1)):
            code = code_match.group(1)
            await cancel_booking(confirmation_code=code)
            clean_reply += f"\n\n❌ Booking *{code}* has been cancelled."
        elif pending:
            count = await cancel_all_pending(phone_number)
            clean_reply += f"\n\n❌ {count} booking(s) cancelled."
        else:
            clean_reply += "\n\nℹ️ No pending bookings found to cancel."

    # --- Handle ACTION: STATUS ---
    elif "[ACTION: STATUS]" in ai_reply:
        clean_reply = _remove_action_tags(clean_reply)
        from src.services.booking_service import get_all_bookings
        bookings = await get_all_bookings(phone_number=phone_number, limit=5)

        if bookings:
            status_text = "\n\n📋 *Your Bookings:*\n"
            for b in bookings:
                emoji = "⏳" if b["status"] == "pending" else "✅" if b["status"] == "confirmed" else "❌"
                status_text += (
                    f"{emoji} *{b['confirmation_code']}* — {b['title']} "
                    f"({b['status']})"
                )
                if b.get("amount"):
                    status_text += f" ₹{b['amount']:,.2f}"
                status_text += "\n"
            clean_reply += status_text
        else:
            clean_reply += "\n\nℹ️ You have no bookings yet."

    return clean_reply.strip()


def _extract_tag(text, tag_name):
    """Extract value from [TAG: value] format."""
    pattern = rf'\[{tag_name}:\s*(.+?)\]'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def _remove_booking_tags(text):
    """Remove all booking-related tags from text."""
    text = text.replace("[CREATE_BOOKING]", "")
    text = re.sub(r'\[(TITLE|TYPE|DATE|TIME|AMOUNT):\s*.+?\]', '', text, flags=re.IGNORECASE)
    return text.strip()


def _remove_action_tags(text):
    """Remove action tags from text."""
    text = re.sub(r'\[ACTION:\s*\w+\]', '', text, flags=re.IGNORECASE)
    return text.strip()


async def execute_trigger(trigger):
    """Execute a single trigger — send the message."""
    trigger_id = trigger["id"]
    channel = trigger["channel"]
    recipient = trigger["recipient"]
    message = trigger["message"]
    subject = trigger["subject"]
    name = trigger["name"]

    logger.info(f"Executing trigger {trigger_id}: {name} -> {channel}:{recipient}")

    try:
        # Check if recipient replied (stop_on_reply)
        if trigger.get("stop_on_reply") and await check_recipient_replied(recipient):
            logger.info(f"Trigger {trigger_id}: recipient replied, marking completed")
            await update_trigger_status(trigger_id, "completed")
            return

        # Send based on channel
        if channel == "whatsapp":
            send_whatsapp = _get_whatsapp_sender()
            result = await send_whatsapp(to=recipient, message=message)
            external_id = result.get("message_id")
        elif channel == "sms":
            result = await send_sms(to=recipient, message=message)
            external_id = result.get("message_id")
        elif channel == "email":
            result = await send_email(
                to_email=recipient, subject=subject or name, body=message
            )
            external_id = result.get("message_id")
        else:
            logger.error(f"Unknown channel: {channel}")
            await update_trigger_status(trigger_id, "failed")
            return

        # Store the triggered message as assistant message for conversation context
        await store_message(
            phone_number=recipient,
            role="assistant",
            message=message,
            channel=channel,
        )

        # Store sent message
        await store_sent_message(
            recipient=recipient,
            channel=channel,
            body=message,
            subject=subject,
            external_id=external_id,
            status="triggered",
        )

        # Mark as completed
        db = await get_db()
        try:
            await db.execute(
                "UPDATE triggers SET status = 'completed', executed_at = ?, updated_at = ? WHERE id = ?",
                (datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), trigger_id),
            )
            await db.commit()
        finally:
            await db.close()

        logger.info(f"Trigger {trigger_id} executed successfully")

    except Exception as e:
        logger.error(f"Trigger {trigger_id} failed: {e}")
        db = await get_db()
        try:
            retries = trigger.get("retries_done", 0) + 1
            max_retries = trigger.get("max_retries", 3)
            new_status = "failed" if retries >= max_retries else "active"
            new_scheduled = (datetime.utcnow() + timedelta(minutes=1)).isoformat() if new_status == "active" else None
            await db.execute(
                "UPDATE triggers SET retries_done = ?, status = ?, scheduled_at = ?, updated_at = ? WHERE id = ?",
                (retries, new_status, new_scheduled, datetime.utcnow().isoformat(), trigger_id),
            )
            await db.commit()
            logger.info(f"Trigger {trigger_id}: retry {retries}/{max_retries}, status={new_status}")
        finally:
            await db.close()


async def process_pending_triggers():
    """Check and execute all triggers that are due."""
    db = await get_db()
    try:
        now = datetime.utcnow().isoformat()
        cursor = await db.execute(
            "SELECT * FROM triggers WHERE status = 'active' AND scheduled_at <= ?",
            (now,),
        )
        rows = await cursor.fetchall()

        if rows:
            logger.info(f"Found {len(rows)} pending triggers to execute")

        for row in rows:
            trigger = {
                "id": row[0], "name": row[1], "trigger_type": row[2],
                "channel": row[3], "recipient": row[4], "recipient_name": row[5],
                "message": row[6], "subject": row[7], "delay_minutes": row[8],
                "max_retries": row[9], "retries_done": row[10],
                "stop_on_reply": bool(row[11]), "status": row[12],
            }
            await execute_trigger(trigger)

    except Exception as e:
        logger.error(f"Error processing triggers: {e}")
    finally:
        await db.close()


async def trigger_scheduler():
    """Background loop — checks for pending triggers every 10 seconds."""
    logger.info(f"Trigger scheduler started (interval: {SCHEDULER_INTERVAL}s)")
    while True:
        try:
            await process_pending_triggers()
        except Exception as e:
            logger.error(f"Trigger scheduler error: {e}")
        await asyncio.sleep(SCHEDULER_INTERVAL)


def start_trigger_scheduler():
    """Start the background trigger scheduler."""
    global _trigger_task
    if _trigger_task is None or _trigger_task.done():
        _trigger_task = asyncio.create_task(trigger_scheduler())
        logger.info("Trigger scheduler task created")


def stop_trigger_scheduler():
    """Stop the background trigger scheduler."""
    global _trigger_task
    if _trigger_task and not _trigger_task.done():
        _trigger_task.cancel()
        logger.info("Trigger scheduler task cancelled")