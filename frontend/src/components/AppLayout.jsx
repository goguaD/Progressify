import { useEffect, useState } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import api from '../api/client'
import Header from './Header'

const HEARTBEAT_MS = 30_000

export default function AppLayout() {
  const navigate = useNavigate()
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('user')
    return stored ? JSON.parse(stored) : null
  })

  useEffect(() => {
    let cancelled = false

    async function ping() {
      try {
        const { data } = await api.get('/me')
        if (cancelled) return
        setUser(data)
        localStorage.setItem('user', JSON.stringify(data))
      } catch (err) {
        if (err?.response?.status === 401) {
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          navigate('/login', { replace: true })
        }
      }
    }

    ping()
    const id = setInterval(ping, HEARTBEAT_MS)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [navigate])

  async function handleLogout() {
    try {
      await api.post('/auth/logout')
    } catch {
      // even if the call fails, fall through and clear locally
    }
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    navigate('/login', { replace: true })
  }

  if (!user) return null

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', transition: 'background 0.25s' }}>
      <Header user={user} onLogout={handleLogout} />
      <Outlet context={{ user, setUser }} />
    </div>
  )
}
