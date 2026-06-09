import { defineStore } from 'pinia'
import api from '@/api'

const MOCK_SESSIONS = [
  { id: 'S-0124', date: '2026-06-08T02:00:00Z', statut: 'TERMINÉ',  nb_transactions: 1247, taux: 100,  nb_ecarts: 2, nb_lettrees: 1247 },
  { id: 'S-0123', date: '2026-06-07T02:00:00Z', statut: 'ERREUR',   nb_transactions: 0,    taux: 0,    nb_ecarts: 0, nb_lettrees: 0    },
  { id: 'S-0122', date: '2026-06-06T02:00:00Z', statut: 'TERMINÉ',  nb_transactions: 1198, taux: 99.8, nb_ecarts: 0, nb_lettrees: 1196 },
  { id: 'S-0121', date: '2026-06-05T02:00:00Z', statut: 'TERMINÉ',  nb_transactions: 1356, taux: 97.2, nb_ecarts: 1, nb_lettrees: 1319 },
  { id: 'S-0120', date: '2026-06-04T02:00:00Z', statut: 'TERMINÉ',  nb_transactions: 1102, taux: 100,  nb_ecarts: 0, nb_lettrees: 1102 }
]

const MOCK_DETAIL = {
  id: 'S-0124',
  date: '2026-06-08T02:00:00Z',
  statut: 'TERMINÉ',
  taux: 100,
  nb_transactions: 1247,
  nb_lettrees: 1247,
  nb_ecarts: 2,
  nb_critiques: 1,
  ecarts: [
    { code: 'EC-05', type_flux: 'MB→CBS', montant: 450000, criticite: 'Critique',  statut: 'À TRAITER' },
    { code: 'EC-06', type_flux: 'CBS→PI', montant: 87500,  criticite: 'Important', statut: 'À TRAITER' }
  ],
  transactions: [
    { ref: 'TXN-10021', type_flux: 'MB→CBS', montant: 500000, statut: 'Lettrée',     date: '2026-06-08T01:42:00Z' },
    { ref: 'TXN-10022', type_flux: 'CBS→PI', montant: 120000, statut: 'Lettrée',     date: '2026-06-08T01:43:00Z' },
    { ref: 'TXN-10023', type_flux: 'PI→MB',  montant: 250000, statut: 'Non lettrée', date: '2026-06-08T01:44:00Z' },
    { ref: 'TXN-10024', type_flux: 'MB→CBS', montant: 85000,  statut: 'Lettrée',     date: '2026-06-08T01:45:00Z' }
  ]
}

export const useSessionsStore = defineStore('sessions', {
  state: () => ({
    list: [],
    detail: null,
    total: 0,
    loading: false,
    loadingDetail: false,
    filters: { date_debut: '', date_fin: '', statut: '' },
    page: 1,
    pageSize: 10
  }),
  actions: {
    async fetchList() {
      this.loading = true
      try {
        const params = { page: this.page, page_size: this.pageSize, ...this.filters }
        const { data } = await api.get('/sessions/', { params })
        this.list = data.results ?? data
        this.total = data.count ?? data.length
      } catch {
        this.list = MOCK_SESSIONS
        this.total = MOCK_SESSIONS.length
      } finally {
        this.loading = false
      }
    },
    async fetchDetail(id) {
      this.loadingDetail = true
      try {
        const { data } = await api.get(`/sessions/${id}/`)
        this.detail = data
      } catch {
        this.detail = { ...MOCK_DETAIL, id }
      } finally {
        this.loadingDetail = false
      }
    }
  }
})
