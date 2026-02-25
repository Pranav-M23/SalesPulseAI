import { useState, useEffect, useRef, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Search, Send, RefreshCw, Phone, MessageSquare,
  Smartphone, Plus, ChevronDown,
} from 'lucide-react'
import { getContacts, getConversation, sendToContact } from '../api/client'
import { formatDistanceToNow, format, isToday, isYesterday } from 'date-fns'

function ContactItem({ contact, isSelected, onClick }) {
  const last = contact.last_message || ''
  const ts = contact.last_at ? new Date(contact.last_at) : null
  const timeStr = ts
    ? isToday(ts) ? format(ts, 'HH:mm')
    : isYesterday(ts) ? 'Yesterday'
    : format(ts, 'dd MMM')
    : ''

  return (
    <button
      onClick={onClick}
      className={`w-full flex items-start gap-3 px-3 py-3 text-left transition-colors border-b border-surface-700/50 ${
        isSelected ? 'bg-surface-700' : 'hover:bg-surface-700/50'
      }`}
    >
      <div className="w-10 h-10 rounded-full bg-brand-800 flex items-center justify-center text-brand-300 text-sm font-bold flex-shrink-0">
        {contact.phone_number.slice(-2)}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <span className="text-sm font-medium text-slate-200 truncate">{contact.phone_number}</span>
          <span className="text-[10px] text-slate-500 flex-shrink-0">{timeStr}</span>
        </div>
        <p className="text-xs text-slate-500 truncate mt-0.5">
          {contact.last_role === 'assistant' ? '→ ' : ''}{last}
        </p>
      </div>
    </button>
  )
}

function DateDivider({ label }) {
  return (
    <div className="flex items-center gap-3 py-2 px-4">
      <div className="flex-1 h-px bg-surface-700" />
      <span className="text-[10px] text-slate-500 uppercase tracking-wider">{label}</span>
      <div className="flex-1 h-px bg-surface-700" />
    </div>
  )
}

