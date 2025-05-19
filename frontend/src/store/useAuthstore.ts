import { create } from 'zustand'
import { persist } from 'zustand/middleware'
interface AuthState {
  isAuthenticated: boolean
  user: any
  login: (user: any) => void
  logout: () => void
}

export const useAuthstore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      user: null,
      login: (user) => set({ isAuthenticated: true, user }),
      logout: () => set({ isAuthenticated: false, user: null }),
    }),
    {
      name: 'auth-storage', // key in localStorage
      partialize: (state) => ({ isAuthenticated: state.isAuthenticated, user: state.user }), // Optional: persist only specific keys
    }
  )
)
