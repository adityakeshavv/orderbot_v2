import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Package, Loader } from 'lucide-react'

export default function LoginPage() {
  const [mode,    setMode]    = useState('login')
  const [form,    setForm]    = useState({ name: '', email: '', password: '' })
  const [error,   setError]   = useState('')
  const [loading, setLoading] = useState(false)
  const { login, register }   = useAuth()
  const navigate              = useNavigate()

  const set = (f) => (e) =>
    setForm((p) => ({ ...p, [f]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (mode === 'login')
        await login(form.email, form.password)
      else
        await register(form.name, form.email, form.password)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>

        {/* Logo */}
        <div style={styles.logo}>
          <div style={styles.logoIcon}><Package size={28} /></div>
          <h1 style={styles.logoTitle}>OrderBot</h1>
          <p style={styles.logoSub}>Tata Steel · Supply Chain Assistant</p>
        </div>

        {/* Tabs */}
        <div style={styles.tabs}>
          <button
            style={{ ...styles.tab, ...(mode === 'login' ? styles.tabActive : {}) }}
            onClick={() => { setMode('login'); setError('') }}
          >Sign In</button>
          
          <button
            style={{ ...styles.tab, ...(mode === 'register' ? styles.tabActive : {}) }}
            onClick={() => { setMode('register'); setError('') }}
          >Register</button>

          <button
            style={{
            ...styles.btn,
            background: '#fff',
            color: '#333',
            border: '1px solid var(--border)',
            marginTop: 8,
            }}
            type="button"
            onClick={() => window.location.href = 'http://localhost:8000/auth/google'}
            >
            <img
              src="https://www.google.com/favicon.ico"
              width={16} height={16}
              alt="Google"
            />
            Continue with Google
          </button>
        </div>

        {/* Form */}
        <form onSubmit={submit}>
          {mode === 'register' && (
            <input
              style={styles.input}
              placeholder="Full name"
              value={form.name}
              onChange={set('name')}
              required
            />
          )}
          <input
            style={styles.input}
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={set('email')}
            required
          />
          <input
            style={styles.input}
            type="password"
            placeholder={mode === 'register'
              ? 'Password (min 8 chars)' : 'Password'}
            value={form.password}
            onChange={set('password')}
            required
          />

          {error && <p style={styles.error}>{error}</p>}

          <button style={styles.btn} type="submit" disabled={loading}>
            {loading
              ? <Loader size={16} style={styles.spin} />
              : mode === 'login' ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <p style={styles.hint}>
          Demo: <code style={styles.code}>rajesh@tatasteel.in</code>{' '}
          / <code style={styles.code}>Test1234</code>
        </p>
      </div>
    </div>
  )
}

const styles = {
  page: {
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    minHeight: '100vh',
    background: 'radial-gradient(ellipse at 50% 20%, rgba(79,124,255,.1) 0%, transparent 60%), var(--bg)',
  },
  card: {
    width: 380, background: 'var(--s1)',
    border: '1px solid var(--border)', borderRadius: 'var(--radius)',
    padding: '36px 32px', boxShadow: '0 8px 40px rgba(0,0,0,.5)',
  },
  logo:      { textAlign: 'center', marginBottom: 24 },
  logoIcon:  {
    display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
    width: 52, height: 52,
    background: 'rgba(79,124,255,.1)', border: '1px solid var(--accent)',
    borderRadius: 13, color: 'var(--accent)', marginBottom: 10,
  },
  logoTitle: { fontSize: 22, fontWeight: 700 },
  logoSub:   { fontSize: 12, color: 'var(--text2)', marginTop: 3 },
  tabs: {
    display: 'flex', background: 'var(--bg)',
    borderRadius: 8, padding: 3, marginBottom: 20,
  },
  tab: {
    flex: 1, padding: '7px', border: 'none',
    background: 'transparent', color: 'var(--text2)',
    borderRadius: 6, fontSize: 13, fontWeight: 500,
    fontFamily: 'var(--font)', transition: 'all .15s',
  },
  tabActive: { background: 'var(--accent)', color: '#fff' },
  input: {
    display: 'block', width: '100%',
    background: 'var(--bg)', border: '1px solid var(--border)',
    borderRadius: 8, color: 'var(--text)',
    fontSize: 13.5, fontFamily: 'var(--font)',
    padding: '10px 14px', outline: 'none', marginBottom: 10,
  },
  error: {
    fontSize: 12, color: 'var(--red)',
    background: 'rgba(239,68,68,.08)',
    border: '1px solid rgba(239,68,68,.25)',
    borderRadius: 7, padding: '8px 12px', marginBottom: 10,
  },
  btn: {
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    gap: 6, width: '100%', padding: 10,
    background: 'var(--accent)', color: '#fff', border: 'none',
    borderRadius: 8, fontSize: 14, fontWeight: 600,
    fontFamily: 'var(--font)', transition: 'background .15s',
  },
  hint: {
    fontSize: 11.5, color: 'var(--text2)',
    textAlign: 'center', marginTop: 16,
  },
  code: {
    background: 'var(--bg)', padding: '2px 5px', borderRadius: 4,
    fontSize: 11, fontFamily: 'monospace',
  },
  spin: { animation: 'spin .7s linear infinite' },
}