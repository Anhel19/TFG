import client from './client'

// --- Restaurantes ---
export const listRestaurants = () =>
  client.get('/restaurants/').then((res) => res.data)

// --- Reservas ---
export const createReservation = (data) =>
  client.post('/reservations/', data).then((res) => res.data)

// GET /api/reservations/  → backend ya filtra por usuario autenticado
export const listMyReservations = () =>
  client.get('/reservations/').then((res) => res.data)

// POST /api/reservations/{id}/cancel/
export const cancelReservation = (id) =>
  client.post(`/reservations/${id}/cancel/`).then((res) => res.data)