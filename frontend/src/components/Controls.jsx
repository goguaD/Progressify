import { useApp } from '../contexts/AppContext'

export default function Controls({ inline = false }) {
  const { theme, toggleTheme, lang, setLang } = useApp()

  return (
    <div className={inline ? 'controls-inline' : 'controls-bar'}>
      <div className="lang-toggle">
        <button
          className={`lang-btn ${lang === 'en' ? 'active' : ''}`}
          onClick={() => setLang('en')}
        >
          🇬🇧 EN
        </button>
        <span className="lang-divider">|</span>
        <button
          className={`lang-btn ${lang === 'ka' ? 'active' : ''}`}
          onClick={() => setLang('ka')}
        >
          🇬🇪 GE
        </button>
      </div>

      <button
        className="theme-btn"
        onClick={toggleTheme}
        title={theme === 'light' ? 'Dark mode' : 'Light mode'}
      >
        {theme === 'light' ? '🌙' : '☀️'}
      </button>
    </div>
  )
}
