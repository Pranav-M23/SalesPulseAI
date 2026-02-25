import { useState, useEffect } from 'react'
import {
  Zap, Plus, X, Trash2, RefreshCw,
  Clock, ChevronDown, ChevronUp, Layers,
} from 'lucide-react'
import {
  getTriggers, createTrigger, cancelTrigger,
  createDripCampaign, cancelCampaign,
} from '../api/client'
import { format } from 'date-fns'

const TRIGGER_TYPES = ['follow_up', 'scheduled', 'no_response', 're_engagement', 'drip']
const CHANNELS      = ['whatsapp', 'sms', 'email']

function StatusBadge({ status }) {
  const cls = {
    active:    'badge-active',
    completed: 'badge-completed',
    failed:    'badge-failed',
    cancelled: 'badge-cancelled',
    paused:    'badge-pending',
  }
  return <span className={cls[status] || 'badge-completed'}>{status}</span>
}

function TriggerRow({ trigger, onCancel }) {
  const [expanded, setExpanded] = useState(false)
  return (
    <>
      <tr
        className="border-b border-surface-700 hover:bg-surface-700/30 cursor-pointer"
        onClick={() => setExpanded(v => !v)}
      >
        <td className="px-4 py-3">
          <div className="flex items-center gap-2">
            {expanded ? <ChevronUp size={12} className="text-slate-500" /> : <ChevronDown size={12} className="text-slate-500" />}
            <span className="text-sm text-slate-200 font-medium">{trigger.name}</span>
          </div>
        </td>
        <td className="px-4 py-3 text-xs text-slate-400 capitalize">{trigger.trigger_type}</td>
        <td className="px-4 py-3 text-xs text-slate-400 capitalize">{trigger.channel}</td>
        <td className="px-4 py-3 text-xs text-slate-300">{trigger.recipient}</td>
        <td className="px-4 py-3"><StatusBadge status={trigger.status} /></td>
        <td className="px-4 py-3 text-xs text-slate-400">
          {trigger.scheduled_at ? format(new Date(trigger.scheduled_at), 'dd MMM HH:mm') : '—'}
        </td>
        <td className="px-4 py-3">
          {trigger.status === 'active' && (
            <button
              onClick={e => { e.stopPropagation(); onCancel(trigger.id) }}
              className="p-1.5 text-red-400 hover:text-red-300 hover:bg-red-900/30 rounded-lg transition-colors"
              title="Cancel trigger"
            >
              <Trash2 size={13} />
            </button>
          )}
        </td>
      </tr>
      {expanded && (
        <tr className="bg-surface-900/50">
          <td colSpan={7} className="px-6 py-3">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
              <div>
                <p className="text-slate-500 mb-0.5">Message preview</p>
                <p className="text-slate-300">{trigger.message}</p>
              </div>
              <div>
                <p className="text-slate-500 mb-0.5">Delay</p>
                <p className="text-slate-300">{trigger.delay_minutes} min</p>
              </div>
              <div>
                <p className="text-slate-500 mb-0.5">Retries</p>
                <p className="text-slate-300">{trigger.retries_done} / {trigger.max_retries}</p>
              </div>
              {trigger.campaign_name && (
                <div>
                  <p className="text-slate-500 mb-0.5">Campaign</p>
                  <p className="text-slate-300">{trigger.campaign_name} (step {trigger.step_number})</p>
                </div>
              )}
              <div>
                <p className="text-slate-500 mb-0.5">Stop on reply</p>
                <p className="text-slate-300">{trigger.stop_on_reply ? 'Yes' : 'No'}</p>
              </div>
              {trigger.executed_at && (
                <div>
                  <p className="text-slate-500 mb-0.5">Executed at</p>
                  <p className="text-slate-300">{format(new Date(trigger.executed_at), 'dd MMM HH:mm')}</p>
                </div>
              )}
            </div>
          </td>
        </tr>
      )}
    </>
  )
}

