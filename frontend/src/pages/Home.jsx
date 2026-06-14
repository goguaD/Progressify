import { useState, useEffect, useCallback } from 'react'
import { useOutletContext, useNavigate, Link } from 'react-router-dom'
import api, { resolveAssetUrl } from '../api/client'
import { useApp } from '../contexts/AppContext'
import BodyFigure, { LEVEL_COLORS } from '../components/BodyFigure'

// ── Utilities ─────────────────────────────────────────────────────────────────

function timeAgo(isoString, t) {
  if (!isoString) return ''
  const diffMs = Date.now() - new Date(isoString).getTime()
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 2) return t.feed_just_now
  if (diffMin < 60) return `${diffMin}${t.feed_ago_min}`
  const diffH = Math.floor(diffMin / 60)
  if (diffH < 24) return `${diffH}${t.feed_ago_hour}`
  return `${Math.floor(diffH / 24)}${t.feed_ago_day}`
}

function UserAvatar({ user, size = 40, onClick }) {
  const initials = ((user?.firstname?.[0] || '') + (user?.lastname?.[0] || '')).toUpperCase() || '?'
  const src = resolveAssetUrl(user?.avatar_url)
  return (
    <div
      className="feed-avatar"
      style={{ width: size, height: size, fontSize: size * 0.38, cursor: onClick ? 'pointer' : 'default' }}
      onClick={onClick}
    >
      {src ? <img src={src} alt="" className="feed-avatar-img" /> : <span>{initials}</span>}
    </div>
  )
}

function FeedCard({ icon, label, timestamp, accent, children }) {
  return (
    <article className="feed-card" style={accent ? { '--card-accent': accent } : {}}>
      <div className="feed-card-topbar">
        <span className="feed-card-type-icon">{icon}</span>
        <span className="feed-card-type-label">{label}</span>
        <span className="feed-card-time">{timestamp}</span>
      </div>
      <div className="feed-card-body">{children}</div>
    </article>
  )
}

// ── Card Components ────────────────────────────────────────────────────────────

function NewMealCard({ item, t, lang, navigate }) {
  const meal = item.meal
  const name = (lang === 'ka' && meal.name_ka) ? meal.name_ka : meal.name
  const imgSrc = resolveAssetUrl(meal.image_url)
  return (
    <FeedCard icon="🥗" label={t.feed_new_meal} timestamp={timeAgo(item.timestamp, t)} accent="var(--green)">
      <button className="feed-media-btn" onClick={() => navigate(`/mealplans?open=${meal.id}`)}>
        <div className="feed-square-img-wrap">
          {imgSrc
            ? <img src={imgSrc} alt={name} className="feed-square-img" />
            : <div className="feed-square-placeholder">🥗</div>}
          <div className="feed-img-overlay">
            <span className="feed-img-overlay-arrow">→</span>
          </div>
        </div>
        <div className="feed-card-info">
          <h3 className="feed-card-title">{name}</h3>
          <div className="feed-card-tags">
            <span className="feed-tag feed-tag-green">{meal.calories} kcal</span>
            <span className="feed-tag">{meal.goal}</span>
            {meal.protein > 0 && <span className="feed-tag">🥩 {meal.protein}g protein</span>}
            {meal.carbs > 0 && <span className="feed-tag">🌾 {meal.carbs}g carbs</span>}
            {meal.fats > 0 && <span className="feed-tag">🥑 {meal.fats}g fat</span>}
            {meal.rating > 0 && <span className="feed-tag">⭐ {meal.rating.toFixed(1)}</span>}
          </div>
        </div>
      </button>
    </FeedCard>
  )
}

