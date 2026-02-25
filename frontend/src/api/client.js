const BASE = import.meta.env.VITE_API_URL || '/api'

async function request(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body !== undefined) opts.body = JSON.stringify(body)

  const res = await fetch(`${BASE}${path}`, opts)
  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const err = await res.json()
      if (Array.isArray(err.detail)) {
        // Pydantic validation errors: [{loc, msg, type}, ...]
        detail = err.detail.map(e => `${e.loc?.slice(1).join('.')}: ${e.msg}`).join(' | ')
      } else {
        detail = err.detail || err.message || detail
      }
    } catch {}
    throw new Error(detail)
  }
  return res.json()
}

export const api = {
  get:    (path)        => request('GET', path),
  post:   (path, body)  => request('POST', path, body),
  delete: (path)        => request('DELETE', path),
}

// ─── Analytics ────────────────────────────────────────────────────────────────
export const getAnalytics = () => api.get('/analytics')

// ─── Contacts & Conversations ─────────────────────────────────────────────────
export const getContacts         = () => api.get('/contacts')
export const getConversation     = (phone, limit = 100) =>
  api.get(`/conversations/${encodeURIComponent(phone)}?limit=${limit}`)
export const sendToContact       = (phone, message, channel = 'whatsapp') =>
  api.post(`/conversations/${encodeURIComponent(phone)}/send`, { message, channel })

// ─── Triggers ─────────────────────────────────────────────────────────────────
export const getTriggers        = (status) =>
  api.get(`/triggers${status ? `?status=${status}` : ''}`)
export const createTrigger      = (data)  => api.post('/triggers', data)
export const cancelTrigger      = (id)    => api.delete(`/triggers/${id}`)
export const createDripCampaign = (data)  => api.post('/triggers/drip-campaign', data)
export const cancelCampaign     = (name)  => api.delete(`/triggers/campaign/${encodeURIComponent(name)}`)

// ─── Bookings ─────────────────────────────────────────────────────────────────
export const getBookings        = (filters = {}) => {
  const q = new URLSearchParams()
  if (filters.phone_number) q.set('phone_number', filters.phone_number)
  if (filters.status)       q.set('status', filters.status)
  if (filters.limit)        q.set('limit', filters.limit)
  return api.get(`/bookings?${q}`)
}
export const createBooking      = (data)  => api.post('/bookings', data)
export const confirmBooking     = (id)    => api.post(`/bookings/${id}/confirm`, {})
export const cancelBookingById  = (id)    => api.post(`/bookings/${id}/cancel`, {})
export const sendBookingConfirm = (phone, bookingId) =>
  api.post(`/bookings/send-confirmation?phone_number=${encodeURIComponent(phone)}&booking_id=${bookingId}`, {})

// ─── Message Generation ───────────────────────────────────────────────────────
export const generateMessage    = (data)  => api.post('/generate-message', data)

// ─── Send ─────────────────────────────────────────────────────────────────────
export const sendWhatsApp = (to, message) => api.post('/send/whatsapp', { to, message })
export const sendSMS      = (to, message) => api.post('/send/sms', { to, message })
export const sendEmail    = (to_email, subject, body, to_name, html) =>
  api.post('/send/email', { to_email, subject, body, to_name, html })