import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { AuthProvider, useAuth } from './hooks/useAuth.jsx'
import LoginPage from './components/LoginPage'
import ChatPage  from './components/ChatPage'
import './index.css'

function Guard({ children }) {
  const { user } = useAuth()
  
  // Check localStorage directly as fallback
  const hasToken = localStorage.getItem('token')
  
  if (!user && !hasToken) return <Navigate to="/login" replace />
  return children
}

function GoogleCallback() {
  const navigate            = useNavigate()
  const { loginWithToken }  = useAuth()

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const token  = params.get('token')
    const name   = decodeURIComponent(params.get('name') || '')
    const email  = params.get('email')
    const role   = params.get('role')

    if (token) {
      loginWithToken(token, { name, email, role })
      // Small timeout to let React re-render with the new user state
      setTimeout(() => navigate('/'), 100)
    } else {
      navigate('/login')
    }
  }, []) // eslint-disable-line

  return (
    <div style={{
      display: 'flex', alignItems: 'center',
      justifyContent: 'center', height: '100vh',
      color: 'white', fontSize: 16,
    }}>
      Signing you in...
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login"         element={<LoginPage />} />
          <Route path="/auth/callback" element={<GoogleCallback />} />
          <Route path="/"              element={<Guard><ChatPage /></Guard>} />
          <Route path="*"              element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}