import { NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

const linkBase =
  'px-3 py-2 rounded-lg text-sm font-medium transition-colors'
const linkActive = 'bg-emerald-600 text-white'
const linkInactive = 'text-slate-700 hover:bg-slate-200'

export default function Navbar() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const accessToken = useAuthStore((s) => s.accessToken)
  const logout = useAuthStore((s) => s.logout)

  const isAuth = Boolean(accessToken)

  const handleLogout = () => {
    logout()
    navigate('/', { replace: true })
  }

  return (
    <nav className="bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* Logo / nombre */}
        <NavLink to="/" className="flex items-center gap-2">
          <img src="/logo.jpg" alt="True Table" className="h-10 w-10 rounded-lg" />
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

          {isAuth && (
            <NavLink
              to="/mis-reservas"
              className={({ isActive }) =>
                `${linkBase} ${isActive ? linkActive : linkInactive}`
              }
            >
              Mis reservas
            </NavLink>
          )}

          {isAuth ? (
            <>
              <span className="px-3 py-2 text-sm text-slate-600 hidden sm:inline">
                Hola, <span className="font-medium">{user?.first_name || user?.email}</span>
              </span>
              <button
                onClick={handleLogout}
                className={`${linkBase} ${linkInactive}`}
              >
                Salir
              </button>
            </>
          ) : (
            <>
              <NavLink
                to="/login"
                className={({ isActive }) =>
                  `${linkBase} ${isActive ? linkActive : linkInactive}`
                }
              >
                Entrar
              </NavLink>
              <NavLink
                to="/registro"
                className={({ isActive }) =>
                  `${linkBase} ${isActive
                    ? linkActive
                    : 'bg-emerald-600 text-white hover:bg-emerald-700'}`
                }
              >
                Registro
              </NavLink>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}