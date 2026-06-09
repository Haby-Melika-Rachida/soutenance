import { defineStore } from 'pinia'
import api from '@/api'

const MOCK_AUDIT = [
  { id: 1, date: '2026-06-08T08:12:00Z', utilisateur: 'resp.mb',      action: 'CONNEXION',          entite: 'Utilisateur',          id_entite: 'USR-002', ip: '192.168.1.45', detail: 'Connexion réussie' },
  { id: 2, date: '2026-06-08T07:58:00Z', utilisateur: 'admin.liceli', action: 'MODIFICATION CONFIG', entite: 'ConfigurationBatch',   id_entite: 'CFG-001', ip: '192.168.1.12', detail: 'Heure modifiée : 01:00 → 02:00' },
  { id: 3, date: '2026-06-07T16:30:00Z', utilisateur: 'agent.bo1',    action: 'ANNOTATION',          entite: 'EcartDetecte',         id_entite: 'EC-06',   ip: '192.168.1.78', detail: 'Statut : À TRAITER → EN COURS' },
  { id: 4, date: '2026-06-07T09:15:00Z', utilisateur: 'agent.bo2',    action: 'ANNOTATION',          entite: 'EcartDetecte',         id_entite: 'EC-02',   ip: '192.168.1.91', detail: 'Statut : EN COURS → RÉSOLU' },
  { id: 5, date: '2026-06-07T02:05:00Z', utilisateur: 'SYSTÈME',      action: 'BATCH EXÉCUTÉ',       entite: 'ReconciliationSession',id_entite: 'S-0123',  ip: '127.0.0.1',    detail: 'Session terminée avec erreur' },
  { id: 6, date: '2026-06-06T14:20:00Z', utilisateur: 'audit.user',   action: 'CONNEXION',           entite: 'Utilisateur',          id_entite: 'USR-005', ip: '192.168.1.33', detail: 'Connexion réussie' },
  { id: 7, date: '2026-06-06T02:03:00Z', utilisateur: 'SYSTÈME',      action: 'BATCH EXÉCUTÉ',       entite: 'ReconciliationSession',id_entite: 'S-0122',  ip: '127.0.0.1',    detail: 'Session terminée — 0 écart' },
  { id: 8, date: '2026-06-05T11:00:00Z', utilisateur: 'admin.liceli', action: 'CRÉATION USER',       entite: 'Utilisateur',          id_entite: 'USR-005', ip: '192.168.1.12', detail: 'Compte audit.user créé' }
]

export const ACTION_TYPES = ['CONNEXION', 'ANNOTATION', 'BATCH EXÉCUTÉ', 'MODIFICATION CONFIG', 'CRÉATION USER']

export const useAuditStore = defineStore('audit', {
  state: () => ({
    list: [],
    total: 0,
    loading: false,
    filters: { utilisateur: '', action: '', date_debut: '', date_fin: '' },
    page: 1,
    pageSize: 15
  }),
  getters: {
    listWithLabels: state => state.list.map(a => ({ ...a, action_label: a.action }))
  },
  actions: {
    async fetchList() {
      this.loading = true
      try {
        const params = { page: this.page, page_size: this.pageSize, ...this.filters }
        const { data } = await api.get('/audit/', { params })
        this.list = data.results ?? data
        this.total = data.count ?? data.length
      } catch {
        let filtered = [...MOCK_AUDIT]
        if (this.filters.utilisateur) filtered = filtered.filter(a => a.utilisateur.includes(this.filters.utilisateur))
        if (this.filters.action)      filtered = filtered.filter(a => a.action === this.filters.action)
        if (this.filters.date_debut)  filtered = filtered.filter(a => a.date >= this.filters.date_debut)
        if (this.filters.date_fin)    filtered = filtered.filter(a => a.date <= this.filters.date_fin + 'T23:59:59Z')
        this.list = filtered
        this.total = 247
      } finally {
        this.loading = false
      }
    }
  }
})
