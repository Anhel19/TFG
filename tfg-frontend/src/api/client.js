import axios from 'axios'
import { useAuthStore } from '../store/authStore'

// URL base de la API:
// - En producción: viene de la variable VITE_API_URL (configurada en Vercel)
// - En local: usa '/api' que Vite proxea al backend de desarrollo
const API_URL = import.meta.env.VITE_API_URL || '/api'

const client = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// --- Request interceptor: inyecta el access token en cada petición ---
client.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// --- Response interceptor: refresca el access token cuando expira ---
let isRefreshing = false
let queue = []

const processQueue = (error, token = null) => {
  queue.forEach((p) => (error ? p.reject(error) : p.resolve(token)))
  queue = []
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const status = error.response?.status

    // Si no es 401, o ya reintentamos esta petición, propaga el error
    if (status !== 401 || originalRequest._retry) {
      return Promise.reject(error)
    }

    // Si la propia llamada fallida es la del refresh, hacemos logout
    if (originalRequest.url?.includes('/auth/refresh')) {
      useAuthStore.getState().logout()
      return Promise.reject(error)
    }

    const { refreshToken, setTokens, logout } = useAuthStore.getState()
    if (!refreshToken) {
      logout()
      return Promise.reject(error)
    }

    // Si ya hay un refresh en marcha, encolamos esta petición
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        queue.push({ resolve, reject })
      })
        .then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return client(originalRequest)
        })
        .catch((err) => Promise.reject(err))
    }

    originalRequest._retry = true
    isRefreshing = true

    try {
      // Llamada con axios "puro" para no entrar en bucle con el interceptor
      const { data } = await axios.post(`${API_URL}/auth/refresh/`, {
        refresh: refreshToken,
      })

      // SimpleJWT con ROTATE_REFRESH_TOKENS=True devuelve también un nuevo refresh
      setTokens({
        access: data.access,
        refresh: data.refresh ?? refreshToken,
      })

      processQueue(null, data.access)
      originalRequest.headers.Authorization = `Bearer ${data.access}`
      return client(originalRequest)
    } catch (refreshError) {
      processQueue(refreshError, null)
      logout()
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  }
)

export default client