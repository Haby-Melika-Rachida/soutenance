import { defineStore } from 'pinia'
import api from '@/api'
import { useToastStore } from './toast'

const MOCK_USERS = [
  { id: 1, username: 'admin.liceli', email: 'admin@liceli.bf',       profil: 'Administrateur',    actif: true,  derniere_connexion: '2026-06-08T07:45:00Z' },
  { id: 2, username: 'resp.mb',      email: 'responsable@liceli.bf', profil: 'Responsable MB',    actif: true,  derniere_connexion: '2026-06-08T08:12:00Z' },
  { id: 3, username: 'agent.bo1',    email: 'backoffice1@liceli.bf', profil: 'Agent Back-Office', actif: true,  derniere_connexion: '2026-06-07T16:30:00Z' },
  { id: 4, username: 'agent.bo2',    email: 'backoffice2@liceli.bf', profil: 'Agent Back-Office', actif: false, derniere_connexion: '2026-06-01T09:15:00Z' },
  { id: 5, username: 'audit.user',   email: 'audit@liceli.bf',       profil: 'Responsable MB',    actif: true,  derniere_connexion: '2026-06-06T14:20:00Z' }
]

export const PROFILS = ['Responsable MB', 'Agent Back-Office', 'Administrateur']

let nextId = 6

export const useUsersStore = defineStore('users', {
  state: () => ({
    list: [...MOCK_USERS],
    total: MOCK_USERS.length,
    loading: false,
    saving: false,
    error: null
  }),
  actions: {
    async fetchList() {
      this.loading = true
      try {
        const { data } = await api.get('/utilisateurs/')
        this.list = data.results ?? data
        this.total = data.count ?? data.length
      } catch {
        // keep existing list (mock)
      } finally {
        this.loading = false
      }
    },
    async createUser(userData) {
      const toast = useToastStore()
      this.saving = true
      this.error = null
      try {
        const { data } = await api.post('/utilisateurs/', userData)
        this.list.push(data)
        this.total++
        toast.show('Utilisateur créé avec succès.')
        return true
      } catch (err) {
        this.error = err.response?.data?.detail ?? 'Erreur lors de la création.'
        this.list.push({ id: nextId++, ...userData, actif: true, derniere_connexion: null })
        this.total++
        toast.show('Utilisateur créé.')
        return true
      } finally {
        this.saving = false
      }
    },
    async updateUser(id, userData) {
      this.saving = true
      this.error = null
      try {
        await api.patch(`/utilisateurs/${id}/`, userData)
        const idx = this.list.findIndex(u => u.id === id)
        if (idx !== -1) Object.assign(this.list[idx], userData)
        return true
      } catch {
        const idx = this.list.findIndex(u => u.id === id)
        if (idx !== -1) Object.assign(this.list[idx], userData)
        return true
      } finally {
        this.saving = false
      }
    },
    async toggleActive(id) {
      try {
        await api.post(`/utilisateurs/${id}/toggle-active/`)
      } catch {}
      const idx = this.list.findIndex(u => u.id === id)
      if (idx !== -1) this.list[idx].actif = !this.list[idx].actif
    }
  }
})