function NewWorkoutCard({ item, t, lang, navigate }) {
  const plan = item.workout
  const name = (lang === 'ka' && plan.name_ka) ? plan.name_ka : plan.name
  const desc = (lang === 'ka' && plan.description_ka) ? plan.description_ka : plan.description
  const imgSrc = resolveAssetUrl(plan.image_url)
  return (
    <FeedCard icon="🏋️" label={t.feed_new_workout} timestamp={timeAgo(item.timestamp, t)} accent="var(--accent)">
      <button className="feed-media-btn" onClick={() => navigate(`/workouts?open=${plan.id}`)}>
        <div className="feed-square-img-wrap">
          {imgSrc
            ? <img src={imgSrc} alt={name} className="feed-square-img" />
            : <div className="feed-square-placeholder">🏋️</div>}
          <div className="feed-img-overlay">
            <span className="feed-img-overlay-arrow">→</span>
          </div>
        </div>
        <div className="feed-card-info">
          <h3 className="feed-card-title">{name}</h3>
          {desc && <p className="feed-card-desc">{desc}</p>}
          <div className="feed-card-tags">
            <span className="feed-tag feed-tag-accent">{plan.days_per_week}×/wk</span>
            <span className="feed-tag">{t[`workouts_level_${plan.level}`] || plan.level}</span>
            {plan.split_type && <span className="feed-tag">{plan.split_type.replace(/_/g,' ')}</span>}
            {plan.rating > 0 && <span className="feed-tag">⭐ {plan.rating.toFixed(1)}</span>}
          </div>
        </div>
      </button>
    </FeedCard>
  )
}

function FriendPRCard({ item, t, navigate }) {
  const levelColor = item.level ? LEVEL_COLORS[item.level] : 'var(--text-muted)'
  const user = item.user
  const backMuscles = ['trapezius','upper-back','lower-back','triceps','hamstring','calves','gluteal']
  const view = item.muscle_group && backMuscles.includes(item.muscle_group) ? 'back' : 'front'

  return (
    <FeedCard icon="💪" label={t.feed_friend_pr} timestamp={timeAgo(item.timestamp, t)} accent={levelColor}>
      <div className="feed-pr-card-layout">
        {/* Left: user info + lift stats */}
        <div className="feed-pr-left">
          <button className="feed-user-row" onClick={() => navigate(`/u/${user.username}`)}>
            <UserAvatar user={user} size={52} />
            <div className="feed-user-info">
              <span className="feed-user-name">{user.firstname} {user.lastname}</span>
              <span className="feed-user-handle">@{user.username}</span>
            </div>
          </button>

          <p className="feed-pr-headline">
            {t.feed_set_pr}
          </p>

          <div className="feed-pr-lift-block">
            <div className="feed-pr-exercise-name">{item.exercise_name}</div>
            <div className="feed-pr-weight-big">{item.weight_kg} <span>kg</span></div>
            {item.level && (
              <span className="feed-pr-level-pill" style={{ background: levelColor }}>
                {t[`level_${item.level}`] || item.level}
              </span>
            )}
          </div>
        </div>

        {/* Right: muscle map */}
        {item.muscle_group && (
          <div className="feed-pr-muscle-map">
            <BodyFigure
              gender={user.gender}
              view={view}
              muscles={{ [item.muscle_group]: item.level || 'beginner' }}
            />
          </div>
        )}
      </div>
    </FeedCard>
  )
}

