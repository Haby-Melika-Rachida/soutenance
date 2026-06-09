import { defineStore } from 'pinia'
import api from '@/api'

const DEMO_USER = {
  username: 'demo',
  prenom: 'Utilisateur',
  nom: 'Démo',
  email: 'demo@liceli.ci',
  role: 'Administrateur',
  profil: 'Administrateur',
  initiales: 'AD'
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    loading: false,
    error: null,
    // Source de vérité réactive — initialisée depuis localStorage au démarrage
    token: localStorage.getItem('access_token') || null
  }),

  getters: {
    // Lisent state.token (réactif) → le guard voit immédiatement les changements
    isAuthenticated: (state) => !!state.token,
    isDemo: (state) => state.token === 'demo-token'
  },

  actions: {
    demoLogin() {
      this.token = 'demo-token'
      localStorage.setItem('access_token', 'demo-token')
      localStorage.setItem('refresh_token', 'demo-refresh')
      this.user = DEMO_USER
    },

    async login(username, password) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.post('/auth/token/', { username, password })
        this.token = data.access
        localStorage.setItem('access_token', data.access)
        localStorage.setItem('refresh_token', data.refresh)
        await this.fetchUser()
        return true
      } catch (err) {
        this.error = err.response?.data?.detail || 'Identifiants incorrects. Vérifiez vos informations.'
        return false
      } finally {
        this.loading = false
      }
    },

    async fetchUser() {
      try {
        const { data } = await api.get('/auth/me/')
        this.user = data
      } catch {
        this.user = { username: 'demo', profil: 'Administrateur', role: 'Administrateur' }
      }
    },

    logout() {
      this.token = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      this.user = null
    }
  }
})
