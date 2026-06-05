import { resolveAssetUrl } from '../../api/client'

export default function ChallengeAvatar({ user }) {
  const initials = ((user.firstname?.[0] || '') + (user.lastname?.[0] || '')).toUpperCase() || '?'
  const src = resolveAssetUrl(user.avatar_url)
  return (
    <div className="avatar avatar-sm">
      {src ? <img src={src} alt="" className="avatar-img" /> : <span>{initials}</span>}
    </div>
  )
}