function MessageBubble({ msg }) {
  const isUser = msg.role === 'user'
  const ts = msg.timestamp ? new Date(msg.timestamp) : null
  const timeStr = ts ? format(ts, 'HH:mm') : ''

  return (
    <div className={`flex ${isUser ? 'justify-start' : 'justify-end'} px-4 py-0.5`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-2.5 shadow-sm ${
          isUser
            ? 'bg-surface-700 text-slate-100 rounded-tl-sm'
            : 'bg-brand-700 text-white rounded-tr-sm'
        }`}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">{msg.message}</p>
        <div className={`flex items-center gap-1 mt-1 ${isUser ? 'justify-start' : 'justify-end'}`}>
          <span className="text-[10px] opacity-60">{timeStr}</span>
          {msg.channel && (
            <span className="text-[10px] opacity-50 capitalize">· {msg.channel}</span>
          )}
        </div>
      </div>
    </div>
  )
}

function groupMessagesByDate(messages) {
  const groups = []
  let lastDate = null
  for (const msg of messages) {
    const ts = msg.timestamp ? new Date(msg.timestamp) : null
    const dateKey = ts ? format(ts, 'yyyy-MM-dd') : 'unknown'
    if (dateKey !== lastDate) {
      const label = ts
        ? isToday(ts) ? 'Today'
        : isYesterday(ts) ? 'Yesterday'
        : format(ts, 'MMMM d, yyyy')
        : ''
      groups.push({ type: 'date', label, key: dateKey })
      lastDate = dateKey
    }
    groups.push({ type: 'msg', msg })
  }
  return groups
}

const CHANNELS = ['whatsapp', 'sms']

export default function ChatPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [contacts, setContacts] = useState([])
  const [search, setSearch] = useState('')
  const [selectedPhone, setSelectedPhone] = useState(searchParams.get('phone') || null)
  const [messages, setMessages] = useState([])
  const [inputText, setInputText] = useState('')
  const [channel, setChannel] = useState('whatsapp')
  const [sending, setSending] = useState(false)
  const [loadingContacts, setLoadingContacts] = useState(true)
  const [loadingMsgs, setLoadingMsgs] = useState(false)
  const [newPhone, setNewPhone] = useState('')
  const [showNewPhone, setShowNewPhone] = useState(false)
  const bottomRef = useRef(null)
  const pollRef = useRef(null)

  // Load contacts
  const loadContacts = useCallback(async () => {
    try {
      const data = await getContacts()
      setContacts(data.contacts || [])
    } catch {}
    setLoadingContacts(false)
  }, [])

  // Load messages for selected phone
  const loadMessages = useCallback(async (phone) => {
    if (!phone) return
    setLoadingMsgs(true)
    try {
      const data = await getConversation(phone, 200)
      setMessages(data.messages || [])
    } catch {}
    setLoadingMsgs(false)
  }, [])

  useEffect(() => { loadContacts() }, [loadContacts])

  useEffect(() => {
    if (selectedPhone) {
      loadMessages(selectedPhone)
      // Poll for new messages every 4 seconds
      clearInterval(pollRef.current)
      pollRef.current = setInterval(() => {
        loadMessages(selectedPhone)
        loadContacts()
      }, 4000)
    }
    return () => clearInterval(pollRef.current)
  }, [selectedPhone, loadMessages, loadContacts])

  // Scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function selectContact(phone) {
    setSelectedPhone(phone)
    setSearchParams({ phone })
  }

  async function handleSend() {
    if (!inputText.trim() || !selectedPhone || sending) return
    const text = inputText.trim()
    setInputText('')
    setSending(true)
    // Optimistically append
    setMessages(prev => [...prev, {
      role: 'assistant',
      message: text,
      channel,
      timestamp: new Date().toISOString(),
    }])
    try {
      await sendToContact(selectedPhone, text, channel)
      await loadMessages(selectedPhone)
      await loadContacts()
    } catch (e) {
      alert(`Send failed: ${e.message}`)
    }
    setSending(false)
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const filtered = contacts.filter(c =>
    c.phone_number.toLowerCase().includes(search.toLowerCase())
  )

  const groups = groupMessagesByDate(messages)

  return (
    <div className="flex-1 flex overflow-hidden">
      {/* ─── Contacts Sidebar ─── */}
      <aside className="w-72 flex-shrink-0 flex flex-col border-r border-surface-700 bg-surface-800">
        {/* Sidebar header */}
        <div className="px-3 pt-4 pb-3 border-b border-surface-700">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-slate-200">Conversations</h2>
            <button
              onClick={() => setShowNewPhone(v => !v)}
              className="text-brand-400 hover:text-brand-300 transition-colors"
              title="Start new conversation"
            >
              <Plus size={16} />
            </button>
          </div>

          {showNewPhone && (
            <div className="mb-3 flex gap-2">
              <input
                className="input text-xs py-1.5 flex-1"
                placeholder="+91 98765 43210"
                value={newPhone}
                onChange={e => setNewPhone(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter' && newPhone.trim()) {
                    selectContact(newPhone.trim())
                    setNewPhone('')
                    setShowNewPhone(false)
                  }
                }}
              />
              <button
                className="btn-primary text-xs py-1.5 px-3"
                onClick={() => {
                  if (newPhone.trim()) {
                    selectContact(newPhone.trim())
                    setNewPhone('')
                    setShowNewPhone(false)
                  }
                }}
              >
                Open
              </button>
            </div>
          )}

          <div className="relative">
            <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              className="input text-xs py-2 pl-8"
              placeholder="Search contacts..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
        </div>

        {/* Contact list */}
        <div className="flex-1 overflow-y-auto">
          {loadingContacts ? (
            <div className="p-6 text-center text-slate-500 text-sm">Loading...</div>
          ) : filtered.length === 0 ? (
            <div className="p-6 text-center text-slate-500 text-sm">
              {search ? 'No matches' : 'No conversations yet.'}
            </div>
          ) : (
            filtered.map(c => (
              <ContactItem
                key={c.phone_number}
                contact={c}
                isSelected={c.phone_number === selectedPhone}
                onClick={() => selectContact(c.phone_number)}
              />
            ))
          )}
        </div>
      </aside>

      {/* ─── Chat Window ─── */}
      {selectedPhone ? (
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Chat header */}
          <div className="flex items-center justify-between px-5 py-3.5 border-b border-surface-700 bg-surface-800">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-brand-800 flex items-center justify-center text-brand-300 text-sm font-bold">
                {selectedPhone.slice(-2)}
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-200">{selectedPhone}</p>
                <p className="text-xs text-slate-500 capitalize">via {channel}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => loadMessages(selectedPhone)}
                className="p-2 text-slate-400 hover:text-slate-200 hover:bg-surface-700 rounded-lg transition-colors"
                title="Refresh"
              >
                <RefreshCw size={14} className={loadingMsgs ? 'animate-spin' : ''} />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto py-3 space-y-0.5 bg-surface-900">
            {loadingMsgs && messages.length === 0 ? (
              <div className="flex items-center justify-center h-full text-slate-500 text-sm">
                Loading messages...
              </div>
            ) : messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full gap-3 text-slate-500">
                <MessageSquare size={40} className="opacity-20" />
                <p className="text-sm">No messages yet. Send the first one!</p>
              </div>
            ) : (
              groups.map((item, i) =>
                item.type === 'date'
                  ? <DateDivider key={`date-${i}`} label={item.label} />
                  : <MessageBubble key={i} msg={item.msg} />
              )
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input area */}
          <div className="border-t border-surface-700 bg-surface-800 px-4 py-3">
            {/* Channel picker */}
            <div className="flex items-center gap-2 mb-2">
              {CHANNELS.map(ch => (
                <button
                  key={ch}
                  onClick={() => setChannel(ch)}
                  className={`flex items-center gap-1 text-xs px-2.5 py-1 rounded-full transition-colors capitalize ${
                    channel === ch
                      ? 'bg-brand-600 text-white'
                      : 'bg-surface-700 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {ch === 'whatsapp' ? <Phone size={10} /> : <Smartphone size={10} />}
                  {ch}
                </button>
              ))}
            </div>
            <div className="flex gap-2">
              <textarea
                rows={2}
                className="input text-sm resize-none leading-snug flex-1 py-2.5"
                placeholder={`Message via ${channel}... (Enter to send, Shift+Enter for newline)`}
                value={inputText}
                onChange={e => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
              />
              <button
                onClick={handleSend}
                disabled={!inputText.trim() || sending}
                className="btn-primary self-end px-4 py-2.5 flex items-center gap-1.5"
              >
                <Send size={14} />
                {sending ? 'Sending…' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 text-slate-500">
          <MessageSquare size={56} className="opacity-10" />
          <div className="text-center">
            <p className="text-lg font-medium text-slate-400">Select a conversation</p>
            <p className="text-sm mt-1">Or click <strong>+</strong> to start a new one</p>
          </div>
        </div>
      )}
    </div>
  )
}