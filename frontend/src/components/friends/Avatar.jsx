export default function Avatar({ user, small }) {
  const initials = ((user.firstname?.[0] || '') + (user.lastname?.[0] || '')).toUpperCase() || '?'
  return (
    <div className={`avatar ${small ? 'avatar-sm' : ''} ${user.is_online ? 'is-online' : ''}`}>
      <span>{initials}</span>
      {typeof user.is_online === 'boolean' && (
        <span className={`status-dot ${user.is_online ? 'online' : 'offline'}`} />
      )}
    </div>
  )
}
