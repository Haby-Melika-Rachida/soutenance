import { defineStore } from 'pinia'
import api from '@/api'
import { useToastStore } from './toast'

const MOCK_ECARTS = [
  {
    id: 1, code: 'E-2024-001', type_flux: 'MB→CBS', montant: 250000, criticite: 'Critique',
    statut: 'À TRAITER', date: '2024-06-06T02:15:00Z', session_id: 'S-2024-0142',
    compte: 'CI0001234567890',
    compte_debiteur: 'CI0001234567890', compte_crediteur: 'CI0009876543210',
    e2e_id: 'E2E-MB-20240606-001', message_id: 'MSG-20240606-1001',
    etape_echouee: 'Rapprochement CBS',
    message_echouee: 'Transaction présente dans Mobile Banking mais absente du Core Banking System après délai de grâce de 24h. Vérifier le traitement CBS du 06/06/2024.',
    historique: [
      { date: '2024-06-06T02:15:00Z', action: 'Détection', auteur: 'Système', detail: 'Écart détecté lors du batch nocturne - session S-2024-0142' }
    ]
  },
  {
    id: 2, code: 'E-2024-002', type_flux: 'CBS→PI', montant: 75000, criticite: 'Important',
    statut: 'EN COURS', date: '2024-06-06T02:20:00Z', session_id: 'S-2024-0142',
    compte: 'CI0002345678901',
    compte_debiteur: 'CI0002345678901', compte_crediteur: 'CI0008765432109',
    e2e_id: 'E2E-CBS-20240606-002', message_id: 'MSG-20240606-1002',
    etape_echouee: 'Rapprochement PI',
    message_echouee: 'Cycle PI absent pour ce transfert interbancaire. Le message ISO 20022 a été émis par CBS mais non reçu par la Plateforme Interopérabilité.',
    historique: [
      { date: '2024-06-06T02:20:00Z', action: 'Détection', auteur: 'Système', detail: 'Écart détecté lors du batch nocturne' },
      { date: '2024-06-06T10:32:00Z', action: 'Prise en charge', auteur: 'M. Diallo', detail: 'Statut changé : À TRAITER → EN COURS. Relance envoyée à la Plateforme PI.' }
    ]
  },
  {
    id: 3, code: 'E-2024-003', type_flux: 'PI→MB', montant: 540000, criticite: 'Critique',
    statut: 'À TRAITER', date: '2024-06-05T02:10:00Z', session_id: 'S-2024-0141',
    compte: 'CI0003456789012',
    compte_debiteur: 'CI0003456789012', compte_crediteur: 'CI0007654321098',
    e2e_id: 'E2E-PI-20240605-003', message_id: 'MSG-20240605-1003',
    etape_echouee: 'Rapprochement MB',
    message_echouee: 'Virement reçu par la Plateforme Interopérabilité non retrouvé dans le journal Mobile Banking. Montant supérieur au seuil d\'alerte critique (500 000 XOF).',
    historique: [
      { date: '2024-06-05T02:10:00Z', action: 'Détection', auteur: 'Système', detail: 'Écart critique détecté - montant supérieur au seuil' }
    ]
  },
  {
    id: 4, code: 'E-2024-004', type_flux: 'MB→CBS', montant: 8500, criticite: 'Faible',
    statut: 'RÉSOLUS', date: '2024-06-05T02:35:00Z', session_id: 'S-2024-0141',
    compte: 'CI0004567890123',
    compte_debiteur: 'CI0004567890123', compte_crediteur: 'CI0006543210987',
    e2e_id: 'E2E-MB-20240605-004', message_id: 'MSG-20240605-1004',
    etape_echouee: 'Rapprochement CBS',
    message_echouee: 'Différence de date de valeur d\'un jour entre MB et CBS. Dans la tolérance configurée.',
    historique: [
      { date: '2024-06-05T02:35:00Z', action: 'Détection', auteur: 'Système', detail: 'Écart de date détecté (tolérance: 1 jour)' },
      { date: '2024-06-05T11:00:00Z', action: 'Résolution', auteur: 'M. Diallo', detail: 'Doublon identifié et supprimé. Transaction originale correcte.' }
    ]
  },
  {
    id: 5, code: 'E-2024-005', type_flux: 'CBS→PI', montant: 120000, criticite: 'Important',
    statut: 'À TRAITER', date: '2024-06-04T02:05:00Z', session_id: 'S-2024-0139',
    compte: 'CI0005678901234',
    compte_debiteur: 'CI0005678901234', compte_crediteur: 'CI0005432109876',
    e2e_id: 'E2E-CBS-20240604-005', message_id: 'MSG-20240604-1005',
    etape_echouee: 'Traitement PI',
    message_echouee: 'Timeout lors de la récupération des cycles PI. Le système PI n\'a pas répondu dans le délai imparti (30s).',
    historique: [
      { date: '2024-06-04T02:05:00Z', action: 'Détection', auteur: 'Système', detail: 'Timeout API PI détecté après 30s' }
    ]
  },
  {
    id: 6, code: 'E-2024-006', type_flux: 'PI→MB', montant: 31000, criticite: 'Faible',
    statut: 'EN COURS', date: '2024-06-04T02:40:00Z', session_id: 'S-2024-0139',
    compte: 'CI0006789012345',
    compte_debiteur: 'CI0006789012345', compte_crediteur: 'CI0004321098765',
    e2e_id: 'E2E-PI-20240604-006', message_id: 'MSG-20240604-1006',
    etape_echouee: 'Rapprochement MB',
    message_echouee: 'Délai de traitement PI anormalement long. La transaction a été soumise avec 47 minutes de retard par rapport à l\'horodatage PI.',
    historique: [
      { date: '2024-06-04T02:40:00Z', action: 'Détection', auteur: 'Système', detail: 'Délai de traitement PI excessif détecté' },
      { date: '2024-06-04T13:30:00Z', action: 'Prise en charge', auteur: 'A. Kone', detail: 'Ticket ouvert auprès du prestataire PI. En attente de retour.' }
    ]
  },
  {
    id: 7, code: 'E-2024-007', type_flux: 'MB→CBS', montant: 890000, criticite: 'Critique',
    statut: 'À TRAITER', date: '2024-06-03T02:12:00Z', session_id: 'S-2024-0138',
    compte: 'CI0007890123456',
    compte_debiteur: 'CI0007890123456', compte_crediteur: 'CI0003210987654',
    e2e_id: 'E2E-MB-20240603-007', message_id: 'MSG-20240603-1007',
    etape_echouee: 'Rapprochement CBS',
    message_echouee: 'Montant critique (890 000 XOF) présent en MB absent du CBS. Vérification urgente requise avant clôture journalière.',
    historique: [
      { date: '2024-06-03T02:12:00Z', action: 'Détection', auteur: 'Système', detail: 'Écart critique - alerte envoyée au superviseur' }
    ]
  },
  {
    id: 8, code: 'E-2024-008', type_flux: 'CBS→PI', montant: 45000, criticite: 'Important',
    statut: 'RÉSOLUS', date: '2024-06-03T02:28:00Z', session_id: 'S-2024-0138',
    compte: 'CI0008901234567',
    compte_debiteur: 'CI0008901234567', compte_crediteur: 'CI0002109876543',
    e2e_id: 'E2E-CBS-20240603-008', message_id: 'MSG-20240603-1008',
    etape_echouee: 'Rapprochement PI',
    message_echouee: 'Message ISO 20022 reçu avec identifiant duplicata par la Plateforme PI.',
    historique: [
      { date: '2024-06-03T02:28:00Z', action: 'Détection', auteur: 'Système', detail: 'Duplicata détecté au niveau PI' },
      { date: '2024-06-03T09:15:00Z', action: 'Résolution', auteur: 'F. Traore', detail: 'Duplicata confirmé et supprimé. Aucun impact financier.' }
    ]
  }
]

