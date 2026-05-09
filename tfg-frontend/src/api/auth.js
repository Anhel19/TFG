import client from './client'

// POST /api/auth/login/  →  { access, refresh }
export const login = (credentials) =>
  client.post('/auth/login/', credentials).then((res) => res.data)

// POST /api/auth/register/  →  datos del nuevo usuario
export const register = (data) =>
  client.post('/auth/register/', data).then((res) => res.data)

// GET /api/auth/me/  →  datos del usuario autenticado
export const fetchMe = () =>
  client.get('/auth/me/').then((res) => res.data)