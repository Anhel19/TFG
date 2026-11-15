import { useEffect, useState } from 'react'
import client from '../api/client'

// ── Helpers ──────────────────────────────────────────────────────────────────

const STATUS_STYLES = {
  PENDING:   'bg-amber-100 text-amber-800 border-amber-200',
  CONFIRMED: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  CANCELLED: 'bg-slate-200 text-slate-600 border-slate-300',
}

const STATUS_LABELS = {
  PENDING:   'Pendiente',
  CONFIRMED: 'Confirmada',
  CANCELLED: 'Cancelada',
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

// ── Componente principal ──────────────────────────────────────────────────────

export default function OwnerDashboardPage() {
  const [restaurants, setRestaurants] = useState([])
  const [selectedId, setSelectedId]   = useState(null)
  const [reservations, setReservations] = useState([])
  const [filter, setFilter]           = useState('ALL')
  const [loading, setLoading]         = useState(true)
  const [loadingRes, setLoadingRes]   = useState(false)
  const [error, setError]             = useState(null)
  const [actionId, setActionId]       = useState(null)

  // Cargo mis restaurantes al montar
  useEffect(() => {
    setLoading(true)
    client
      .get('/restaurants/mine/')
      .then((res) => {
        const list = Array.isArray(res.data) ? res.data : res.data.results || []
        setRestaurants(list)
        if (list.length > 0) setSelectedId(list[0].id)
      })
      .catch(() => setError('No se pudieron cargar tus restaurantes.'))
      .finally(() => setLoading(false))
  }, [])

  // Cargo reservas cuando cambia el restaurante seleccionado
  useEffect(() => {
    if (!selectedId) return
    setLoadingRes(true)
    client
      .get(`/reservations/?restaurant=${selectedId}`)
      .then((res) => {
        const list = Array.isArray(res.data) ? res.data : res.data.results || []
        setReservations(list)
      })
      .catch(() => setReservations([]))
      .finally(() => setLoadingRes(false))
  }, [selectedId])

  // Confirmar reserva
  const handleConfirm = async (id) => {
    setActionId(id)
    try {
      const res = await client.patch(`/reservations/${id}/`, { status: 'CONFIRMED' })
      setReservations((prev) =>
        prev.map((r) => (r.id === id ? { ...r, ...res.data } : r))
      )
    } catch {
      alert('No se pudo confirmar la reserva.')
    } finally {
      setActionId(null)
    }
  }

  // Cancelar reserva
  const handleCancel = async (id) => {
    if (!window.confirm('¿Cancelar esta reserva?')) return
    setActionId(id)
    try {
      const res = await client.post(`/reservations/${id}/cancel/`)
      setReservations((prev) =>
        prev.map((r) => (r.id === id ? { ...r, ...res.data } : r))
      )
    } catch (err) {
      alert(err.response?.data?.detail || 'No se pudo cancelar la reserva.')
    } finally {
      setActionId(null)
    }
  }

  // Reservas filtradas
  const filtered = filter === 'ALL'
    ? reservations
    : reservations.filter((r) => r.status === filter)

  // Contadores para las pestañas
  const counts = {
    ALL:       reservations.length,
    PENDING:   reservations.filter((r) => r.status === 'PENDING').length,
    CONFIRMED: reservations.filter((r) => r.status === 'CONFIRMED').length,
    CANCELLED: reservations.filter((r) => r.status === 'CANCELLED').length,
  }

  // ── Render ──────────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-20 text-center">
        <p className="text-slate-500">Cargando tus restaurantes...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-20 text-center">
        <p className="text-red-600">{error}</p>
      </div>
    )
  }

  if (restaurants.length === 0) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-20 text-center">
        <h1 className="text-3xl font-bold text-slate-800 mb-4">Panel del propietario</h1>
        <p className="text-slate-500">Todavía no tienes ningún restaurante registrado.</p>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">

      {/* Cabecera */}
      <h1 className="text-3xl font-bold text-slate-800 mb-8">Panel del propietario</h1>

      {/* Selector de restaurante */}
      {restaurants.length > 1 && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-slate-600 mb-1">
            Restaurante
          </label>
          <select
            value={selectedId}
            onChange={(e) => setSelectedId(Number(e.target.value))}
            className="border border-slate-300 rounded-lg px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          >
            {restaurants.map((r) => (
              <option key={r.id} value={r.id}>{r.name}</option>
            ))}
          </select>
        </div>
      )}

      {/* Info del restaurante seleccionado */}
      {restaurants.find((r) => r.id === selectedId) && (() => {
        const rest = restaurants.find((r) => r.id === selectedId)
        return (
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 mb-8">
            <h2 className="text-xl font-bold text-slate-800">{rest.name}</h2>
            <p className="text-sm text-slate-500 mt-1">
              📍 {rest.address}, {rest.city}
              {rest.phone && <span className="ml-4">📞 {rest.phone}</span>}
            </p>
          </div>
        )
      })()}

      {/* Resumen de contadores */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
        {[
          { key: 'ALL',       label: 'Total',      color: 'bg-slate-100 text-slate-700' },
          { key: 'PENDING',   label: 'Pendientes', color: 'bg-amber-50 text-amber-700' },
          { key: 'CONFIRMED', label: 'Confirmadas',color: 'bg-emerald-50 text-emerald-700' },
          { key: 'CANCELLED', label: 'Canceladas', color: 'bg-red-50 text-red-700' },
        ].map(({ key, label, color }) => (
          <div key={key} className={`rounded-xl p-4 ${color}`}>
            <p className="text-3xl font-bold">{counts[key]}</p>
            <p className="text-sm mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Filtros */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {['ALL', 'PENDING', 'CONFIRMED', 'CANCELLED'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              filter === f
                ? 'bg-emerald-600 text-white border-emerald-600'
                : 'bg-white text-slate-600 border-slate-300 hover:border-emerald-400'
            }`}
          >
            {f === 'ALL' ? 'Todas' : STATUS_LABELS[f]}
            <span className="ml-1 opacity-70">({counts[f]})</span>
          </button>
        ))}
      </div>

      {/* Lista de reservas */}
      {loadingRes ? (
        <p className="text-slate-500 text-center py-10">Cargando reservas...</p>
      ) : filtered.length === 0 ? (
        <p className="text-slate-400 text-center py-10">No hay reservas en esta categoría.</p>
      ) : (
        <div className="space-y-4">
          {filtered.map((r) => {
            const isPending   = r.status === 'PENDING'
            const isCancelled = r.status === 'CANCELLED'
            const isWorking   = actionId === r.id

            return (
              <div
                key={r.id}
                className={`bg-white rounded-2xl border border-slate-200 shadow-sm p-5 ${
                  isCancelled ? 'opacity-60' : ''
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  {/* Info de la reserva */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="font-semibold text-slate-800 truncate">
                        {r.guest_name}
                      </h3>
                      <span
                        className={`text-xs font-medium px-2.5 py-0.5 rounded-full border shrink-0 ${
                          STATUS_STYLES[r.status] || STATUS_STYLES.PENDING
                        }`}
                      >
                        {STATUS_LABELS[r.status] || r.status}
                      </span>
                    </div>
                    <p className="text-sm text-slate-500">
                      📅 {formatDateTime(r.reservation_datetime)}
                    </p>
                    <p className="text-sm text-slate-500 mt-0.5">
                      👥 {r.party_size} {r.party_size === 1 ? 'persona' : 'personas'} ·
                      Mesa #{r.table_number}
                    </p>
                    {r.guest_email && (
                      <p className="text-sm text-slate-400 mt-0.5">✉️ {r.guest_email}</p>
                    )}
                    {r.notes && (
                      <p className="text-sm text-slate-500 mt-1 italic">
                        💬 {r.notes}
                      </p>
                    )}
                  </div>

                  {/* Acciones */}
                  {!isCancelled && (
                    <div className="flex flex-col gap-2 shrink-0">
                      {isPending && (
                        <button
                          onClick={() => handleConfirm(r.id)}
                          disabled={isWorking}
                          className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white text-sm font-medium rounded-lg transition-colors"
                        >
                          {isWorking ? '...' : 'Confirmar'}
                        </button>
                      )}
                      <button
                        onClick={() => handleCancel(r.id)}
                        disabled={isWorking}
                        className="px-4 py-1.5 bg-white hover:bg-red-50 disabled:bg-slate-100 text-red-600 text-sm font-medium rounded-lg border border-red-200 transition-colors"
                      >
                        {isWorking ? '...' : 'Cancelar'}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
