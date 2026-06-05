import axios from 'axios'

export const API_BASE = 'http://localhost:8000'

export function resolveAssetUrl(relativeOrAbsolute) {
  if (!relativeOrAbsolute) return null
  if (/^https?:\/\//i.test(relativeOrAbsolute)) return relativeOrAbsolute
  return `${API_BASE}${relativeOrAbsolute}`
}

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  // Let the browser set multipart boundary — a bare "multipart/form-data"
  // header without boundary breaks file uploads (meals, workouts, avatars).
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  return config
})

api.interceptors.response.use(
  (resp) => resp,
  (err) => {
    if (err?.response?.status === 401) {
      const onAuthPage = ['/login', '/signup'].includes(window.location.pathname)
      if (!onAuthPage) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export default api