export const useEcartsStore = defineStore('ecarts', {
  state: () => ({
    list: [],
    total: 0,
    loading: false,
    filters: { type_flux: '', criticite: '', statut: '', date_debut: '', date_fin: '' },
    page: 1,
    pageSize: 10
  }),
  actions: {
    async fetchList() {
      this.loading = true
      try {
        const params = { page: this.page, page_size: this.pageSize, ...this.filters }
        const { data } = await api.get('/ecarts/', { params })
        this.list = data.results ?? data
        this.total = data.count ?? data.length
      } catch {
        let filtered = MOCK_ECARTS
        if (this.filters.type_flux) filtered = filtered.filter(e => e.type_flux === this.filters.type_flux)
        if (this.filters.criticite) filtered = filtered.filter(e => e.criticite === this.filters.criticite)
        if (this.filters.statut)    filtered = filtered.filter(e => e.statut === this.filters.statut)
        this.list = filtered
        this.total = filtered.length
      } finally {
        this.loading = false
      }
    },

    async prendreEnCharge(id, annotationData) {
      const toast = useToastStore()
      try {
        await api.patch(`/ecarts/${id}/annoter/`, annotationData)
        const idx = this.list.findIndex(e => e.id === id)
        if (idx !== -1) {
          this.list[idx].statut = annotationData.statut
          this.list[idx].historique = [
            ...(this.list[idx].historique ?? []),
            { date: new Date().toISOString(), action: 'Prise en charge', auteur: 'Moi', detail: annotationData.commentaire }
          ]
        }
        toast.show('Prise en charge enregistrée avec succès.')
        return true
      } catch {
        // Mode démo — mise à jour locale
        const idx = this.list.findIndex(e => e.id === id)
        if (idx !== -1) {
          this.list[idx].statut = annotationData.statut
          this.list[idx].historique = [
            ...(this.list[idx].historique ?? []),
            { date: new Date().toISOString(), action: 'Prise en charge', auteur: 'Démo', detail: annotationData.commentaire }
          ]
        }
        toast.show('Prise en charge enregistrée.')
        return true
      }
    }
  }
})
