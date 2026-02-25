import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Send, Zap, CalendarCheck, Users,
  TrendingUp, Clock, CheckCircle, XCircle,
  ArrowRight, RefreshCw,
} from 'lucide-react'
import { getAnalytics, getContacts, getTriggers } from '../api/client'

function StatCard({ icon: Icon, label, value, sub, color = 'brand' }) {
  const colors = {
    brand:  'text-brand-400 bg-brand-900/30',
    yellow: 'text-yellow-400 bg-yellow-900/30',
    blue:   'text-blue-400 bg-blue-900/30',
    purple: 'text-purple-400 bg-purple-900/30',
    red:    'text-red-400 bg-red-900/30',
  }
  return (
    <div className="card flex items-start gap-4">
      <div className={`p-3 rounded-lg ${colors[color]}`}>
        <Icon size={20} />
      </div>
      <div>
        <p className="text-2xl font-bold text-white">{value ?? '—'}</p>
        <p className="text-sm text-slate-400 mt-0.5">{label}</p>
        {sub && <p className="text-xs text-slate-500 mt-1">{sub}</p>}
      </div>
    </div>
  )
}

function MiniBar({ data }) {
  if (!data || data.length === 0) {
    return <p className="text-sm text-slate-500">No data yet.</p>
  }
  const max = Math.max(...data.map(d => d.count), 1)
  return (
    <div className="flex items-end gap-1 h-16">
      {data.map((d) => (
        <div key={d.date} className="flex-1 flex flex-col items-center gap-1 group relative">
          <div
            className="w-full bg-brand-600 rounded-t-sm transition-all group-hover:bg-brand-400"
            style={{ height: `${Math.max((d.count / max) * 100, 8)}%` }}
          />
          <span className="text-[9px] text-slate-500 truncate w-full text-center">
            {d.date?.slice(5)}
          </span>
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-surface-700 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-10">
            {d.date}: {d.count}
          </div>
        </div>
      ))}
    </div>
  )
}

export default function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [contacts, setContacts] = useState([])
  const [triggers, setTriggers] = useState([])
  const [loading, setLoading] = useState(true)

  async function load() {
    setLoading(true)
    try {
      const [a, c, t] = await Promise.all([
        getAnalytics(),
        getContacts(),
        getTriggers('active'),
      ])
      setStats(a.stats)
      setContacts(c.contacts || [])
      setTriggers(t.triggers || [])
    } catch {}
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-slate-400 mt-0.5">Overview of your SalesPulse AI</p>
        </div>
        <button onClick={load} disabled={loading} className="btn-secondary flex items-center gap-2 text-sm">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Send}       label="Messages Sent"   value={stats?.total_sent}        sub={`${stats?.sent_today ?? 0} today`} color="brand" />
        <StatCard icon={Zap}        label="Active Triggers" value={stats?.active_triggers}    sub={`${stats?.total_triggers ?? 0} total`} color="yellow" />
        <StatCard icon={CalendarCheck} label="Pending Bookings" value={stats?.pending_bookings} sub={`${stats?.confirmed_bookings ?? 0} confirmed`} color="blue" />
        <StatCard icon={Users}      label="Contacts"        value={stats?.total_contacts}     sub={`${stats?.total_messages ?? 0} messages`} color="purple" />
      </div>

      {/* Charts + breakdowns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Activity chart */}
        <div className="card lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-slate-200">Messages Sent — Last 7 Days</h2>
            <TrendingUp size={14} className="text-brand-400" />
          </div>
          <MiniBar data={stats?.sent_last_7_days} />
        </div>

        {/* Channel breakdown */}
        <div className="card">
          <h2 className="text-sm font-semibold text-slate-200 mb-4">By Channel</h2>
          {stats?.by_channel && Object.keys(stats.by_channel).length > 0 ? (
            <div className="space-y-3">
              {Object.entries(stats.by_channel).map(([ch, cnt]) => {
                const total = Object.values(stats.by_channel).reduce((a, b) => a + b, 0)
                const pct = Math.round((cnt / total) * 100)
                return (
                  <div key={ch}>
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-slate-300 capitalize">{ch}</span>
                      <span className="text-slate-400">{cnt} ({pct}%)</span>
                    </div>
                    <div className="h-1.5 bg-surface-700 rounded-full overflow-hidden">
                      <div className="h-full bg-brand-500 rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <p className="text-sm text-slate-500">No messages sent yet.</p>
          )}
        </div>
      </div>

      {/* Recent contacts + active triggers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Recent contacts */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-slate-200">Recent Contacts</h2>
            <Link to="/chat" className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1">
              View all <ArrowRight size={12} />
            </Link>
          </div>
          {contacts.length === 0 ? (
            <p className="text-sm text-slate-500">No contacts yet.</p>
          ) : (
            <div className="space-y-2">
              {contacts.slice(0, 6).map((c) => (
                <Link
                  key={c.phone_number}
                  to={`/chat?phone=${encodeURIComponent(c.phone_number)}`}
                  className="flex items-start gap-3 p-2 rounded-lg hover:bg-surface-700 transition-colors"
                >
                  <div className="w-8 h-8 rounded-full bg-brand-800 flex items-center justify-center text-brand-400 text-xs font-bold flex-shrink-0">
                    {c.phone_number.slice(-2)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-slate-200 truncate">{c.phone_number}</p>
                    <p className="text-xs text-slate-500 truncate mt-0.5">
                      {c.last_role === 'user' ? '← ' : '→ '}{c.last_message}
                    </p>
                  </div>
                  <span className="text-[10px] text-slate-500 flex-shrink-0">
                    {c.last_at ? new Date(c.last_at).toLocaleDateString() : ''}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Active triggers */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-slate-200">Active Triggers</h2>
            <Link to="/triggers" className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1">
              View all <ArrowRight size={12} />
            </Link>
          </div>
          {triggers.length === 0 ? (
            <p className="text-sm text-slate-500">No active triggers.</p>
          ) : (
            <div className="space-y-2">
              {triggers.slice(0, 6).map((t) => (
                <div key={t.id} className="flex items-start gap-3 p-2 rounded-lg hover:bg-surface-700 transition-colors">
                  <div className="w-8 h-8 rounded-full bg-yellow-900/40 flex items-center justify-center text-yellow-400 flex-shrink-0">
                    <Zap size={14} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-slate-200 truncate">{t.name}</p>
                    <p className="text-xs text-slate-500 truncate mt-0.5">
                      {t.channel} · {t.recipient}
                    </p>
                  </div>
                  <span className="badge-active">active</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}