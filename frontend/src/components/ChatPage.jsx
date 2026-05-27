import { useState, useRef, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { sessionsAPI, ordersAPI, streamChat } from '../utils/api'
import {
  Plus, Trash2, LogOut, Send, Loader,
  Bot, User, Package, ChevronLeft, ChevronRight,
  MessageSquare, ShoppingBag, RefreshCw,
} from 'lucide-react'
import { format, isToday, isYesterday } from 'date-fns'

// ── Helpers ───────────────────────────────────────────────────────────────────

function md(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>')
}

function groupSessions(sessions) {
  const g = { Today: [], Yesterday: [], Earlier: [] }
  sessions.forEach((s) => {
    const d = new Date(s.updated_at)
    if (isToday(d))          g.Today.push(s)
    else if (isYesterday(d)) g.Yesterday.push(s)
    else                     g.Earlier.push(s)
  })
  return g
}

const STATUS_COLOR = {
  Processing: '#f59e0b',
  Shipped:    '#3b82f6',
  Delivered:  '#10b981',
  Closed:     '#6b7280',
}

const QUICK = [
  'place order',
  'my orders',
  'track order',
  'speed up order',
  'swap order',
  'cancel order',
]

// ── Sub-components ────────────────────────────────────────────────────────────

function Bubble({ msg }) {
  const bot = msg.role === 'bot'
  return (
    <div style={{ ...s.row, justifyContent: bot ? 'flex-start' : 'flex-end' }}>
      {bot && (
        <div style={{ ...s.avatar, background: 'rgba(79,124,255,.12)',
          color: 'var(--accent)', border: '1px solid var(--accent)' }}>
          <Bot size={14} />
        </div>
      )}
      <div style={{
        ...s.bubble,
        background:   bot ? 'var(--bot-bg)' : 'var(--user-bg)',
        border:       bot ? '1px solid var(--border)'
                          : '1px solid rgba(79,124,255,.3)',
        borderBottomLeftRadius:  bot ? 4 : 14,
        borderBottomRightRadius: bot ? 14 : 4,
      }}>
        <div dangerouslySetInnerHTML={{ __html: md(msg.content) }} />
        <div style={s.ts}>
          {format(new Date(msg.created_at || msg.ts), 'HH:mm')}
        </div>
      </div>
      {!bot && (
        <div style={{ ...s.avatar, background: 'var(--s3)',
          color: 'var(--text2)', border: '1px solid var(--border2)' }}>
          <User size={14} />
        </div>
      )}
    </div>
  )
}

function Typing() {
  return (
    <div style={{ ...s.row, justifyContent: 'flex-start' }}>
      <div style={{ ...s.avatar, background: 'rgba(79,124,255,.12)',
        color: 'var(--accent)', border: '1px solid var(--accent)' }}>
        <Bot size={14} />
      </div>
      <div style={{ ...s.bubble, background: 'var(--bot-bg)',
        border: '1px solid var(--border)', display: 'flex',
        gap: 5, alignItems: 'center', padding: '12px 14px' }}>
        {[0, 200, 400].map((d) => (
          <div key={d} style={{
            width: 6, height: 6, borderRadius: '50%',
            background: 'var(--accent)',
            animation: `bounce 1.1s ${d}ms infinite ease-in-out`,
          }} />
        ))}
      </div>
    </div>
  )
}

function StreamBubble({ text }) {
  return (
    <div style={{ ...s.row, justifyContent: 'flex-start' }}>
      <div style={{ ...s.avatar, background: 'rgba(79,124,255,.12)',
        color: 'var(--accent)', border: '1px solid var(--accent)' }}>
        <Bot size={14} />
      </div>
      <div style={{ ...s.bubble, background: 'var(--bot-bg)',
        border: '1px solid var(--border)',
        borderBottomLeftRadius: 4 }}>
        <div dangerouslySetInnerHTML={{ __html: md(text) }} />
        <span style={{ color: 'var(--accent)', fontSize: 12,
          animation: 'blink .65s steps(1) infinite' }}>▋</span>
      </div>
    </div>
  )
}

function OrderCard({ o }) {
  const color = STATUS_COLOR[o.status] || '#6b7280'
  const date  = o.delivery_date
    ? format(new Date(o.delivery_date), 'dd MMM yyyy') : 'TBD'
  return (
    <div style={s.orderCard}>
      <div style={{ display: 'flex', justifyContent: 'space-between',
        alignItems: 'center', marginBottom: 3 }}>
        <span style={{ fontSize: 11, fontWeight: 700,
          color: 'var(--text2)', fontFamily: 'monospace' }}>
          #{o.id}
        </span>
        <span style={{ fontSize: 10, fontWeight: 600, color,
          border: `1px solid ${color}`, borderRadius: 99,
          padding: '1px 7px' }}>
          {o.status}
        </span>
      </div>
      <p style={{ fontSize: 12.5, fontWeight: 500,
        overflow: 'hidden', whiteSpace: 'nowrap',
        textOverflow: 'ellipsis' }}>
        {o.product}
      </p>
      <p style={{ fontSize: 11, color: 'var(--text2)', marginTop: 2 }}>
        Qty: {o.quantity} · {date}
      </p>
    </div>
  )
}

// ── Main ──────────────────────────────────────────────────────────────────────

export default function ChatPage() {
  const { user, logout }          = useAuth()
  const navigate                  = useNavigate()
  const [sessions,   setSessions] = useState([])
  const [activeId,   setActiveId] = useState(null)
  const [messages,   setMessages] = useState([])
  const [streaming,  setStreaming] = useState(false)
  const [streamText, setStreamText] = useState('')
  const [input,      setInput]    = useState('')
  const [orders,     setOrders]   = useState([])
  const [leftOpen,   setLeftOpen] = useState(true)
  const [rightOpen,  setRightOpen] = useState(true)
  const [loading,    setLoading]  = useState(false)

  const endRef   = useRef(null)
  const inputRef = useRef(null)
  const abortRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamText])

  const loadSessions = useCallback(async () => {
    try {
      const { data } = await sessionsAPI.list()
      setSessions(data)
      if (data.length > 0 && !activeId) openSession(data[0].id)
    } catch { /* ignore */ }
  }, []) // eslint-disable-line

  useEffect(() => { loadSessions() }, [loadSessions])

  const loadOrders = useCallback(async () => {
    try {
      const { data } = await ordersAPI.list()
      setOrders(data)
    } catch { /* ignore */ }
  }, [])

  useEffect(() => { loadOrders() }, [loadOrders])

  const openSession = useCallback(async (id) => {
    setLoading(true)
    setActiveId(id)
    setStreamText('')
    try {
      const { data } = await sessionsAPI.get(id)
      setMessages(data.messages || [])
    } catch { setMessages([]) }
    finally { setLoading(false) }
  }, [])

  const newChat = useCallback(() => {
    setActiveId(null)
    setMessages([])
    setStreamText('')
    inputRef.current?.focus()
  }, [])

  const deleteSession = useCallback(async (e, id) => {
    e.stopPropagation()
    try { await sessionsAPI.delete(id) } catch { /* ignore */ }
    setSessions((p) => p.filter((s) => s.id !== id))
    if (activeId === id) { setActiveId(null); setMessages([]) }
  }, [activeId])

  const send = useCallback(async (text) => {
    const msg = (text || input).trim()
    if (!msg || streaming) return

    let sid = activeId
    if (!sid) {
      sid = crypto.randomUUID()
      setActiveId(sid)
    }

    setInput('')
    setMessages((p) => [...p, {
      role: 'user', content: msg, ts: new Date().toISOString(),
    }])
    setStreaming(true)
    setStreamText('')

    let acc = ''

    abortRef.current = streamChat(sid, msg, {
      onToken: (token) => {
        acc += token
        setStreamText(acc)
      },
      onDone: () => {
        setMessages((p) => [...p, {
          role: 'bot', content: acc, ts: new Date().toISOString(),
        }])
        setStreamText('')
        setStreaming(false)
        loadOrders()
        loadSessions()
        inputRef.current?.focus()
      },
      onError: (detail) => {
        setMessages((p) => [...p, {
          role: 'bot',
          content: `⚠️ ${detail}`,
          ts: new Date().toISOString(),
        }])
        setStreamText('')
        setStreaming(false)
      },
    })
  }, [input, streaming, activeId, loadOrders, loadSessions])

  const onKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
  }

  const doLogout = () => {
    abortRef.current?.abort()
    logout()
    navigate('/login')
  }

  const groups = groupSessions(sessions)

  return (
    <div style={s.shell}>
      <style>{`
        @keyframes bounce {
          0%,60%,100% { transform:translateY(0); opacity:.4 }
          30% { transform:translateY(-6px); opacity:1 }
        }
        @keyframes blink { 50% { opacity:0 } }
        @keyframes spin   { to { transform:rotate(360deg) } }
        strong { color: #5ee7c8 }
        input:focus, textarea:focus { outline: none;
          border-color: var(--accent) !important; }
      `}</style>

      {/* ── Left sidebar ─────────────────────────────────────────────────── */}
      <aside style={{ ...s.sideLeft,
        width: leftOpen ? 250 : 50, minWidth: leftOpen ? 250 : 50 }}>

        <div style={s.sideTop}>
          {leftOpen && (
            <button style={s.newBtn} onClick={newChat}>
              <Plus size={14} /> New Chat
            </button>
          )}
          <button style={s.iconBtn}
            onClick={() => setLeftOpen((v) => !v)}>
            {leftOpen
              ? <ChevronLeft size={16} />
              : <Plus size={16} />}
          </button>
        </div>

        {leftOpen && (
          <div style={s.sessionList}>
            {sessions.length === 0 && (
              <p style={s.empty}>No chats yet</p>
            )}
            {Object.entries(groups).map(([label, items]) =>
              items.length === 0 ? null : (
                <div key={label}>
                  <p style={s.groupLabel}>{label}</p>
                  {items.map((sess) => (
                    <div
                      key={sess.id}
                      style={{
                        ...s.sessionItem,
                        background: sess.id === activeId
                          ? 'var(--s3)' : 'transparent',
                      }}
                      onClick={() => openSession(sess.id)}
                    >
                      <MessageSquare size={12}
                        style={{ color: 'var(--text3)', flexShrink: 0 }} />
                      <span style={s.sessionTitle}>{sess.title}</span>
                      <button style={s.delBtn}
                        onClick={(e) => deleteSession(e, sess.id)}>
                        <Trash2 size={11} />
                      </button>
                    </div>
                  ))}
                </div>
              )
            )}
          </div>
        )}

        <div style={s.sideFooter}>
          {leftOpen && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1, minWidth: 0 }}>
              <div style={s.avatar2}>{user?.name?.[0]}</div>
              <div style={{ minWidth: 0 }}>
                <p style={{ fontSize: 12.5, fontWeight: 600,
                  whiteSpace: 'nowrap', overflow: 'hidden',
                  textOverflow: 'ellipsis' }}>
                  {user?.name}
                </p>
                <p style={{ fontSize: 11, color: 'var(--text2)',
                  textTransform: 'capitalize' }}>
                  {user?.role}
                </p>
              </div>
            </div>
          )}
          <button style={s.iconBtn} onClick={doLogout} title="Sign out">
            <LogOut size={15} />
          </button>
        </div>
      </aside>

      {/* ── Chat main ─────────────────────────────────────────────────────── */}
      <main style={s.chatMain}>

        {/* Header */}
        <div style={s.chatHeader}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={s.chatIcon}><Package size={18} /></div>
            <div>
              <p style={{ fontSize: 15, fontWeight: 700 }}>OrderBot</p>
              <p style={{ fontSize: 11, color: 'var(--text2)' }}>
                Supply Chain Assistant
              </p>
            </div>
          </div>
          {activeId && (
            <p style={{ fontSize: 10, color: 'var(--text3)',
              fontFamily: 'monospace' }}>
              {activeId.slice(0, 8)}…
            </p>
          )}
        </div>

        {/* Messages */}
        <div style={s.messages}>
          {!activeId && !loading && (
            <div style={s.emptyState}>
              <div style={s.emptyIcon}><Bot size={36} /></div>
              <h2 style={{ fontSize: 18, fontWeight: 600 }}>
                Welcome, {user?.name?.split(' ')[0]}!
              </h2>
              <p style={{ fontSize: 13, color: 'var(--text2)' }}>
                Click <strong>New Chat</strong> or select one from the sidebar.
              </p>
            </div>
          )}

          {loading && (
            <div style={s.emptyState}>
              <Loader size={24} style={{ animation: 'spin .7s linear infinite' }} />
            </div>
          )}

          {!loading && messages.map((m, i) => (
            <Bubble key={i} msg={m} />
          ))}

          {streaming && streamText === '' && <Typing />}
          {streaming && streamText !== '' && <StreamBubble text={streamText} />}

          <div ref={endRef} />
        </div>

        {/* Quick actions */}
        {activeId && messages.length === 0 && !streaming && (
          <div style={s.quickBar}>
            {QUICK.map((q) => (
              <button key={q} style={s.quickChip} onClick={() => send(q)}>
                {q}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div style={s.inputRow}>
          <textarea
            ref={inputRef}
            style={s.chatInput}
            placeholder="Type a message…"
            value={input}
            rows={1}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKey}
            disabled={streaming}
          />
          <button
            style={{
              ...s.sendBtn,
              opacity: (!input.trim() || streaming) ? 0.45 : 1,
              cursor:  (!input.trim() || streaming) ? 'not-allowed' : 'pointer',
            }}
            onClick={() => send()}
            disabled={!input.trim() || streaming}
          >
            {streaming
              ? <Loader size={16} style={{ animation: 'spin .7s linear infinite' }} />
              : <Send size={16} />}
          </button>
        </div>
      </main>

      {/* ── Right sidebar: orders ──────────────────────────────────────────── */}
      <aside style={{ ...s.sideRight,
        width: rightOpen ? 240 : 50, minWidth: rightOpen ? 240 : 50 }}>

        <div style={{ ...s.sideTop, gap: 6 }}>
          <button style={s.iconBtn}
            onClick={() => setRightOpen((v) => !v)}>
            {rightOpen
              ? <ChevronRight size={16} />
              : <ShoppingBag size={16} />}
          </button>
          {rightOpen && (
            <>
              <p style={{ fontSize: 12, fontWeight: 600,
                color: 'var(--text2)', display: 'flex',
                alignItems: 'center', gap: 5 }}>
                <ShoppingBag size={13} /> My Orders
              </p>
              <button style={{ ...s.iconBtn, marginLeft: 'auto' }}
                onClick={loadOrders}>
                <RefreshCw size={13} />
              </button>
            </>
          )}
        </div>

        {rightOpen && (
          <div style={{ flex: 1, overflowY: 'auto', padding: '10px 8px' }}>
            {orders.length === 0
              ? <p style={s.empty}>No orders yet</p>
              : orders.map((o) => <OrderCard key={o.id} o={o} />)}
          </div>
        )}
      </aside>
    </div>
  )
}

// ── Styles ────────────────────────────────────────────────────────────────────

const s = {
  shell: {
    display: 'flex', height: '100vh', overflow: 'hidden',
  },
  sideLeft: {
    display: 'flex', flexDirection: 'column',
    background: 'var(--s1)', borderRight: '1px solid var(--border)',
    transition: 'width .2s ease', flexShrink: 0, overflow: 'hidden',
  },
  sideRight: {
    display: 'flex', flexDirection: 'column',
    background: 'var(--s1)', borderLeft: '1px solid var(--border)',
    transition: 'width .2s ease', flexShrink: 0, overflow: 'hidden',
  },
  sideTop: {
    display: 'flex', alignItems: 'center', gap: 6,
    padding: '12px 10px', borderBottom: '1px solid var(--border)',
  },
  sideFooter: {
    display: 'flex', alignItems: 'center', gap: 8,
    padding: 10, borderTop: '1px solid var(--border)',
  },
  newBtn: {
    flex: 1, display: 'flex', alignItems: 'center', gap: 6,
    padding: '7px 12px', background: 'var(--accent)', color: '#fff',
    border: 'none', borderRadius: 'var(--radius)',
    fontSize: 13, fontWeight: 600, fontFamily: 'var(--font)',
    whiteSpace: 'nowrap',
  },
  iconBtn: {
    background: 'none', border: 'none', color: 'var(--text2)',
    display: 'flex', alignItems: 'center', padding: 4,
    borderRadius: 5, flexShrink: 0,
  },
  sessionList: {
    flex: 1, overflowY: 'auto', padding: '8px 6px',
  },
  empty: {
    fontSize: 12, color: 'var(--text3)',
    textAlign: 'center', padding: '16px 8px',
  },
  groupLabel: {
    fontSize: 10, fontWeight: 600, textTransform: 'uppercase',
    letterSpacing: '.07em', color: 'var(--text3)',
    padding: '8px 6px 4px',
  },
  sessionItem: {
    display: 'flex', alignItems: 'center', gap: 6,
    padding: '7px 8px', borderRadius: 7, cursor: 'pointer',
    marginBottom: 1,
  },
  sessionTitle: {
    flex: 1, fontSize: 12.5,
    whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
  },
  delBtn: {
    display: 'none', background: 'none', border: 'none',
    color: 'var(--text3)', padding: 2, borderRadius: 4,
  },
  avatar2: {
    width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
    background: 'rgba(79,124,255,.15)', border: '1px solid var(--accent)',
    color: 'var(--accent)', display: 'flex',
    alignItems: 'center', justifyContent: 'center',
    fontWeight: 700, fontSize: 13,
  },
  chatMain: {
    flex: 1, display: 'flex', flexDirection: 'column',
    minWidth: 0, overflow: 'hidden',
  },
  chatHeader: {
    display: 'flex', alignItems: 'center',
    justifyContent: 'space-between',
    padding: '12px 20px', background: 'var(--s1)',
    borderBottom: '1px solid var(--border)', flexShrink: 0,
  },
  chatIcon: {
    width: 36, height: 36, borderRadius: 9, flexShrink: 0,
    background: 'rgba(79,124,255,.12)', border: '1px solid var(--accent)',
    color: 'var(--accent)', display: 'flex',
    alignItems: 'center', justifyContent: 'center',
  },
  messages: {
    flex: 1, overflowY: 'auto', padding: '20px',
    display: 'flex', flexDirection: 'column', gap: 12,
  },
  emptyState: {
    flex: 1, display: 'flex', flexDirection: 'column',
    alignItems: 'center', justifyContent: 'center',
    gap: 12, color: 'var(--text2)', textAlign: 'center',
  },
  emptyIcon: {
    width: 68, height: 68, borderRadius: '50%',
    background: 'rgba(79,124,255,.08)', border: '1px solid var(--border2)',
    color: 'var(--accent)', display: 'flex',
    alignItems: 'center', justifyContent: 'center',
  },
  row: {
    display: 'flex', alignItems: 'flex-end', gap: 8,
  },
  avatar: {
    width: 26, height: 26, borderRadius: '50%', flexShrink: 0,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
  },
  bubble: {
    maxWidth: '68%', padding: '10px 14px',
    borderRadius: 14, fontSize: 13.5, lineHeight: 1.6,
  },
  ts: {
    fontSize: 10, color: 'var(--text3)',
    marginTop: 5, textAlign: 'right',
  },
  quickBar: {
    display: 'flex', flexWrap: 'wrap', gap: 6,
    padding: '6px 20px 10px',
  },
  quickChip: {
    padding: '5px 12px', background: 'var(--s2)',
    border: '1px solid var(--border2)', borderRadius: 99,
    color: 'var(--text)', fontSize: 12, fontFamily: 'var(--font)',
    textTransform: 'capitalize',
  },
  inputRow: {
    display: 'flex', alignItems: 'flex-end', gap: 8,
    padding: '12px 20px', background: 'var(--s1)',
    borderTop: '1px solid var(--border)', flexShrink: 0,
  },
  chatInput: {
    flex: 1, background: 'var(--s2)',
    border: '1px solid var(--border2)', borderRadius: 'var(--radius)',
    color: 'var(--text)', fontSize: 13.5, fontFamily: 'var(--font)',
    padding: '10px 14px', resize: 'none', maxHeight: 120,
    lineHeight: 1.5,
  },
  sendBtn: {
    width: 40, height: 40, borderRadius: '50%',
    background: 'var(--accent)', border: 'none', color: '#fff',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    flexShrink: 0,
  },
  orderCard: {
    background: 'var(--s2)', border: '1px solid var(--border)',
    borderRadius: 8, padding: '9px 10px', marginBottom: 6,
  },
}