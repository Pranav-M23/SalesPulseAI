import { useState, useEffect } from 'react'
import {
  CalendarCheck, Plus, X, RefreshCw,
  CheckCircle, XCircle, Send, Search,
} from 'lucide-react'
import {
  getBookings, createBooking, confirmBooking,
  cancelBookingById, sendBookingConfirm,
} from '../api/client'
import { format } from 'date-fns'

function StatusBadge({ status }) {
  const cls = {
    pending:   'badge-pending',
    confirmed: 'badge-confirmed',
    cancelled: 'badge-cancelled',
  }
  return <span className={cls[status] || 'badge-pending'}>{status}</span>
}

function BookingCard({ booking, onAction }) {
  const [acting, setActing] = useState(false)

  async function act(fn) {
    setActing(true)
    try { await fn() } catch (e) { alert(e.message) }
    setActing(false)
    onAction()
  }

  return (
    <div className="card hover:border-surface-600 transition-colors">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-100">{booking.title}</h3>
          <p className="text-xs text-slate-400 mt-0.5">{booking.phone_number}</p>
        </div>
        <StatusBadge status={booking.status} />
      </div>

      <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 mb-3">
        {booking.booking_type && (
          <div>
            <p className="text-[10px] text-slate-500 uppercase tracking-wider">Type</p>
            <p className="text-xs text-slate-300 capitalize">{booking.booking_type}</p>
          </div>
        )}
        {booking.confirmation_code && (
          <div>
            <p className="text-[10px] text-slate-500 uppercase tracking-wider">Code</p>
            <p className="text-xs text-slate-300 font-mono font-bold">{booking.confirmation_code}</p>
          </div>
        )}
        {booking.date && (
          <div>
            <p className="text-[10px] text-slate-500 uppercase tracking-wider">Date</p>
            <p className="text-xs text-slate-300">{booking.date}</p>
          </div>
        )}
        {booking.time && (
          <div>
            <p className="text-[10px] text-slate-500 uppercase tracking-wider">Time</p>
            <p className="text-xs text-slate-300">{booking.time}</p>
          </div>
        )}
        {booking.amount != null && (
          <div>
            <p className="text-[10px] text-slate-500 uppercase tracking-wider">Amount</p>
            <p className="text-xs text-slate-300">{booking.currency} {Number(booking.amount).toLocaleString()}</p>
          </div>
        )}
        {booking.customer_name && (
          <div>
            <p className="text-[10px] text-slate-500 uppercase tracking-wider">Customer</p>
            <p className="text-xs text-slate-300">{booking.customer_name}</p>
          </div>
        )}
      </div>

      <p className="text-[10px] text-slate-500 mb-3">
        Created {booking.created_at ? format(new Date(booking.created_at), 'dd MMM yyyy, HH:mm') : '—'}
      </p>

      {booking.status === 'pending' && (
        <div className="flex gap-2">
          <button
            disabled={acting}
            onClick={() => act(() => confirmBooking(booking.id))}
            className="flex-1 flex items-center justify-center gap-1.5 bg-brand-700/40 hover:bg-brand-700/70 text-brand-300 text-xs py-2 rounded-lg transition-colors"
          >
            <CheckCircle size={12} /> Confirm
          </button>
          <button
            disabled={acting}
            onClick={() => act(() => sendBookingConfirm(booking.phone_number, booking.id))}
            className="flex-1 flex items-center justify-center gap-1.5 bg-surface-700 hover:bg-surface-600 text-slate-300 text-xs py-2 rounded-lg transition-colors"
          >
            <Send size={12} /> Send WA
          </button>
          <button
            disabled={acting}
            onClick={() => act(() => cancelBookingById(booking.id))}
            className="flex-1 flex items-center justify-center gap-1.5 bg-red-900/30 hover:bg-red-900/50 text-red-400 text-xs py-2 rounded-lg transition-colors"
          >
            <XCircle size={12} /> Cancel
          </button>
        </div>
      )}
    </div>
  )
}

