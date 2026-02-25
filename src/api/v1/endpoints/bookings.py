from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from src.services.booking_service import (
    create_booking, get_all_bookings, get_booking_by_code,
    get_booking_by_id, confirm_booking, cancel_booking,
)
from src.core.logging import logger

router = APIRouter()


# ─── Schemas ───────────────────────────────────────────────────────────────────

class CreateBookingRequest(BaseModel):
    phone_number: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=200)
    booking_type: str = Field(default="general", max_length=50)
    customer_name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    amount: Optional[float] = None
    currency: str = Field(default="INR", max_length=5)
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    success: bool = True
    booking_id: int
    confirmation_code: str
    title: str
    booking_type: str
    status: str
    detail: str = "Booking created successfully"


class BookingActionResponse(BaseModel):
    success: bool = True
    detail: str


# ─── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/bookings", response_model=BookingResponse, tags=["Bookings"])
async def create_booking_endpoint(request: CreateBookingRequest):
    """Create a new booking/order that will be sent to the customer for confirmation via WhatsApp."""
    logger.info(f"POST /bookings for {request.phone_number}: {request.title}")
    result = await create_booking(
        phone_number=request.phone_number,
        title=request.title,
        booking_type=request.booking_type,
        customer_name=request.customer_name,
        description=request.description,
        date=request.date,
        time=request.time,
        amount=request.amount,
        currency=request.currency,
        notes=request.notes,
    )
    return BookingResponse(
        booking_id=result["booking_id"],
        confirmation_code=result["confirmation_code"],
        title=result["title"],
        booking_type=result["booking_type"],
        status=result["status"],
        detail=f"Booking created. Code: {result['confirmation_code']}",
    )


@router.get("/bookings", tags=["Bookings"])
async def list_bookings(
    phone_number: Optional[str] = Query(None, description="Filter by phone number"),
    status: Optional[str] = Query(None, description="Filter by status: pending, confirmed, cancelled"),
    limit: int = Query(50, ge=1, le=200),
):
    """List all bookings with optional filters."""
    bookings = await get_all_bookings(phone_number=phone_number, status=status, limit=limit)
    return {"success": True, "total": len(bookings), "bookings": bookings}


@router.get("/bookings/{booking_id}", tags=["Bookings"])
async def get_booking(booking_id: int):
    """Get a specific booking by ID."""
    booking = await get_booking_by_id(booking_id)
    if not booking:
        return {"success": False, "detail": "Booking not found"}
    return {"success": True, "booking": booking}


@router.get("/bookings/code/{confirmation_code}", tags=["Bookings"])
async def get_booking_by_code_endpoint(confirmation_code: str):
    """Look up a booking by confirmation code."""
    booking = await get_booking_by_code(confirmation_code)
    if not booking:
        return {"success": False, "detail": "Booking not found"}
    return {"success": True, "booking": booking}


@router.post("/bookings/{booking_id}/confirm", response_model=BookingActionResponse, tags=["Bookings"])
async def confirm_booking_endpoint(booking_id: int):
    """Confirm a pending booking."""
    booking = await get_booking_by_id(booking_id)
    if not booking:
        return BookingActionResponse(success=False, detail="Booking not found")
    if booking["status"] != "pending":
        return BookingActionResponse(success=False, detail=f"Booking is already {booking['status']}")

    await confirm_booking(booking_id=booking_id)
    return BookingActionResponse(detail=f"Booking {booking['confirmation_code']} confirmed")


@router.post("/bookings/{booking_id}/cancel", response_model=BookingActionResponse, tags=["Bookings"])
async def cancel_booking_endpoint(booking_id: int):
    """Cancel a pending booking."""
    booking = await get_booking_by_id(booking_id)
    if not booking:
        return BookingActionResponse(success=False, detail="Booking not found")
    if booking["status"] != "pending":
        return BookingActionResponse(success=False, detail=f"Booking is already {booking['status']}")

    await cancel_booking(booking_id=booking_id)
    return BookingActionResponse(detail=f"Booking {booking['confirmation_code']} cancelled")


@router.post("/bookings/send-confirmation", tags=["Bookings"])
async def send_booking_confirmation(
    phone_number: str = Query(..., description="Recipient phone number"),
    booking_id: int = Query(..., description="Booking ID to send confirmation for"),
):
    """Send a booking confirmation message to the customer via WhatsApp/SMS."""
    booking = await get_booking_by_id(booking_id)
    if not booking:
        return {"success": False, "detail": "Booking not found"}

    # Build the confirmation message
    msg = f"📋 *Booking Confirmation Request*\n\n"
    msg += f"📌 {booking['title']}\n"
    if booking.get("date"):
        msg += f"📅 Date: {booking['date']}\n"
    if booking.get("time"):
        msg += f"🕐 Time: {booking['time']}\n"
    if booking.get("amount"):
        msg += f"💰 Amount: ₹{booking['amount']:,.2f}\n"
    msg += f"🔖 Code: *{booking['confirmation_code']}*\n\n"
    msg += "Reply *CONFIRM* to confirm or *CANCEL* to cancel this booking."

    # Send via the configured WhatsApp provider
    from src.config.settings import settings
    if settings.WHATSAPP_PROVIDER == "meta":
        from src.services.meta_whatsapp_service import send_whatsapp
    else:
        from src.services.twilio_service import send_whatsapp

    try:
        result = await send_whatsapp(to=phone_number, message=msg)
        from src.services.conversation_service import store_sent_message, store_message
        await store_message(phone_number=phone_number, role="assistant", message=msg, channel="whatsapp")
        await store_sent_message(
            recipient=phone_number, channel="whatsapp", body=msg,
            external_id=result.get("message_id"), status="booking_confirmation",
        )
        return {
            "success": True,
            "detail": f"Booking confirmation sent to {phone_number}",
            "message_id": result.get("message_id"),
            "confirmation_code": booking["confirmation_code"],
        }
    except Exception as e:
        logger.error(f"Failed to send booking confirmation: {e}")
        return {"success": False, "detail": str(e)}
