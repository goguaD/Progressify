import { useState, useEffect, useMemo } from 'react'
import { useApp } from '../contexts/AppContext'
import api from '../api/client'
import MealCard from '../components/meals/MealCard'
import MealDetail from '../components/meals/MealDetail'

const GOAL_FILTERS = ['all', 'cut', 'bulk', 'maintain']
const SORT_OPTIONS = [
  { value: 'newest', label: 'Newest' },
  { value: 'oldest', label: 'Oldest' },
  { value: 'rating', label: 'Top Rated' },
  { value: 'views', label: 'Most Viewed' },
]

export default function MealPlans() {
  const { t, lang } = useApp()
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  const [meals, setMeals] = useState([])
  const [loading, setLoading] = useState(true)
  const [goalFilter, setGoalFilter] = useState('all')
  const [sort, setSort] = useState('newest')
  const [selectedMeal, setSelectedMeal] = useState(null)

  const userGoal = useMemo(() => {
    if (!user?.goal) return null
    const g = user.goal.toLowerCase()
    if (g.includes('muscle') || g.includes('bulk') || g.includes('gain')) return 'bulk'
    if (g.includes('loss') || g.includes('cut') || g.includes('fat')) return 'cut'
    if (g.includes('maintain')) return 'maintain'
    return null
  }, [user])

  useEffect(() => {
    setLoading(true)
    const params = { sort }
    if (goalFilter !== 'all') params.goal = goalFilter
    api.get('/meals', { params })
      .then(r => setMeals(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [goalFilter, sort])

  const recommended = useMemo(() => {
    if (!userGoal || goalFilter !== 'all') return []
    return meals.filter(m => m.goal === userGoal)
  }, [meals, userGoal, goalFilter])

  const otherMeals = useMemo(() => {
    if (!userGoal || goalFilter !== 'all') return meals
    return meals.filter(m => m.goal !== userGoal)
  }, [meals, userGoal, goalFilter])

  const handleRate = async (mealId, score) => {
    try {
      const r = await api.post(`/meals/${mealId}/rate`, { score })
      setMeals(prev => prev.map(m => m.id === mealId ? r.data : m))
      if (selectedMeal?.id === mealId) setSelectedMeal(r.data)
    } catch { /* ignore */ }
  }

  const handleView = async (meal) => {
    try {
      const r = await api.post(`/meals/${meal.id}/view`)
      setMeals(prev => prev.map(m => m.id === meal.id ? r.data : m))
      setSelectedMeal(r.data)
    } catch {
      setSelectedMeal(meal)
    }
  }

  return (
    <div className="meals-page">
      <div className="meals-top">
        <div>
          <h1 className="meals-title">{t.mealplans_title}</h1>
          <p className="meals-subtitle">{t.meals_sub || 'Proven meals tailored to your fitness goals.'}</p>
        </div>
        <button className="btn btn-primary btn-tiny meals-add-btn" disabled>
          + {t.meals_add || 'Add Meal'}
        </button>
      </div>

      <div className="meals-toolbar">
        <div className="filter-tabs">
          {GOAL_FILTERS.map(g => (
            <button
              key={g}
              className={`filter-tab${goalFilter === g ? ' active' : ''}`}
              onClick={() => setGoalFilter(g)}
            >
              {t[`meals_goal_${g}`] || g.charAt(0).toUpperCase() + g.slice(1)}
            </button>
          ))}
        </div>
        <select
          className="meals-sort-select"
          value={sort}
          onChange={e => setSort(e.target.value)}
        >
          {SORT_OPTIONS.map(o => (
            <option key={o.value} value={o.value}>
              {t[`meals_sort_${o.value}`] || o.label}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="meals-loading">{t.admin_loading || 'Loading…'}</div>
      ) : (
        <>
          {recommended.length > 0 && (
            <section className="meals-section">
              <h2 className="meals-section-title">
                {t.meals_for_you || 'Meals for you'}
              </h2>
              <p className="meals-section-sub">
                {t.meals_for_you_sub || 'Based on your current goal'}
              </p>
              <div className="meals-grid">
                {recommended.map(m => (
                  <MealCard key={m.id} meal={m} t={t} onRate={handleRate} onView={handleView} />
                ))}
              </div>
            </section>
          )}

          <section className="meals-section">
            {recommended.length > 0 && (
              <h2 className="meals-section-title">
                {t.meals_all || 'All Meals'}
              </h2>
            )}
            {otherMeals.length === 0 && !recommended.length ? (
              <div className="empty-card">{t.meals_empty || 'No meals found.'}</div>
            ) : (
              <div className="meals-grid">
                {otherMeals.map(m => (
                  <MealCard key={m.id} meal={m} t={t} onRate={handleRate} onView={handleView} />
                ))}
              </div>
            )}
          </section>
        </>
      )}

      {selectedMeal && (
        <MealDetail
          meal={selectedMeal}
          t={t}
          onClose={() => setSelectedMeal(null)}
          onRate={handleRate}
          appLang={lang}
        />
      )}
    </div>
  )
}
