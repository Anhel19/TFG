import { NavLink } from 'react-router-dom'

const linkBase =
  'px-3 py-2 rounded-lg text-sm font-medium transition-colors'
const linkActive = 'bg-emerald-600 text-white'
const linkInactive = 'text-slate-700 hover:bg-slate-200'

export default function Navbar() {
  return (
    <nav className="bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* Logo / nombre */}
        <NavLink to="/" className="flex items-center gap-2">
          <span className="text-2xl">🍽️</span>
          <span className="text-xl font-bold text-slate-800">True Table</span>
        </NavLink>

        {/* Enlaces */}
        <div className="flex items-center gap-1">
          <NavLink
            to="/reservar"
            className={({ isActive }) =>
              `${linkBase} ${isActive ? linkActive : linkInactive}`
            }
          >
            Reservar
          </NavLink>
          <NavLink
            to="/mis-reservas"
            className={({ isActive }) =>
              `${linkBase} ${isActive ? linkActive : linkInactive}`
            }
          >
            Mis reservas
          </NavLink>
          <NavLink
            to="/login"
            className={({ isActive }) =>
              `${linkBase} ${isActive ? linkActive : linkInactive}`
            }
          >
            Entrar
          </NavLink>
        </div>
      </div>
    </nav>
  )
}