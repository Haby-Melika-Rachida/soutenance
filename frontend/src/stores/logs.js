import { defineStore } from 'pinia'
import api from '@/api'

const MOCK_LOGS = [
  { id: 'S-0124', date: '2026-06-08T02:00:00Z', duree: '1m 23s', txMb: 1247, txCbs: 1247, cyclesPi: 89, ecarts: 2, erreurs: 0, statut: 'TERMINÉ' },
  { id: 'S-0123', date: '2026-06-07T02:00:00Z', duree: '0m 45s', txMb: 0,    txCbs: 0,    cyclesPi: 0,  ecarts: 0, erreurs: 3, statut: 'ERREUR'  },
  { id: 'S-0122', date: '2026-06-06T02:00:00Z', duree: '1m 18s', txMb: 1198, txCbs: 1198, cyclesPi: 76, ecarts: 0, erreurs: 0, statut: 'TERMINÉ' },
  { id: 'S-0121', date: '2026-06-05T02:00:00Z', duree: '1m 31s', txMb: 1356, txCbs: 1355, cyclesPi: 92, ecarts: 1, erreurs: 0, statut: 'TERMINÉ' },
  { id: 'S-0120', date: '2026-06-04T02:00:00Z', duree: '1m 09s', txMb: 1102, txCbs: 1102, cyclesPi: 71, ecarts: 0, erreurs: 0, statut: 'TERMINÉ' }
]

export const useLogsStore = defineStore('logs', {
  state: () => ({
    list: [],
    total: 0,
    loading: false,
    filters: { date_debut: '', date_fin: '' },
    page: 1,
    pageSize: 10
  }),
  actions: {
    async fetchList() {
      this.loading = true
      try {
        const params = { page: this.page, page_size: this.pageSize, ...this.filters }
        const { data } = await api.get('/batch/logs/', { params })
        this.list = data.results ?? data
        this.total = data.count ?? data.length
      } catch {
        let filtered = [...MOCK_LOGS]
        if (this.filters.date_debut) {
          filtered = filtered.filter(l => l.date >= this.filters.date_debut)
        }
        if (this.filters.date_fin) {
          filtered = filtered.filter(l => l.date <= this.filters.date_fin + 'T23:59:59Z')
        }
        this.list = filtered
        this.total = 124
      } finally {
        this.loading = false
      }
    }
  }
})
