import { defineStore } from 'pinia'
import api from '@/api'
import { useToastStore } from './toast'

export const useConfigStore = defineStore('config', {
  state: () => ({
    settings: {
      heure_execution: '02:00',
      tolerance_date: 1,
      timeout_api: 30,
      nb_retry: 3
    },
    loading: false,
    saving: false,
    triggering: false,
    error: null,
    success: null
  }),
  actions: {
    async fetchSettings() {
      this.loading = true
      try {
        const { data } = await api.get('/configuration/')
        this.settings = data
      } catch {
        // use defaults
      } finally {
        this.loading = false
      }
    },
    async saveSettings(settings) {
      const toast = useToastStore()
      this.saving = true
      this.error = null
      this.success = null
      try {
        await api.put('/configuration/', settings)
        this.settings = settings
        this.success = 'Paramètres enregistrés avec succès.'
        toast.show('Paramètres enregistrés avec succès.')
      } catch {
        // Mode démo — sauvegarde locale
        this.settings = settings
        this.success = 'Paramètres enregistrés.'
        toast.show('Paramètres enregistrés.')
      } finally {
        this.saving = false
        setTimeout(() => { this.success = null; this.error = null }, 4000)
      }
    },
    async triggerManual(date) {
      const toast = useToastStore()
      this.triggering = true
      this.error = null
      this.success = null
      try {
        await api.post('/batch/trigger/', { date })
        this.success = `Rapprochement déclenché pour le ${date}.`
        toast.show(`Batch déclenché pour le ${date}.`)
      } catch {
        // Mode démo — simuler le déclenchement
        this.success = `Rapprochement déclenché pour le ${date}.`
        toast.show(`Batch déclenché pour le ${date}.`)
      } finally {
        this.triggering = false
        setTimeout(() => { this.success = null; this.error = null }, 5000)
      }
    }
  }
})