function FriendChallengeCard({ item, t, navigate }) {
  const isCompleted = item.status === 'completed'
  const statusColor = isCompleted ? '#22c55e' : 'var(--accent)'
  const typeLabel = t[`ch_type_${item.challenge_type}`] || item.challenge_type

  function typeDetail() {
    const parts = []
    if (item.challenge_type === 'strength' && item.muscle_group) {
      parts.push(t[`muscle_${item.muscle_group.replace('-', '_')}`] || item.muscle_group)
    }
    if (item.challenge_type === 'endurance') {
      if (item.endurance_mode) parts.push(t[`ch_mode_${item.endurance_mode}`] || item.endurance_mode)
      if (item.endurance_speed) parts.push(`${item.endurance_speed} km/h`)
      if (item.endurance_gradient) parts.push(`${item.endurance_gradient}% incline`)
    }
    if (item.challenge_type === 'target_weight' && item.target_weight_kg) {
      parts.push(`${t.ch_goal || 'Target'}: ${item.target_weight_kg} kg`)
    }
    return parts.join(' · ')
  }

  function formatResult(val, type) {
    if (val == null) return '—'
    if (type === 'endurance') {
      const mins = Math.floor(val / 60)
      const secs = Math.round(val % 60)
      return `${mins}m ${secs}s`
    }
    return `${val} kg`
  }

  const detail = typeDetail()
  const challResult = formatResult(item.challenger_result, item.challenge_type)
  const oppResult = formatResult(item.opponent_result, item.challenge_type)
  const challerWon = item.winner?.username === item.challenger?.username
  const opponentWon = item.winner?.username === item.opponent?.username

  return (
    <FeedCard
      icon={isCompleted ? '🏆' : '⚔️'}
      label={isCompleted ? t.feed_challenge_ended : t.feed_challenge_started}
      timestamp={timeAgo(item.timestamp, t)}
      accent={statusColor}
    >
      <div className="feed-challenge-layout">
        {/* H2H matchup */}
        <div className="feed-challenge-h2h">
          <button className="feed-challenge-fighter" onClick={() => navigate(`/u/${item.challenger.username}`)}>
            <UserAvatar user={item.challenger} size={56} />
            <span className="feed-challenge-fighter-name">{item.challenger.firstname}</span>
            <span className="feed-challenge-fighter-handle">@{item.challenger.username}</span>
            {isCompleted && (
              <span className="feed-challenge-result-val" style={{ color: challerWon ? '#22c55e' : 'var(--text-muted)' }}>
                {challResult}
                {challerWon && ' 🏆'}
              </span>
            )}
          </button>

          <div className="feed-challenge-vs-block">
            <span className="feed-challenge-vs">VS</span>
            <span className="feed-challenge-type-pill" style={{ borderColor: statusColor, color: statusColor }}>
              {typeLabel}
            </span>
          </div>

          <button className="feed-challenge-fighter" onClick={() => navigate(`/u/${item.opponent.username}`)}>
            <UserAvatar user={item.opponent} size={56} />
            <span className="feed-challenge-fighter-name">{item.opponent.firstname}</span>
            <span className="feed-challenge-fighter-handle">@{item.opponent.username}</span>
            {isCompleted && (
              <span className="feed-challenge-result-val" style={{ color: opponentWon ? '#22c55e' : 'var(--text-muted)' }}>
                {oppResult}
                {opponentWon && ' 🏆'}
              </span>
            )}
          </button>
        </div>

        {/* Meta row */}
        <div className="feed-challenge-meta-row">
          {detail && <span className="feed-tag">{detail}</span>}
          {item.deadline && !isCompleted && (
            <span className="feed-tag">⏰ {new Date(item.deadline).toLocaleDateString()}</span>
          )}
          {item.message && (
            <span className="feed-challenge-quote">"{item.message}"</span>
          )}
        </div>

        {/* Winner announcement */}
        {isCompleted && (
          <div className="feed-challenge-outcome" style={{ borderColor: statusColor }}>
            {item.winner
              ? <span>🏆 {t.feed_winner}: <strong>{item.winner.firstname}</strong></span>
              : (item.challenger_result != null && item.opponent_result != null)
                ? <span>{t.feed_draw}</span>
                : null}
          </div>
        )}
      </div>
    </FeedCard>
  )
}

function MuscleAchievementCard({ item, t, navigate }) {
  const levelColor = LEVEL_COLORS[item.new_level] || 'var(--accent)'
  const musKey = `muscle_${(item.muscle_slug || '').replace('-', '_')}`
  const muscleName = t[musKey] || item.muscle_slug
  const backMuscles = ['trapezius', 'upper-back', 'lower-back', 'triceps', 'hamstring', 'calves', 'gluteal']
  const view = backMuscles.includes(item.muscle_slug) ? 'back' : 'front'

  return (
    <FeedCard icon="🧬" label={t.feed_muscle_achievement} timestamp={timeAgo(item.timestamp, t)} accent={levelColor}>
      <div className="feed-achievement-layout">
        <button className="feed-achievement-left" onClick={() => navigate(`/u/${item.user.username}`)}>
          <UserAvatar user={item.user} size={56} />
          <div className="feed-achievement-user-info">
            <span className="feed-user-name">{item.user.firstname} {item.user.lastname}</span>
            <span className="feed-user-handle">@{item.user.username}</span>
          </div>
        </button>

        <div className="feed-achievement-center">
          <p className="feed-achievement-headline">
            {t.feed_level_up}
          </p>
          <div className="feed-achievement-level-display">
            {item.old_level && (
              <>
                <span className="feed-ach-level-old">{t[`level_${item.old_level}`] || item.old_level}</span>
                <span className="feed-ach-arrow">→</span>
              </>
            )}
            <span className="feed-ach-level-new" style={{ color: levelColor, borderColor: levelColor }}>
              {t[`level_${item.new_level}`] || item.new_level}
            </span>
          </div>
          <p className="feed-achievement-muscle-name">
            {t.feed_in_muscle} <strong>{muscleName}</strong>
          </p>
        </div>

        <div className="feed-achievement-muscle-map">
          <BodyFigure
            gender={item.user.gender}
            view={view}
            muscles={{ [item.muscle_slug]: item.new_level }}
          />
        </div>
      </div>
    </FeedCard>
  )
}

