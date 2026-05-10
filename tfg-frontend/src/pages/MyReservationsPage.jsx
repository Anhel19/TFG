import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listMyReservations, cancelReservation } from '../api/reservations'

const STATUS_STYLES = {
  PENDING: 'bg-amber-100 text-amber-800 border-amber-200',
  CONFIRMED: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  CANCELLED: 'bg-slate-200 text-slate-600 border-slate-300',
}

function formatDateTime(iso) {
  const d = new Date(iso)
  return d.toLocaleString('es-ES', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function MyReservationsPage() {
  const [reservations, setReservations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [cancellingId, setCancellingId] = useState(null)

  const loadReservations = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await listMyReservations()
      const list = Array.isArray(data) ? data : data.results || []
      setReservations(list)
    } catch (err) {
      setError('No se pudieron cargar tus reservas. Inténtalo más tarde.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadReservations()
  }, [])

  const handleCancel = async (id) => {
    const ok = window.confirm('¿Seguro que quieres cancelar esta reserva?')
    if (!ok) return

    setCancellingId(id)
    try {
      const updated = await cancelReservation(id)
      setReservations((prev) =>
        prev.map((r) => (r.id === id ? { ...r, ...updated } : r))
      )
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        'No se pudo cancelar la reserva. Inténtalo de nuevo.'
      alert(msg)
    } finally {
      setCancellingId(null)
    }
  }

  // --- Estados de UI ---
  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-20 text-center">
        <p className="text-slate-500">Cargando tus reservas...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-20 text-center">
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={loadReservations}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg"
        >
          Reintentar
        </button>
      </div>
    )
  }

  if (reservations.length === 0) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-20 text-center">
        <h1 className="text-3xl font-bold text-slate-800 mb-4">Mis reservas</h1>
        <p className="text-slate-500 mb-6">Aún no tienes ninguna reserva.</p>
        <Link
          to="/reservar"
          className="inline-block px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-lg transition-colors"
        >
          Reservar ahora
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold text-slate-800">Mis reservas</h1>
        <Link
          to="/reservar"
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg transition-colors"
        >
          + Nueva reserva
        </Link>
      </div>

      <div className="space-y-4">
        {reservations.map((r) => {
          const isCancelled = r.status === 'CANCELLED'
          const isPast = new Date(r.reservation_datetime) < new Date()
          const canCancel = !isCancelled && !isPast

          return (
            <div
              key={r.id}
              className={`bg-white rounded-2xl shadow-sm border border-slate-200 p-6 ${
                isCancelled ? 'opacity-60' : ''
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h2 className="text-lg font-semibold text-slate-800">
                    {r.restaurant_name}
                  </h2>
                  <p className="text-sm text-slate-500">
                    Mesa #{r.table_number} · {r.party_size}{' '}
                    {r.party_size === 1 ? 'persona' : 'personas'}
                  </p>
                </div>
                <span
                  className={`text-xs font-medium px-3 py-1 rounded-full border ${
                    STATUS_STYLES[r.status] || STATUS_STYLES.PENDING
                  }`}
                >
                  {r.status_display}
                </span>
              </div>

              <p className="text-slate-700 mb-4">
                📅 {formatDateTime(r.reservation_datetime)}
              </p>

              {canCancel && (
                <button
                  onClick={() => handleCancel(r.id)}
                  disabled={cancellingId === r.id}
                  className="text-sm font-medium text-red-600 hover:text-red-700 disabled:text-slate-400"
                >
                  {cancellingId === r.id ? 'Cancelando...' : 'Cancelar reserva'}
                </button>
              )}
              {isPast && !isCancelled && (
                <span className="text-sm text-slate-400">Reserva pasada</span>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}