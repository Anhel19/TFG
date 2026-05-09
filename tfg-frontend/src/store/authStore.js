import { create } from 'zustand'
import { persist } from 'zustand/middleware'

/**
 * Store global de autenticación.
 *
 * Persiste en localStorage:
 * - accessToken / refreshToken (JWT de SimpleJWT)
 * - user (datos del usuario logueado)
 *
 * Así, al recargar la página, el usuario sigue logueado.
 */
export const useAuthStore = create(
  persist(
    (set) => ({
      // --- estado ---
      accessToken: null,
      refreshToken: null,
      user: null,

      // --- acciones ---
      setTokens: ({ access, refresh }) =>
        set({ accessToken: access, refreshToken: refresh }),

      setUser: (user) => set({ user }),

      logout: () =>
        set({ accessToken: null, refreshToken: null, user: null }),
    }),
    {
      name: 'truetable-auth', // clave en localStorage
    }
  )
)

// Selector útil: ¿está logueado?
export const isAuthenticated = () =>
  Boolean(useAuthStore.getState().accessToken)