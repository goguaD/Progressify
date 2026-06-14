import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useApp } from '../contexts/AppContext'
import Controls from '../components/Controls'

export default function SignUp() {
  const navigate = useNavigate()
  const { t } = useApp()
  const [step, setStep] = useState(1)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const [form, setForm] = useState({
    username: '',
    firstname: '',
    lastname: '',
    middlename: '',
    email: '',
    password: '',
    confirmPassword: '',
    weight: '',
    height: '',
    age: '',
    goal: '',
    gender: '',
  })

  const USERNAME_RE = /^[a-z0-9_]{3,20}$/

  const GOALS = [
    { value: 'muscle_gain',  label: t.goals.muscle_gain },
    { value: 'weight_loss',  label: t.goals.weight_loss },
    { value: 'maintain',     label: t.goals.maintain },
    { value: 'endurance',    label: t.goals.endurance },
  ]

  function handleChange(e) {
    let value = e.target.value
    if (e.target.name === 'username') value = value.toLowerCase()
    setForm((prev) => ({ ...prev, [e.target.name]: value }))
    setError('')
  }

  function validateStep1() {
    if (!form.firstname.trim()) return t.err_firstname
    if (!form.lastname.trim()) return t.err_lastname
    if (!form.username.trim()) return t.err_username_req
    if (!USERNAME_RE.test(form.username.trim())) return t.err_username_format
    if (!form.email.trim()) return t.err_email_req
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) return t.err_email_invalid
    if (form.password.length < 6) return t.err_password_short
    if (form.password !== form.confirmPassword) return t.err_password_match
    return null
  }

  function validateStep2() {
    if (!form.weight || isNaN(form.weight) || Number(form.weight) <= 0) return t.err_weight
    if (!form.height || isNaN(form.height) || Number(form.height) <= 0) return t.err_height
    const age = Number(form.age)
    if (!form.age || isNaN(age) || age < 13 || age > 100) return t.err_age
    if (!form.gender) return t.err_gender
    if (!form.goal) return t.err_goal
    return null
  }

  function handleNext(e) {
    e.preventDefault()
    const err = validateStep1()
    if (err) { setError(err); return }
    setError('')
    setStep(2)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const err = validateStep2()
    if (err) { setError(err); return }

    setLoading(true)
    try {
      const { data } = await api.post('/auth/register', {
        username: form.username.trim().toLowerCase(),
        firstname: form.firstname.trim(),
        lastname: form.lastname.trim(),
        middlename: form.middlename.trim() || null,
        email: form.email.trim(),
        password: form.password,
        weight: Number(form.weight),
        height: Number(form.height),
        age: Number(form.age),
        goal: form.goal,
        gender: form.gender,
      })
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || t.err_register)
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

        {/* Step indicator */}
        <div className="step-indicator">
          <div className={`step-dot ${step === 1 ? 'active' : 'done'}`}>
            {step === 1 ? '1' : '✓'}
          </div>
          <div className={`step-line ${step === 2 ? 'done' : ''}`} />
          <div className={`step-dot ${step === 2 ? 'active' : 'inactive'}`}>2</div>
        </div>

        {step === 1 && (
          <>
            <h1 className="auth-title">{t.signup_title}</h1>
            <p className="auth-subtitle">{t.signup_step1_sub}</p>

            {error && <div className="msg-error">{error}</div>}

            <form onSubmit={handleNext} noValidate>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="firstname">{t.firstname}</label>
                  <input
                    id="firstname"
                    name="firstname"
                    type="text"
                    placeholder={t.ph_firstname}
                    value={form.firstname}
                    onChange={handleChange}
                    autoFocus
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="lastname">{t.lastname}</label>
                  <input
                    id="lastname"
                    name="lastname"
                    type="text"
                    placeholder={t.ph_lastname}
                    value={form.lastname}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="middlename">
                  {t.middlename} <span className="optional-tag">({t.optional})</span>
                </label>
                <input
                  id="middlename"
                  name="middlename"
                  type="text"
                  placeholder={t.ph_middlename}
                  value={form.middlename}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label htmlFor="username">
                  {t.username}{' '}
                  <span className="optional-tag">{t.username_hint}</span>
                </label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  placeholder={t.ph_username}
                  value={form.username}
                  onChange={handleChange}
                  autoComplete="username"
                  spellCheck={false}
                />
              </div>

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
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">{t.password}</label>
                <div style={{ position: 'relative' }}>
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder={t.ph_password}
                    value={form.password}
                    onChange={handleChange}
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
                    }}
                    tabIndex={-1}
                  >
                    {showPassword ? '🙈' : '👁️'}
                  </button>
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: 24 }}>
                <label htmlFor="confirmPassword">{t.confirm_password}</label>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showPassword ? 'text' : 'password'}
                  placeholder={t.ph_confirm}
                  value={form.confirmPassword}
                  onChange={handleChange}
                />
              </div>

              <button className="btn btn-primary" type="submit">
                {t.next}
              </button>
            </form>
          </>
        )}

        {step === 2 && (
          <>
            <h1 className="auth-title">{t.signup_almost}</h1>
            <p className="auth-subtitle">{t.signup_step2_sub}</p>

            {error && <div className="msg-error">{error}</div>}

            <form onSubmit={handleSubmit} noValidate>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="weight">{t.weight}</label>
                  <div className="input-with-unit">
                    <input
                      id="weight"
                      name="weight"
                      type="number"
                      placeholder="70"
                      min="20"
                      max="300"
                      step="0.1"
                      value={form.weight}
                      onChange={handleChange}
                    />
                    <span className="input-unit">kg</span>
                  </div>
                </div>
                <div className="form-group">
                  <label htmlFor="height">{t.height}</label>
                  <div className="input-with-unit">
                    <input
                      id="height"
                      name="height"
                      type="number"
                      placeholder="175"
                      min="100"
                      max="250"
                      step="0.1"
                      value={form.height}
                      onChange={handleChange}
                    />
                    <span className="input-unit">cm</span>
                  </div>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="age">{t.bmi_age || 'Age'}</label>
                <div className="input-with-unit">
                  <input
                    id="age"
                    name="age"
                    type="number"
                    placeholder="25"
                    min="13"
                    max="100"
                    step="1"
                    value={form.age}
                    onChange={handleChange}
                  />
                  <span className="input-unit">{t.age_unit || 'yrs'}</span>
                </div>
              </div>

              <div className="form-group">
                <label>{t.gender}</label>
                <div className="gender-toggle">
                  <button
                    type="button"
                    className={`gender-option ${form.gender === 'male' ? 'active' : ''}`}
                    onClick={() => { setForm((p) => ({ ...p, gender: 'male' })); setError('') }}
                  >
                    <span className="gender-icon">♂</span>
                    {t.gender_male}
                  </button>
                  <button
                    type="button"
                    className={`gender-option ${form.gender === 'female' ? 'active' : ''}`}
                    onClick={() => { setForm((p) => ({ ...p, gender: 'female' })); setError('') }}
                  >
                    <span className="gender-icon">♀</span>
                    {t.gender_female}
                  </button>
                </div>
              </div>

              <div className="form-group" style={{ marginBottom: 24 }}>
                <label htmlFor="goal">{t.goal_label}</label>
                <select
                  id="goal"
                  name="goal"
                  value={form.goal}
                  onChange={handleChange}
                >
                  <option value="" disabled>{t.goal_ph}</option>
                  {GOALS.map((g) => (
                    <option key={g.value} value={g.value}>{g.label}</option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'flex', gap: 10 }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => { setStep(1); setError('') }}
                  style={{ width: 'auto', padding: '12px 20px', flexShrink: 0 }}
                >
                  {t.back}
                </button>
                <button className="btn btn-primary" type="submit" disabled={loading}>
                  {loading ? t.creating : t.done}
                </button>
              </div>
            </form>
          </>
        )}

        <div className="auth-footer">
          {t.already_have} <Link to="/login">{t.sign_in}</Link>
        </div>
      </div>
    </div>
  )
}
