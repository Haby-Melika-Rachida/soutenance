import { defineStore } from 'pinia'
import api from '@/api'

const MOCK_ANNOTATIONS = [
  {
    id: 1, ecart_code: 'E-2024-002', session_id: 'S-2024-0142',
    analyste: 'M. Diallo', date: '2024-06-06T10:32:00Z',
    statut: 'EN COURS', statut_precedent: 'À TRAITER',
    type_flux: 'CBS→PI', criticite: 'Important',
    commentaire: 'Message ISO 20022 non reçu par PI. Relance envoyée au back-office PI. En attente de confirmation de réception.',
    transaction_concernee: {
      id: 'TXN-10022', montant: 75000,
      e2e_id: 'E2E-CBS-20240606-002', message_id: 'MSG-20240606-1002',
      compte_debit: 'CI0002345678901', compte_credit: 'CI0008765432109',
      date: '2024-06-06T01:43:00Z', statut: 'Non lettrée'
    }
  },
  {
    id: 2, ecart_code: 'E-2024-004', session_id: 'S-2024-0141',
    analyste: 'M. Diallo', date: '2024-06-05T11:00:00Z',
    statut: 'RÉSOLUS', statut_precedent: 'À TRAITER',
    type_flux: 'MB→CBS', criticite: 'Faible',
    commentaire: 'Doublon identifié et supprimé. Transaction originale correcte. Aucun impact financier.',
    transaction_concernee: {
      id: 'TXN-10024', montant: 8500,
      e2e_id: 'E2E-MB-20240605-004', message_id: 'MSG-20240605-1004',
      compte_debit: 'CI0004567890123', compte_credit: 'CI0006543210987',
      date: '2024-06-05T01:55:00Z', statut: 'Lettrée'
    }
  },
  {
    id: 3, ecart_code: 'E-2024-006', session_id: 'S-2024-0139',
    analyste: 'A. Koné', date: '2024-06-04T13:30:00Z',
    statut: 'EN COURS', statut_precedent: 'À TRAITER',
    type_flux: 'PI→MB', criticite: 'Faible',
    commentaire: 'Ticket ouvert auprès du prestataire PI. Délai de traitement anormal signalé. En attente de retour sous 48h.',
    transaction_concernee: {
      id: 'TXN-10031', montant: 31000,
      e2e_id: 'E2E-PI-20240604-006', message_id: 'MSG-20240604-1006',
      compte_debit: 'CI0006789012345', compte_credit: 'CI0004321098765',
      date: '2024-06-04T01:53:00Z', statut: 'Non lettrée'
    }
  },
  {
    id: 4, ecart_code: 'E-2024-008', session_id: 'S-2024-0138',
    analyste: 'F. Traoré', date: '2024-06-03T09:15:00Z',
    statut: 'RÉSOLUS', statut_precedent: 'À TRAITER',
    type_flux: 'CBS→PI', criticite: 'Important',
    commentaire: 'Duplicata confirmé et supprimé. Vérification effectuée côté CBS et PI. Aucun impact sur les soldes.',
    transaction_concernee: {
      id: 'TXN-10042', montant: 45000,
      e2e_id: 'E2E-CBS-20240603-008', message_id: 'MSG-20240603-1008',
      compte_debit: 'CI0008901234567', compte_credit: 'CI0002109876543',
      date: '2024-06-03T01:48:00Z', statut: 'Lettrée'
    }
  },
  {
    id: 5, ecart_code: 'E-2024-002', session_id: 'S-2024-0142',
    analyste: 'A. Koné', date: '2024-06-06T14:00:00Z',
    statut: 'IGNORÉ', statut_precedent: 'EN COURS',
    type_flux: 'CBS→PI', criticite: 'Important',
    commentaire: 'Confirmé que le cycle PI a finalement été reçu avec 2h de retard. Classé sans suite — transaction apurée.',
    transaction_concernee: {
      id: 'TXN-10022', montant: 75000,
      e2e_id: 'E2E-CBS-20240606-002', message_id: 'MSG-20240606-1002',
      compte_debit: 'CI0002345678901', compte_credit: 'CI0008765432109',
      date: '2024-06-06T01:43:00Z', statut: 'Lettrée'
    }
  }
]

export const useAnnotationsStore = defineStore('annotations', {
  state: () => ({
    list: [],
    total: 0,
    loading: false,
    mineOnly: false,
    page: 1,
    pageSize: 10
  }),
  getters: {
    counters: state => ({
      EN_COURS: state.list.filter(a => a.statut === 'EN COURS').length,
      RESOLUS:  state.list.filter(a => a.statut === 'RÉSOLUS').length,
      IGNORE:   state.list.filter(a => a.statut === 'IGNORÉ').length
    })
  },
  actions: {
    async fetchList() {
      this.loading = true
      try {
        const params = { page: this.page, page_size: this.pageSize, mine_only: this.mineOnly }
        const { data } = await api.get('/annotations/', { params })
        this.list = data.results ?? data
        this.total = data.count ?? data.length
      } catch {
        this.list = MOCK_ANNOTATIONS
        this.total = MOCK_ANNOTATIONS.length
      } finally {
        this.loading = false
      }
    },
    async createAnnotation(ecartCode, sessionId, payload) {
      try {
        await api.post('/annotations/', { ecart_code: ecartCode, session_id: sessionId, ...payload })
        await this.fetchList()
        return true
      } catch {
        return false
      }
    }
  }
})
