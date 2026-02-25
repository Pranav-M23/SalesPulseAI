import { useState } from 'react'
import {
  Wand2, Copy, Send, Check, ChevronDown,
  Star, MessageSquare, Mail,
} from 'lucide-react'
import { generateMessage, sendWhatsApp, sendSMS, sendEmail } from '../api/client'

// Must match backend SalesStage and MessageTone enums exactly
const STAGES = ['prospecting', 'qualification', 'proposal', 'negotiation', 'closing', 'follow_up', 're_engagement']
const TONES  = ['formal', 'friendly', 'urgent', 'consultative', 'casual']

function ScoreBar({ score }) {
  const pct = Math.round((score || 0) * 100)
  const color = pct >= 75 ? 'bg-brand-500' : pct >= 50 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-2 bg-surface-700 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all duration-700`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-sm font-bold text-slate-200 w-10 text-right">{pct}</span>
    </div>
  )
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)
  function copy() {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <button onClick={copy} className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-surface-700 rounded transition-colors">
      {copied ? <Check size={13} className="text-brand-400" /> : <Copy size={13} />}
    </button>
  )
}

function SendModal({ result, onClose }) {
  const [tab, setTab] = useState('whatsapp')
  const [to, setTo] = useState('')
  const [subject, setSubject] = useState(result.subject || '')
  const [sending, setSending] = useState(false)
  const [sent, setSent] = useState(false)
  const [err, setErr] = useState('')

  async function doSend() {
    if (!to.trim()) return
    setSending(true)
    setErr('')
    try {
      if (tab === 'whatsapp') await sendWhatsApp(to, result.message)
      else if (tab === 'sms')  await sendSMS(to, result.message)
      else await sendEmail(to, subject, result.message)
      setSent(true)
    } catch (e) {
      setErr(e.message)
    }
    setSending(false)
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-surface-800 rounded-2xl w-full max-w-md border border-surface-700 shadow-2xl">
        <div className="flex items-center justify-between px-5 py-4 border-b border-surface-700">
          <h2 className="text-base font-semibold text-white">Send Generated Message</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">✕</button>
        </div>
        <div className="p-5 space-y-4">
          {/* Channel tabs */}
          <div className="flex gap-1 bg-surface-900 p-1 rounded-lg">
            {['whatsapp', 'sms', 'email'].map(ch => (
              <button
                key={ch}
                onClick={() => setTab(ch)}
                className={`flex-1 py-1.5 text-xs rounded-md transition-colors capitalize ${
                  tab === ch ? 'bg-brand-600 text-white' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {ch}
              </button>
            ))}
          </div>

          <div>
            <label className="text-xs text-slate-400 mb-1 block">
              {tab === 'email' ? 'Email address' : 'Phone number'}
            </label>
            <input
              className="input text-sm"
              value={to}
              onChange={e => setTo(e.target.value)}
              placeholder={tab === 'email' ? 'name@example.com' : '+91 98765 43210'}
            />
          </div>

          {tab === 'email' && (
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Subject</label>
              <input className="input text-sm" value={subject} onChange={e => setSubject(e.target.value)} />
            </div>
          )}

          <div>
            <label className="text-xs text-slate-400 mb-1 block">Message preview</label>
            <div className="bg-surface-900 rounded-lg p-3 text-xs text-slate-300 max-h-28 overflow-y-auto leading-relaxed">
              {result.message}
            </div>
          </div>

          {sent ? (
            <div className="flex items-center gap-2 text-brand-400 text-sm">
              <Check size={16} /> Sent successfully!
            </div>
          ) : (
            <>
              {err && <p className="text-sm text-red-400">{err}</p>}
              <button onClick={doSend} disabled={sending || !to.trim()} className="btn-primary w-full flex items-center justify-center gap-2">
                <Send size={14} /> {sending ? 'Sending…' : 'Send Now'}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default function GeneratorPage() {
  const [form, setForm] = useState({
    name: '', role: '', company: '', industry: '',
    pain_point: '', stage: 'prospecting', tone: 'friendly',
    use_ai_rewrite: true,
  })
  const [result, setResult] = useState(null)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [showSend, setShowSend] = useState(false)

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  async function generate(e) {
    e.preventDefault()
    setGenerating(true)
    setError('')
    setResult(null)
    try {
      const data = await generateMessage(form)
      setResult(data)
    } catch (e) {
      setError(e.message)
    }
    setGenerating(false)
  }

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-xl font-bold text-white">Message Generator</h1>
          <p className="text-sm text-slate-400 mt-0.5">AI-powered personalized sales messages</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
          {/* Form */}
          <div className="lg:col-span-2">
            <div className="card space-y-3">
              <h2 className="text-sm font-semibold text-slate-200 mb-1">Lead Details</h2>
              <form onSubmit={generate} className="space-y-3">
                <div>
                  <label className="text-xs text-slate-400 mb-1 block">Lead name *</label>
                  <input className="input text-sm" value={form.name} onChange={e => set('name', e.target.value)} required placeholder="John Doe" />
                </div>
                <div>
                  <label className="text-xs text-slate-400 mb-1 block">Role / Job title</label>
                  <input className="input text-sm" value={form.role} onChange={e => set('role', e.target.value)} placeholder="Head of Sales" />
                </div>
                <div>
                  <label className="text-xs text-slate-400 mb-1 block">Company</label>
                  <input className="input text-sm" value={form.company} onChange={e => set('company', e.target.value)} placeholder="Acme Corp" />
                </div>
                <div>
                  <label className="text-xs text-slate-400 mb-1 block">Industry</label>
                  <input className="input text-sm" value={form.industry} onChange={e => set('industry', e.target.value)} placeholder="SaaS / E-commerce" />
                </div>
                <div>
                  <label className="text-xs text-slate-400 mb-1 block">Pain point</label>
                  <textarea rows={2} className="input text-sm resize-none" value={form.pain_point} onChange={e => set('pain_point', e.target.value)} placeholder="Low conversion rates, manual follow-ups…" />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-slate-400 mb-1 block">Stage</label>
                    <select className="input text-sm" value={form.stage} onChange={e => set('stage', e.target.value)}>
                      {STAGES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 mb-1 block">Tone</label>
                    <select className="input text-sm" value={form.tone} onChange={e => set('tone', e.target.value)}>
                      {TONES.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </div>
                </div>
                <div className="flex items-center gap-2 pt-1">
                  <input type="checkbox" id="airewrite" checked={form.use_ai_rewrite} onChange={e => set('use_ai_rewrite', e.target.checked)} className="accent-brand-500" />
                  <label htmlFor="airewrite" className="text-xs text-slate-300">AI rewrite (Groq)</label>
                </div>
                {error && <p className="text-sm text-red-400">{error}</p>}
                <button type="submit" disabled={generating} className="btn-primary w-full flex items-center justify-center gap-2">
                  <Wand2 size={14} />
                  {generating ? 'Generating…' : 'Generate Message'}
                </button>
              </form>
            </div>
          </div>

          {/* Result */}
          <div className="lg:col-span-3 space-y-4">
            {generating && (
              <div className="card flex items-center justify-center py-16 text-slate-500">
                <div className="text-center space-y-2">
                  <Wand2 size={32} className="mx-auto animate-pulse text-brand-500" />
                  <p className="text-sm">Generating with AI…</p>
                </div>
              </div>
            )}

            {result && !generating && (
              <>
                {/* Score */}
                <div className="card">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                      <Star size={14} className="text-yellow-400" /> Message Score
                    </h3>
                    <span className="text-xs text-slate-400 capitalize">
                      {result.stage} · {result.tone}
                    </span>
                  </div>
                  <ScoreBar score={result.score} />
                </div>

                {/* Subject */}
                {result.subject && (
                  <div className="card">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-xs font-medium text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                        <Mail size={11} /> Subject Line
                      </h3>
                      <CopyButton text={result.subject} />
                    </div>
                    <p className="text-sm text-slate-100">{result.subject}</p>
                  </div>
                )}

                {/* Message body */}
                <div className="card">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-xs font-medium text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                      <MessageSquare size={11} /> Message Body
                    </h3>
                    <CopyButton text={result.message} />
                  </div>
                  <p className="text-sm text-slate-100 whitespace-pre-wrap leading-relaxed">{result.message}</p>
                </div>

                {/* CTA */}
                {result.cta && (
                  <div className="card">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-xs font-medium text-slate-400 uppercase tracking-wider">CTA</h3>
                      <CopyButton text={result.cta} />
                    </div>
                    <p className="text-sm text-brand-300 font-medium">{result.cta}</p>
                  </div>
                )}

                {/* Actions */}
                <button
                  onClick={() => setShowSend(true)}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  <Send size={14} /> Send this Message
                </button>
              </>
            )}

            {!result && !generating && (
              <div className="card flex flex-col items-center justify-center py-16 text-slate-600 gap-3">
                <Wand2 size={40} className="opacity-20" />
                <p className="text-sm">Fill in the form and click Generate.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {showSend && result && (
        <SendModal result={result} onClose={() => setShowSend(false)} />
      )}
    </div>
  )
}