function CreateTriggerModal({ onClose, onCreated }) {
  const [form, setForm] = useState({
    name: '', trigger_type: 'follow_up', channel: 'whatsapp',
    recipient: '', recipient_name: '', message: '', subject: '',
    delay_minutes: 60, max_retries: 3, stop_on_reply: true,
  })
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  async function submit(e) {
    e.preventDefault()
    setSaving(true)
    setErr('')
    try {
      await createTrigger(form)
      onCreated()
      onClose()
    } catch (e) {
      setErr(e.message)
    }
    setSaving(false)
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-surface-800 rounded-2xl w-full max-w-lg border border-surface-700 shadow-2xl">
        <div className="flex items-center justify-between px-5 py-4 border-b border-surface-700">
          <h2 className="text-base font-semibold text-white">New Trigger</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">
            <X size={16} />
          </button>
        </div>
        <form onSubmit={submit} className="p-5 space-y-3 overflow-y-auto max-h-[70vh]">
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <label className="text-xs text-slate-400 mb-1 block">Trigger name *</label>
              <input className="input text-sm" value={form.name} onChange={e => set('name', e.target.value)} required />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Type</label>
              <select className="input text-sm" value={form.trigger_type} onChange={e => set('trigger_type', e.target.value)}>
                {TRIGGER_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Channel</label>
              <select className="input text-sm" value={form.channel} onChange={e => set('channel', e.target.value)}>
                {CHANNELS.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Recipient phone *</label>
              <input className="input text-sm" value={form.recipient} onChange={e => set('recipient', e.target.value)} required placeholder="+91 98765 43210" />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Recipient name</label>
              <input className="input text-sm" value={form.recipient_name} onChange={e => set('recipient_name', e.target.value)} placeholder="John Doe" />
            </div>
            {form.channel === 'email' && (
              <div className="col-span-2">
                <label className="text-xs text-slate-400 mb-1 block">Email subject</label>
                <input className="input text-sm" value={form.subject} onChange={e => set('subject', e.target.value)} />
              </div>
            )}
            <div className="col-span-2">
              <label className="text-xs text-slate-400 mb-1 block">Message *</label>
              <textarea rows={3} className="input text-sm resize-none" value={form.message} onChange={e => set('message', e.target.value)} required />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Delay (minutes)</label>
              <input type="number" min={0} max={43200} className="input text-sm" value={form.delay_minutes} onChange={e => set('delay_minutes', Number(e.target.value))} />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Max retries</label>
              <input type="number" min={1} max={10} className="input text-sm" value={form.max_retries} onChange={e => set('max_retries', Number(e.target.value))} />
            </div>
            <div className="col-span-2 flex items-center gap-2">
              <input type="checkbox" id="stopreply" checked={form.stop_on_reply} onChange={e => set('stop_on_reply', e.target.checked)} className="accent-brand-500" />
              <label htmlFor="stopreply" className="text-sm text-slate-300">Stop when lead replies</label>
            </div>
          </div>
          {err && <p className="text-sm text-red-400">{err}</p>}
          <div className="flex gap-2 pt-1">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" disabled={saving} className="btn-primary flex-1">
              {saving ? 'Creating…' : 'Create Trigger'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function CreateDripModal({ onClose, onCreated }) {
  const [form, setForm] = useState({
    name: '', channel: 'whatsapp', recipient: '', recipient_name: '',
    subject_prefix: '', delay_between_minutes: 1440, stop_on_reply: true,
    messages: ['', ''],
  })
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState('')

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))
  const setMsg = (i, v) => setForm(f => {
    const msgs = [...f.messages]; msgs[i] = v; return { ...f, messages: msgs }
  })

  async function submit(e) {
    e.preventDefault()
    setSaving(true)
    setErr('')
    try {
      const payload = { ...form, messages: form.messages.filter(m => m.trim()) }
      await createDripCampaign(payload)
      onCreated()
      onClose()
    } catch (e) {
      setErr(e.message)
    }
    setSaving(false)
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-surface-800 rounded-2xl w-full max-w-lg border border-surface-700 shadow-2xl">
        <div className="flex items-center justify-between px-5 py-4 border-b border-surface-700">
          <h2 className="text-base font-semibold text-white flex items-center gap-2">
            <Layers size={16} className="text-brand-400" /> New Drip Campaign
          </h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200"><X size={16} /></button>
        </div>
        <form onSubmit={submit} className="p-5 space-y-3 overflow-y-auto max-h-[70vh]">
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <label className="text-xs text-slate-400 mb-1 block">Campaign name *</label>
              <input className="input text-sm" value={form.name} onChange={e => set('name', e.target.value)} required />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Channel</label>
              <select className="input text-sm" value={form.channel} onChange={e => set('channel', e.target.value)}>
                {CHANNELS.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Delay between steps (min)</label>
              <input type="number" min={0} className="input text-sm" value={form.delay_between_minutes} onChange={e => set('delay_between_minutes', Number(e.target.value))} />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Recipient phone *</label>
              <input className="input text-sm" value={form.recipient} onChange={e => set('recipient', e.target.value)} required />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Recipient name</label>
              <input className="input text-sm" value={form.recipient_name} onChange={e => set('recipient_name', e.target.value)} />
            </div>
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs text-slate-400">Messages (steps)</label>
              <button type="button" onClick={() => setForm(f => ({ ...f, messages: [...f.messages, ''] }))}
                className="text-xs text-brand-400 hover:text-brand-300">+ Add step</button>
            </div>
            {form.messages.map((m, i) => (
              <div key={i} className="flex gap-2 mb-2">
                <span className="text-xs text-slate-500 w-5 flex-shrink-0 mt-2.5">{i + 1}.</span>
                <textarea rows={2} className="input text-sm resize-none flex-1" placeholder={`Step ${i + 1} message`}
                  value={m} onChange={e => setMsg(i, e.target.value)} />
                {form.messages.length > 1 && (
                  <button type="button" onClick={() => setForm(f => ({ ...f, messages: f.messages.filter((_, j) => j !== i) }))}
                    className="text-slate-500 hover:text-red-400 mt-2">
                    <X size={13} />
                  </button>
                )}
              </div>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" id="ds" checked={form.stop_on_reply} onChange={e => set('stop_on_reply', e.target.checked)} className="accent-brand-500" />
            <label htmlFor="ds" className="text-sm text-slate-300">Stop when lead replies</label>
          </div>
          {err && <p className="text-sm text-red-400">{err}</p>}
          <div className="flex gap-2 pt-1">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
            <button type="submit" disabled={saving} className="btn-primary flex-1">
              {saving ? 'Creating…' : 'Launch Campaign'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function TriggersPage() {
  const [triggers, setTriggers] = useState([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [showDrip, setShowDrip] = useState(false)

  async function load() {
    setLoading(true)
    try {
      const data = await getTriggers(statusFilter || undefined)
      setTriggers(data.triggers || [])
    } catch {}
    setLoading(false)
  }

  useEffect(() => { load() }, [statusFilter])

  async function handleCancel(id) {
    if (!confirm('Cancel this trigger?')) return
    await cancelTrigger(id)
    load()
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-5">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-white">Triggers</h1>
          <p className="text-sm text-slate-400 mt-0.5">Automated & scheduled messages</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <button onClick={() => setShowDrip(true)} className="btn-secondary flex items-center gap-2 text-sm">
            <Layers size={14} /> Drip Campaign
          </button>
          <button onClick={() => setShowCreate(true)} className="btn-primary flex items-center gap-2 text-sm">
            <Plus size={14} /> New Trigger
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 flex-wrap">
        {['', 'active', 'completed', 'failed', 'cancelled'].map(s => (
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
        <button onClick={load} className="ml-auto text-slate-400 hover:text-slate-200">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {/* Table */}
      <div className="card p-0 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-surface-700">
                {['Name', 'Type', 'Channel', 'Recipient', 'Status', 'Scheduled At', ''].map(h => (
                  <th key={h} className="px-4 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-500 text-sm">Loading…</td></tr>
              ) : triggers.length === 0 ? (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-slate-500 text-sm">No triggers found.</td></tr>
              ) : (
                triggers.map(t => (
                  <TriggerRow key={t.id} trigger={t} onCancel={handleCancel} />
                ))
              )}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-2 border-t border-surface-700 text-xs text-slate-500">
          {triggers.length} trigger{triggers.length !== 1 ? 's' : ''}
        </div>
      </div>

      {showCreate && <CreateTriggerModal onClose={() => setShowCreate(false)} onCreated={load} />}
      {showDrip   && <CreateDripModal   onClose={() => setShowDrip(false)}   onCreated={load} />}
    </div>
  )
}