function FeedItem({ item, t, lang, navigate }) {
  switch (item.type) {
    case 'new_meal':          return <NewMealCard item={item} t={t} lang={lang} navigate={navigate} />
    case 'new_workout':       return <NewWorkoutCard item={item} t={t} lang={lang} navigate={navigate} />
    case 'friend_pr':         return <FriendPRCard item={item} t={t} navigate={navigate} />
    case 'friend_challenge':  return <FriendChallengeCard item={item} t={t} navigate={navigate} />
    case 'muscle_achievement':return <MuscleAchievementCard item={item} t={t} navigate={navigate} />
    default: return null
  }
}

function TrendingCard({ type, item, t, lang, navigate }) {
  const isWorkout = type === 'workout'
  const obj = isWorkout ? item.workout : item.meal
  const name = (lang === 'ka' && obj.name_ka) ? obj.name_ka : obj.name
  const imgUrl = resolveAssetUrl(obj.image_url)
  const dest = isWorkout ? `/workouts?open=${obj.id}` : `/mealplans?open=${obj.id}`

  return (
    <button className="trending-card" onClick={() => navigate(dest)}>
      <div className="trending-card-img-wrap">
        {imgUrl
          ? <img src={imgUrl} alt="" className="trending-card-img" />
          : <div className="trending-card-img-placeholder">{isWorkout ? '🏋️' : '🥗'}</div>
        }
        <span className="trending-card-badge">🔥 {item.trend_views}</span>
      </div>
      <div className="trending-card-body">
        <p className="trending-card-type">{isWorkout ? t.feed_trending_workout : t.feed_trending_meal}</p>
        <p className="trending-card-name">{name}</p>
        <p className="trending-card-meta">
          {isWorkout
            ? `${obj.days_per_week}×/wk · ${obj.level}`
            : `${obj.calories} kcal · ${obj.goal}`
          }
        </p>
      </div>
    </button>
  )
}

// ── Online Friends Sidebar ─────────────────────────────────────────────────────

function OnlineSidebar({ t, navigate }) {
  const [data, setData] = useState(null)

  useEffect(() => {
    api.get('/feed/online-friends').then(r => setData(r.data)).catch(() => {})
    const id = setInterval(() => {
      api.get('/feed/online-friends').then(r => setData(r.data)).catch(() => {})
    }, 30_000)
    return () => clearInterval(id)
  }, [])

  const friends = data?.friends || []
  const onlineCount = data?.online_count ?? 0

  return (
    <aside className="online-sidebar">
      <div className="online-sidebar-header">
        <h3 className="online-sidebar-title">{t.online_sidebar_title}</h3>
        {friends.length > 0 && (
          <span className="online-sidebar-count">
            <span className="online-dot" />
            {onlineCount} {t.online_sidebar_count_one}
          </span>
        )}
      </div>

      {friends.length === 0 ? (
        <p className="online-sidebar-none">{t.online_sidebar_none}</p>
      ) : (
        <ul className="online-sidebar-list">
          {friends.map((f) => (
            <li key={f.id}>
              <button
                className="online-sidebar-item"
                onClick={() => navigate(`/u/${f.username}`)}
              >
                <span className={`online-sidebar-dot ${f.is_online ? 'is-online' : 'is-offline'}`} />
                <span className="online-sidebar-item-name">
                  {f.firstname} {f.lastname}
                </span>
                <span className="online-sidebar-item-handle">@{f.username}</span>
              </button>
            </li>
          ))}
        </ul>
      )}

      <Link to="/friends" className="online-sidebar-link">
        {t.online_sidebar_friends} →
      </Link>
    </aside>
  )
}

