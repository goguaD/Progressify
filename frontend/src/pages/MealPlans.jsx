import { useState, useEffect, useMemo, useRef, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useApp } from '../contexts/AppContext'
import api from '../api/client'
import MealCard from '../components/meals/MealCard'
import MealDetail from '../components/meals/MealDetail'
import AddMealModal from '../components/meals/AddMealModal'

const GOAL_FILTERS = ['all', 'cut', 'bulk', 'maintain', 'cheat']
const SORT_OPTIONS = [
  { value: 'recommended', label: 'Recommended' },
  { value: 'newest', label: 'Newest' },
  { value: 'oldest', label: 'Oldest' },
  { value: 'rating', label: 'Top Rated' },
  { value: 'views', label: 'Most Viewed' },
]

function recScore(m) {
  return m.rating * m.views
}

const PAGE_SIZE = 6

export default function MealPlans() {
  const { t, lang } = useApp()
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  const [searchParams] = useSearchParams()
  const [meals, setMeals] = useState([])
  const [loading, setLoading] = useState(true)
  const [goalFilter, setGoalFilter] = useState('all')
  const [sort, setSort] = useState('recommended')
  const [selectedMeal, setSelectedMeal] = useState(null)
  const [showAddModal, setShowAddModal] = useState(false)

  const userGoal = useMemo(() => {
    if (!user?.goal) return null
    const g = user.goal.toLowerCase()
    if (g.includes('muscle') || g.includes('bulk') || g.includes('gain')) return 'bulk'
    if (g.includes('loss') || g.includes('cut') || g.includes('fat')) return 'cut'
    if (g.includes('maintain')) return 'maintain'
    return null
  }, [user])

  const loadMeals = useCallback(() => {
    setLoading(true)
    const params = { limit: 100 }
    if (goalFilter !== 'all') params.goal = goalFilter
    return api.get('/meals', { params })
      .then(r => setMeals(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [goalFilter])

  // Always fetch ALL meals (no server-side sort/filter for sections to work)
  useEffect(() => { loadMeals() }, [loadMeals])

  // Auto-open a meal when ?open=<id> is in the URL
  useEffect(() => {
    const openId = searchParams.get('open')
    if (!openId || meals.length === 0) return
    const target = meals.find((m) => m.id === parseInt(openId, 10))
    if (target) handleView(target)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [meals, searchParams])

  // Whether we're on the default "recommended" view with no goal filter
  const isDefaultView = sort === 'recommended' && goalFilter === 'all'

  // Featured section when a non-default sort is selected
  const featuredMeals = useMemo(() => {
    if (sort === 'recommended') return null
    const sorted = [...meals]
    if (sort === 'rating') {
      sorted.sort((a, b) => b.rating - a.rating || b.rating_count - a.rating_count)
    } else if (sort === 'views') {
      sorted.sort((a, b) => b.views - a.views)
    } else if (sort === 'newest') {
      sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    } else if (sort === 'oldest') {
      sorted.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
    }
    return sorted
  }, [meals, sort])

  const featuredTitle = useMemo(() => {
    if (sort === 'rating') return t.meals_best_rated || 'Best Rated'
    if (sort === 'views') return t.meals_most_viewed || 'Most Viewed'
    if (sort === 'newest') return t.meals_sort_newest || 'Newest'
    if (sort === 'oldest') return t.meals_sort_oldest || 'Oldest'
    return null
  }, [sort, t])

  const featuredSub = useMemo(() => {
    if (sort === 'rating') return t.meals_best_rated_sub || 'Highest-rated meals by our users'
    if (sort === 'views') return t.meals_most_viewed_sub || 'Popular meals the community loves'
    return ''
  }, [sort, t])

  // Recommended carousel — user's goal first only when no goal filter is active
  const recommendedMeals = useMemo(() => {
    if (sort !== 'recommended') return []
    return [...meals].sort((a, b) => {
      if (goalFilter === 'all' && userGoal) {
        const aMatch = a.goal === userGoal ? 0 : 1
        const bMatch = b.goal === userGoal ? 0 : 1
        if (aMatch !== bMatch) return aMatch - bMatch
      }
      return recScore(b) - recScore(a)
    })
  }, [meals, sort, goalFilter, userGoal])

  // Sections for "recommended" default view
  const forYou = useMemo(() => {
    if (!userGoal || !isDefaultView) return []
    return meals.filter(m => m.goal === userGoal)
  }, [meals, userGoal, isDefaultView])

  const mostViewed = useMemo(() => {
    if (!isDefaultView) return []
    return [...meals].sort((a, b) => b.views - a.views).filter(m => m.views > 0)
  }, [meals, isDefaultView])

  const bestRated = useMemo(() => {
    if (!isDefaultView) return []
    return [...meals].sort((a, b) => b.rating - a.rating || b.rating_count - a.rating_count)
      .filter(m => m.rating_count > 0)
  }, [meals, isDefaultView])

  const cheatMeals = useMemo(() => {
    if (!isDefaultView) return []
    return meals.filter(m => m.goal === 'cheat')
  }, [meals, isDefaultView])

  // "All Meals" — always uses recommended score (rating × views), with user's goal boosted
  const allMealsSorted = useMemo(() => {
    const copy = [...meals]
    copy.sort((a, b) => {
      if (userGoal) {
        const aMatch = a.goal === userGoal ? 0 : 1
        const bMatch = b.goal === userGoal ? 0 : 1
        if (aMatch !== bMatch) return aMatch - bMatch
      }
      return recScore(b) - recScore(a)
    })
    return copy
  }, [meals, userGoal])

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

  const handleMealAdded = () => {
    if (goalFilter !== 'all') {
      setGoalFilter('all')
    } else {
      loadMeals()
    }
  }

  return (
    <div className="meals-page">
      <div className="meals-top">
        <div>
          <h1 className="meals-title">{t.mealplans_title}</h1>
          <p className="meals-subtitle">{t.meals_sub || 'Proven meals tailored to your fitness goals.'}</p>
        </div>
        <button
          className="btn btn-primary btn-tiny meals-add-btn"
          onClick={() => setShowAddModal(true)}
        >
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
          {/* Featured section when a non-default sort is selected */}
          {featuredMeals && (
            <MealCarousel
              title={featuredTitle}
              sub={featuredSub}
              meals={featuredMeals}
              t={t} onRate={handleRate} onView={handleView} appLang={lang}
            />
          )}

          {/* Recommended carousel — shows whenever sort is "recommended", any goal filter */}
          {recommendedMeals.length > 0 && (
            <MealCarousel
              title={t.meals_sort_recommended || 'Recommended'}
              sub={t.meals_recommended_sub || 'Best combination of rating and popularity'}
              meals={recommendedMeals}
              t={t} onRate={handleRate} onView={handleView} appLang={lang}
            />
          )}

          {/* Extra sections only on default view (recommended + all goals) */}
          {isDefaultView && (
            <>
              {forYou.length > 0 && (
                <MealCarousel
                  title={t.meals_for_you || 'Meals for you'}
                  sub={t.meals_for_you_sub || 'Based on your current goal'}
                  meals={forYou}
                  t={t} onRate={handleRate} onView={handleView} appLang={lang}
                />
              )}
              {mostViewed.length > 0 && (
                <MealCarousel
                  title={t.meals_most_viewed || 'Most Viewed'}
                  sub={t.meals_most_viewed_sub || 'Popular meals the community loves'}
                  meals={mostViewed}
                  t={t} onRate={handleRate} onView={handleView} appLang={lang}
                />
              )}
              {bestRated.length > 0 && (
                <MealCarousel
                  title={t.meals_best_rated || 'Best Rated'}
                  sub={t.meals_best_rated_sub || 'Highest-rated meals by our users'}
                  meals={bestRated}
                  t={t} onRate={handleRate} onView={handleView} appLang={lang}
                />
              )}
              {cheatMeals.length > 0 && (
                <MealCarousel
                  title={t.meals_cheat_section || 'Healthy Cheat Meals'}
                  sub={t.meals_cheat_section_sub || 'Satisfy cravings without derailing your goals'}
                  meals={cheatMeals}
                  t={t} onRate={handleRate} onView={handleView} appLang={lang}
                />
              )}
            </>
          )}

          {/* All Meals — always present, recommended order */}
          <section className="meals-section">
            <h2 className="meals-section-title">{t.meals_all || 'All Meals'}</h2>
            {allMealsSorted.length === 0 ? (
              <div className="empty-card">{t.meals_empty || 'No meals found.'}</div>
            ) : (
              <div className="meals-grid">
                {allMealsSorted.map(m => (
                  <MealCard key={m.id} meal={m} t={t} onRate={handleRate} onView={handleView} appLang={lang} />
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
          currentUser={user}
          onDeleted={(id) => setMeals((prev) => prev.filter((m) => m.id !== id))}
        />
      )}

      {showAddModal && (
        <AddMealModal
          t={t}
          appLang={lang}
          onClose={() => setShowAddModal(false)}
          onAdded={handleMealAdded}
        />
      )}
    </div>
  )
}


function MealCarousel({ title, sub, meals, t, onRate, onView, appLang }) {
  const [page, setPage] = useState(0)
  const trackRef = useRef(null)
  const totalPages = Math.ceil(meals.length / PAGE_SIZE)
  const canPrev = page > 0
  const canNext = page < totalPages - 1

  const visibleMeals = meals.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  return (
    <section className="meals-section">
      <div className="meals-carousel-header">
        <div>
          <h2 className="meals-section-title">{title}</h2>
          {sub && <p className="meals-section-sub">{sub}</p>}
        </div>
        {totalPages > 1 && (
          <div className="meals-carousel-nav">
            <span className="meals-carousel-counter">
              {page + 1} / {totalPages}
            </span>
            <button
              className={`meals-carousel-arrow${!canPrev ? ' disabled' : ''}`}
              onClick={() => canPrev && setPage(p => p - 1)}
              aria-label="Previous"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
            </button>
            <button
              className={`meals-carousel-arrow${!canNext ? ' disabled' : ''}`}
              onClick={() => canNext && setPage(p => p + 1)}
              aria-label="Next"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </button>
          </div>
        )}
      </div>

      <div className="meals-carousel-viewport">
        <div
          className="meals-carousel-track"
          ref={trackRef}
          style={{ transform: `translateX(-${page * 100}%)` }}
        >
          {Array.from({ length: totalPages }).map((_, pi) => {
            const items = meals.slice(pi * PAGE_SIZE, (pi + 1) * PAGE_SIZE)
            const cols = Math.min(items.length, 3)
            return (
              <div className="meals-carousel-page" key={pi} style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
                {items.map(m => (
                  <MealCard key={m.id} meal={m} t={t} onRate={onRate} onView={onView} appLang={appLang} />
                ))}
              </div>
            )
          })}
        </div>
      </div>

      {totalPages > 1 && (
        <div className="meals-carousel-dots">
          {Array.from({ length: totalPages }).map((_, i) => (
            <button
              key={i}
              className={`meals-carousel-dot${i === page ? ' active' : ''}`}
              onClick={() => setPage(i)}
            />
          ))}
        </div>
      )}
    </section>
  )
}
