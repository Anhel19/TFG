import { useEffect, useState } from 'react'
import { createReservation, listRestaurants } from '../api/reservations'

const initialForm = {
  restaurant: '',
  guest_name: '',
  guest_email: '',
  guest_phone: '',
  date: '',
  time: '',
  party_size: 2,
  notes: '',
}

export default function ReservationForm() {
  const [form, setForm] = useState(initialForm)
  const [restaurants, setRestaurants] = useState([])
  const [loadingRestaurants, setLoadingRestaurants] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [errors, setErrors] = useState({})
  const [success, setSuccess] = useState(null)

  const today = new Date().toISOString().split('T')[0]

  useEffect(() => {
    listRestaurants()
      .then((data) => {
        const list = Array.isArray(data) ? data : data.results || []
        setRestaurants(list)
      })
      .catch(() => {
        setErrors({ general: 'No se pudieron cargar los restaurantes.' })
      })
      .finally(() => setLoadingRestaurants(false))
  }, [])

  const handleChange = (e) => {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setErrors({})
    setSuccess(null)

    const reservation_datetime = `${form.date}T${form.time}:00`

    const payload = {
      restaurant: Number(form.restaurant),
      guest_name: form.guest_name,
      guest_email: form.guest_email,
      guest_phone: form.guest_phone,
      reservation_datetime,
      party_size: Number(form.party_size),
      notes: form.notes,
    }

    try {
      const reservation = await createReservation(payload)
      setSuccess(reservation)
      setForm(initialForm)
    } catch (err) {
      const data = err.response?.data
      if (data && typeof data === 'object') {
        setErrors(data)
      } else {
        setErrors({ general: 'Error al crear la reserva. Inténtalo de nuevo.' })
      }
    } finally {
      setSubmitting(false)
    }
  }

  const fieldError = (field) => {
    const e = errors[field]
    if (!e) return null
    return Array.isArray(e) ? e[0] : e
  }

  return (
    <div className="w-full max-w-2xl mx-auto p-8 bg-white rounded-2xl shadow-lg">
      <h2 className="text-3xl font-bold text-slate-800 mb-1">Reservar mesa</h2>
      <p className="text-slate-500 mb-6">
        Completa el formulario para reservar en True Table
      </p>

      {success && (
        <div className="mb-6 p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg">
          <p className="font-semibold">¡Reserva creada con éxito! 🎉</p>
          <p className="text-sm mt-1">
            Mesa #{success.table_number} en {success.restaurant_name} para{' '}
            {success.party_size} personas.
          </p>
        </div>
      )}

      {errors.general && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {errors.general}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Restaurante
          </label>
          <select
            name="restaurant"
            value={form.restaurant}
            onChange={handleChange}
            required
            disabled={loadingRestaurants}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 disabled:bg-slate-100"
          >
            <option value="">
              {loadingRestaurants ? 'Cargando...' : 'Selecciona un restaurante'}
            </option>
            {restaurants.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
          {fieldError('restaurant') && (
            <p className="text-red-600 text-sm mt-1">{fieldError('restaurant')}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Nombre completo
          </label>
          <input
            type="text"
            name="guest_name"
            value={form.guest_name}
            onChange={handleChange}
            required
            maxLength={150}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
          {fieldError('guest_name') && (
            <p className="text-red-600 text-sm mt-1">{fieldError('guest_name')}</p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Email
            </label>
            <input
              type="email"
              name="guest_email"
              value={form.guest_email}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
            {fieldError('guest_email') && (
              <p className="text-red-600 text-sm mt-1">{fieldError('guest_email')}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Teléfono
            </label>
            <input
              type="tel"
              name="guest_phone"
              value={form.guest_phone}
              onChange={handleChange}
              required
              maxLength={20}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
            {fieldError('guest_phone') && (
              <p className="text-red-600 text-sm mt-1">{fieldError('guest_phone')}</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Fecha
            </label>
            <input
              type="date"
              name="date"
              min={today}
              value={form.date}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Hora
            </label>
            <input
              type="time"
              name="time"
              value={form.time}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Comensales
            </label>
            <input
              type="number"
              name="party_size"
              min="1"
              max="50"
              value={form.party_size}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>
        {fieldError('reservation_datetime') && (
          <p className="text-red-600 text-sm">{fieldError('reservation_datetime')}</p>
        )}
        {fieldError('party_size') && (
          <p className="text-red-600 text-sm">{fieldError('party_size')}</p>
        )}

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            Notas (opcional)
          </label>
          <textarea
            name="notes"
            value={form.notes}
            onChange={handleChange}
            rows="3"
            placeholder="Alergias, peticiones especiales..."
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none"
          />
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-400 text-white font-medium rounded-lg transition-colors"
        >
          {submitting ? 'Enviando...' : 'Reservar'}
        </button>
      </form>
    </div>
  )
}