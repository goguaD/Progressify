import { useState } from 'react'

export default function StarRating({ rating = 0, myRating, onRate, size = 18 }) {
  const [hover, setHover] = useState(null)

  const display = hover ?? myRating ?? rating
  const interactive = !!onRate

  const handleClick = (value) => {
    if (!interactive) return
    if (myRating === value) {
      onRate(0)
    } else {
      onRate(value)
    }
  }

  return (
    <span
      className="star-rating"
      onMouseLeave={() => setHover(null)}
      style={{ fontSize: size }}
    >
      {[1, 2, 3, 4, 5].map(star => {
        const full = display >= star
        const half = !full && display >= star - 0.5
        return (
          <span key={star} className="star-wrap" style={{ position: 'relative', cursor: interactive ? 'pointer' : 'default' }}>
            {interactive && (
              <>
                <span
                  className="star-hit star-hit-left"
                  onMouseEnter={() => setHover(star - 0.5)}
                  onClick={() => handleClick(star - 0.5)}
                />
                <span
                  className="star-hit star-hit-right"
                  onMouseEnter={() => setHover(star)}
                  onClick={() => handleClick(star)}
                />
              </>
            )}
            <span className={`star ${full ? 'star-full' : half ? 'star-half' : 'star-empty'}`}>
              ★
            </span>
          </span>
        )
      })}
    </span>
  )
}
