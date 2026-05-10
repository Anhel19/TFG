import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

/**
 * Envuelve rutas privadas. Si no hay sesión, redirige a /login
 * guardando la ruta original en location.state.from para volver
 * tras iniciar sesión.
 */
export default function ProtectedRoute({ children }) {
  const accessToken = useAuthStore((s) => s.accessToken)
  const location = useLocation()

  if (!accessToken) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  return children
}