function CreateBookingModal({ onClose, onCreated }) {
  const [form, setForm] = useState({
    phone_number: '', title: '', booking_type: 'general',
    customer_name: '', description: '', date: '', time: '',
    amount: '', currency: 'INR', notes: '',
  })
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  async function submit(e) {
    e.preventDefault()
    setSaving(true)
    setErr('')
    try {
      const payload = { ...form, amount: form.amount ? Number(form.amount) : null }
      await createBooking(payload)
      onCreated()
      onClose()
    } catch (e) {
      setErr(e.message)
    }
    setSaving(false)
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-surface-800 rounded-2xl w-full max-w-md border border-surface-700 shadow-2xl">
        <div className="flex items-center justify-between px-5 py-4 border-b border-surface-700">
          <h2 className="text-base font-semibold text-white">New Booking</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200"><X size={16} /></button>
        </div>
        <form onSubmit={submit} className="p-5 space-y-3 overflow-y-auto max-h-[70vh]">
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <label className="text-xs text-slate-400 mb-1 block">Phone number *</label>
              <input className="input text-sm" value={form.phone_number} onChange={e => set('phone_number', e.target.value)} required placeholder="+91 98765 43210" />
            </div>
            <div className="col-span-2">
              <label className="text-xs text-slate-400 mb-1 block">Title *</label>
              <input className="input text-sm" value={form.title} onChange={e => set('title', e.target.value)} required placeholder="Product order / Meeting" />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Type</label>
              <select className="input text-sm" value={form.booking_type} onChange={e => set('booking_type', e.target.value)}>
                {['general', 'booking', 'order', 'appointment', 'reservation'].map(t =>
                  <option key={t} value={t}>{t}</option>
                )}
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Customer name</label>
              <input className="input text-sm" value={form.customer_name} onChange={e => set('customer_name', e.target.value)} />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Date</label>
              <input type="date" className="input text-sm" value={form.date} onChange={e => set('date', e.target.value)} />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Time</label>
              <input type="time" className="input text-sm" value={form.time} onChange={e => set('time', e.target.value)} />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Amount</label>
              <input type="number" step="0.01" min="0" className="input text-sm" value={form.amount} onChange={e => set('amount', e.target.value)} placeholder="0.00" />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Currency</label>
              <input className="input text-sm" value={form.currency} onChange={e => set('currency', e.target.value)} />
            </div>
            <div className="col-span-2">
              <label className="text-xs text-slate-400 mb-1 block">Notes</label>
              <textarea rows={2} className="input text-sm resize-none" value={form.notes} onChange={e => set('notes', e.target.value)} />
            </div>
          </div>
          {err && <p className="text-sm text-red-400">{err}</p>}
          <div className="flex gap-2 pt-1">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" disabled={saving} className="btn-primary flex-1">
              {saving ? 'Creating…' : 'Create Booking'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function BookingsPage() {
  const [bookings, setBookings] = useState([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('')
  const [phoneFilter, setPhoneFilter] = useState('')
  const [showCreate, setShowCreate] = useState(false)

  async function load() {
    setLoading(true)
    try {
      const data = await getBookings({
        status: statusFilter || undefined,
        phone_number: phoneFilter || undefined,
        limit: 100,
      })
      setBookings(data.bookings || [])
    } catch {}
    setLoading(false)
  }

  useEffect(() => { load() }, [statusFilter])

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-5">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-white">Bookings</h1>
          <p className="text-sm text-slate-400 mt-0.5">Orders, appointments, and reservations</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary flex items-center gap-2 text-sm">
          <Plus size={14} /> New Booking
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2">
        {['', 'pending', 'confirmed', 'cancelled'].map(s => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`text-xs px-3 py-1.5 rounded-full transition-colors ${
              statusFilter === s
                ? 'bg-brand-600 text-white'
                : 'bg-surface-700 text-slate-400 hover:text-slate-200'
            }`}
          >
            {s || 'All'}
          </button>
        ))}
        <div className="relative ml-auto flex items-center gap-2">
          <div className="relative">
            <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              className="input text-xs py-1.5 pl-7 w-44"
              placeholder="Filter by phone…"
              value={phoneFilter}
              onChange={e => setPhoneFilter(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && load()}
            />
          </div>
          <button onClick={load} className="text-slate-400 hover:text-slate-200">
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Cards grid */}
      {loading ? (
        <div className="text-center text-slate-500 text-sm py-12">Loading…</div>
      ) : bookings.length === 0 ? (
        <div className="text-center text-slate-500 text-sm py-12">
          <CalendarCheck size={40} className="mx-auto mb-3 opacity-20" />
          No bookings found.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {bookings.map(b => (
            <BookingCard key={b.id} booking={b} onAction={load} />
          ))}
        </div>
      )}

      {showCreate && <CreateBookingModal onClose={() => setShowCreate(false)} onCreated={load} />}
    </div>
  )
}