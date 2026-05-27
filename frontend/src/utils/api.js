import axios from 'axios'

const http = axios.create({ baseURL: '' })

http.interceptors.request.use((cfg) => {
  const t = localStorage.getItem('token')
  if (t) cfg.headers.Authorization = `Bearer ${t}`
  return cfg
})

http.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.clear()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const authAPI = {
  register: (d) => http.post('/auth/register', d),
  login:    (d) => http.post('/auth/login', d),
  me:       ()  => http.get('/auth/me'),
}

export const sessionsAPI = {
  create: ()          => http.post('/sessions'),
  list:   ()          => http.get('/sessions'),
  get:    (id)        => http.get(`/sessions/${id}`),
  delete: (id)        => http.delete(`/sessions/${id}`),
  rename: (id, title) => http.patch(`/sessions/${id}`, { title }),
}

export const ordersAPI = {
  list: () => http.get('/orders'),
}

export function streamChat(sessionId, message, { onToken, onDone, onError }) {
  const controller = new AbortController()
  const token      = localStorage.getItem('token')

  fetch('/chat', {
    method:  'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body:   JSON.stringify({ session_id: sessionId, message }),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        onError(err.detail || 'Request failed')
        return
      }
      const reader  = res.body.getReader()
      const decoder = new TextDecoder()
      let   buffer  = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop()
        let event = null
        for (const line of lines) {
          if (line.startsWith('event: '))      event = line.slice(7).trim()
          else if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (event === 'token') onToken(data.token)
              else if (event === 'done')  onDone(data)
              else if (event === 'error') onError(data.detail)
            } catch { /* bad frame */ }
            event = null
          }
        }
      }
    })
    .catch((e) => {
      if (e.name !== 'AbortError') onError(e.message || 'Connection lost')
    })

  return controller
}

export default http