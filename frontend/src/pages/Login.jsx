import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useApp } from '../contexts/AppContext'
import Controls from '../components/Controls'

export default function Login() {
  const navigate = useNavigate()
  const { t } = useApp()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
    setError('')
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.email || !form.password) {
      setError(t.login_err_fill)
      return
    }
    setLoading(true)
    try {
      const { data } = await api.post('/auth/login', {
        email: form.email,
        password: form.password,
      })
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || t.login_err_generic)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-wrapper">
      <Controls />

      <div className="auth-card">
        <div className="brand">
          <div className="brand-icon">💪</div>
          <div className="brand-name">
            Pro<span>gressify</span>
          </div>
        </div>

        <h1 className="auth-title">{t.login_title}</h1>
        <p className="auth-subtitle">{t.login_subtitle}</p>

        {error && <div className="msg-error">{error}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label htmlFor="email">{t.email}</label>
            <input
              id="email"
              name="email"
              type="email"
              placeholder={t.login_ph_email}
              value={form.email}
              onChange={handleChange}
              autoComplete="email"
              autoFocus
            />
          </div>

          <div className="form-group" style={{ marginBottom: 24 }}>
            <label htmlFor="password">{t.password}</label>
            <div style={{ position: 'relative' }}>
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                placeholder={t.login_ph_password}
                value={form.password}
                onChange={handleChange}
                autoComplete="current-password"
                style={{ paddingRight: 48 }}
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                style={{
                  position: 'absolute',
                  right: 12,
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: 'var(--text-subtle)',
                  fontSize: 16,
                  padding: 0,
                  lineHeight: 1,
                }}
                tabIndex={-1}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? t.login_loading : t.sign_in}
          </button>
        </form>

        <div className="auth-footer">
          {t.login_no_account} <Link to="/signup">{t.login_create}</Link>
        </div>
      </div>
    </div>
  )
}
