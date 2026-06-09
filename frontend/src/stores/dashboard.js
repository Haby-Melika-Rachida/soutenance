import { defineStore } from 'pinia'
import api from '@/api'

const MOCK_KPI = {
  taux_moyen: 99.2,
  transactions_lettrees: 4905,
  ecarts_detectes: 3,
  ecarts_critiques: 1
}

const MOCK_LAST_SESSION = {
  id: 'S-0124',
  date: '2026-06-08T02:00:00Z',
  statut: 'TERMINÉ',
  nb_transactions: 1247,
  nb_lettrees: 1247,
  nb_ecarts: 2,
  nb_critiques: 1,
  taux: 100
}

const MOCK_WEEKLY = {
  labels: ['Sem. 19', 'Sem. 20', 'Sem. 21', 'Sem. 22', 'Sem. 23', 'Sem. 24', 'Sem. 25', 'Sem. 26'],
  data: [0, 0, 3, 0, 0, 1, 0, 2]
}

const lastDate = new Date('2026-06-08')
const monthlyLabels = Array.from({ length: 30 }, (_, i) => {
  const d = new Date(lastDate)
  d.setDate(d.getDate() - (29 - i))
  return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' })
})
const MOCK_MONTHLY = {
  labels: monthlyLabels,
  data: Array.from({ length: 30 }, (_, i) => {
    if (i === 7)  return 3
    if (i === 14) return 1
    if (i === 21) return 2
    if (i === 29) return 2
    return 0
  })
}

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    kpi: null,
    lastSession: null,
    weekly: null,
    monthly: null,
    loading: false
  }),
  actions: {
    async fetchAll() {
      this.loading = true
      try {
        const [kpiRes, sessionRes, weeklyRes, monthlyRes] = await Promise.allSettled([
          api.get('/dashboard/kpi/'),
          api.get('/sessions/last/'),
          api.get('/dashboard/chart/weekly/'),
          api.get('/dashboard/chart/monthly/')
        ])
        this.kpi         = kpiRes.status     === 'fulfilled' ? kpiRes.value.data     : MOCK_KPI
        this.lastSession = sessionRes.status === 'fulfilled' ? sessionRes.value.data : MOCK_LAST_SESSION
        this.weekly      = weeklyRes.status  === 'fulfilled' ? weeklyRes.value.data  : MOCK_WEEKLY
        this.monthly     = monthlyRes.status === 'fulfilled' ? monthlyRes.value.data : MOCK_MONTHLY
      } finally {
        this.loading = false
      }
    }
  }
})