// ── Main Component ─────────────────────────────────────────────────────────────

export default function Home() {
  const { t, lang } = useApp()
  const { user } = useOutletContext()
  const navigate = useNavigate()

  const [feed, setFeed] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const fetchFeed = useCallback(async (silent = false) => {
    if (silent) setRefreshing(true)
    else setLoading(true)
    try {
      const { data } = await api.get('/feed')
      setFeed(data)
    } catch {
      /* silently degrade */
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  useEffect(() => { fetchFeed() }, [fetchFeed])

  const hasTrending = feed && (feed.trending_meals.length > 0 || feed.trending_workouts.length > 0)
  const hasItems = feed && feed.items.length > 0

  return (
    <div className="feed-page-outer">

      {/* ── Page header ──────────────────────────────────────────── */}
      <div className="feed-top-header">
        <div>
          <p className="feed-eyebrow">{t.feed_eyebrow}</p>
          <h1 className="feed-greeting">
            {t.feed_hello}, <span className="feed-greeting-name">{user.firstname}</span>! 👋
          </h1>
        </div>
        <button
          className="btn btn-secondary feed-refresh-btn"
          onClick={() => fetchFeed(true)}
          disabled={refreshing}
        >
          {refreshing ? '⟳' : '↻'} {t.feed_refresh}
        </button>
      </div>

      {/* ── Two-column layout: feed + sidebar ────────────────────── */}
      <div className="feed-layout">

        {/* ── Main feed column ──────────────────────────────────── */}
        <div className="feed-main">
          {loading ? (
            <div className="feed-loading">
              <div className="feed-loading-spinner" />
              <p>{t.feed_loading}</p>
            </div>
          ) : (
            <>
              {/* Trending section */}
              {hasTrending && (
                <section className="feed-section">
                  <div className="feed-section-header">
                    <h2 className="feed-section-title">🔥 {t.feed_trending}</h2>
                    <span className="feed-section-sub">{t.feed_trending_sub}</span>
                  </div>
                  <div className="feed-trending-scroll">
                    {feed.trending_meals.map((item) => (
                      <TrendingCard key={`meal-${item.meal.id}`} type="meal" item={item} t={t} lang={lang} navigate={navigate} />
                    ))}
                    {feed.trending_workouts.map((item) => (
                      <TrendingCard key={`workout-${item.workout.id}`} type="workout" item={item} t={t} lang={lang} navigate={navigate} />
                    ))}
                  </div>
                </section>
              )}

              {/* Activity timeline */}
              <section className="feed-section">
                <div className="feed-section-header">
                  <h2 className="feed-section-title">⚡ {t.feed_timeline}</h2>
                  {hasItems && (
                    <span className="feed-section-sub">{feed.items.length} {t.feed_items_count}</span>
                  )}
                </div>

                {hasItems ? (
                  <div className="feed-timeline">
                    {feed.items.map((item, idx) => (
                      <FeedItem
                        key={`${item.type}-${idx}`}
                        item={item}
                        t={t}
                        lang={lang}
                        navigate={navigate}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="feed-empty-state">
                    <div className="feed-empty-icon">🌱</div>
                    <p className="feed-empty-title">{t.feed_no_friends_msg}</p>
                    <p className="feed-empty-sub">{t.feed_no_friends_sub}</p>
                    <Link
                      to="/friends"
                      className="btn btn-primary"
                      style={{ width: 'auto', display: 'inline-block', padding: '11px 28px', marginTop: 16 }}
                    >
                      {t.feed_find_friends}
                    </Link>
                  </div>
                )}
              </section>
            </>
          )}
        </div>

        {/* ── Online friends sidebar ────────────────────────────── */}
        <OnlineSidebar t={t} navigate={navigate} />
      </div>
    </div>
  )
}
