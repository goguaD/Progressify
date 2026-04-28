import { useApp } from '../contexts/AppContext'

export default function Workouts() {
  const { t } = useApp()
  return (
    <div className="main-body">
      <div style={{ textAlign: 'center' }}>
        <h1 className="main-greeting">{t.workouts_title} 🏋️</h1>
        <p className="main-sub" style={{ marginTop: 10 }}>{t.workouts_sub}</p>
      </div>
      <p className="coming-soon-text">{t.coming_soon}</p>
    </div>
  )
}
