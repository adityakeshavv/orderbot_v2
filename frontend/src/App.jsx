import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { AuthProvider, useAuth } from './hooks/useAuth.jsx'
import LoginPage from './components/LoginPage'
import ChatPage  from './components/ChatPage'
import './index.css'

function Guard({ children }) {
  const { user } = useAuth()
  return user ? children : <Navigate to="/login" replace />
}

function GoogleCallback() {
  const navigate          = useNavigate()
  const { loginWithToken } = useAuth()

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const token  = params.get('token')
    const name   = params.get('name')
    const email  = params.get('email')
    const role   = params.get('role')
    if (token) {
      loginWithToken(token, { name, email, role })
      navigate('/')
    } else {
      navigate('/login')
    }
  }, []) // eslint-disable-line

  return (
    <p style={{ color: 'white', padding: 20 }}>Signing you in...</p>
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