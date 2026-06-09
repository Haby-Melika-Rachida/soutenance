<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Journaux d'exécution</h1>
        <p class="page-subtitle">Métriques de chaque session batch de rapprochement</p>
      </div>
    </div>

    <!-- Onglets -->
    <div class="tabs mb-4">
      <button class="tab-btn" :class="{ active: activeTab === 'logs' }" @click="activeTab = 'logs'">
        Journaux d'exécution
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'metrics' }" @click="activeTab = 'metrics'">
        Métriques
      </button>
    </div>

    <!-- ── ONGLET 1 : Journaux d'exécution ── -->
    <template v-if="activeTab === 'logs'">
      <!-- Filtres date -->
      <div class="filters-bar">
        <div class="form-group">
          <label class="form-label">Date début</label>
          <input v-model="store.filters.date_debut" type="date" class="form-control" />
        </div>
        <div class="form-group">
          <label class="form-label">Date fin</label>
          <input v-model="store.filters.date_fin" type="date" class="form-control" />
        </div>
        <div class="filter-actions">
          <button class="btn btn-primary" @click="applyFilters">Appliquer</button>
          <button class="btn btn-secondary" @click="resetFilters">Réinitialiser</button>
        </div>
      </div>

      <div class="card">
        <div v-if="store.loading" class="loading-state"><div class="spinner" />Chargement…</div>
        <template v-else>
          <div class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID SESSION</th>
                  <th>DATE D'EXÉCUTION</th>
                  <th>DURÉE</th>
                  <th>TX MB</th>
                  <th>TX CBS</th>
                  <th>CYCLES PI</th>
                  <th>ÉCARTS</th>
                  <th>ERREURS API</th>
                  <th>STATUT</th>
                  <th>ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!store.list.length">
                  <td colspan="10"><div class="empty-state">Aucun journal disponible.</div></td>
                </tr>
                <tr v-for="log in store.list" :key="log.id">
                  <td><span class="id-badge">{{ log.id }}</span></td>
                  <td class="text-sm">{{ formatDate(log.date) }}</td>
                  <td class="text-sm">{{ log.duree }}</td>
                  <td>{{ log.txMb ? log.txMb.toLocaleString('fr-FR') : '—' }}</td>
                  <td>{{ log.txCbs ? log.txCbs.toLocaleString('fr-FR') : '—' }}</td>
                  <td>{{ log.cyclesPi }}</td>
                  <td>
                    <span :class="log.ecarts > 0 ? 'val-warning' : 'val-ok'">{{ log.ecarts }}</span>
                  </td>
                  <td>
                    <span :class="log.erreurs > 0 ? 'val-error' : 'val-ok'">{{ log.erreurs }}</span>
                  </td>
                  <td><StatusBadge :status="log.statut" /></td>
                  <td>
                    <button class="btn btn-secondary btn-sm" @click="openDetail(log)">Détail</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="pagination">
            <span>Affichage de {{ store.list.length }} sur {{ store.total }} sessions</span>
            <div class="pagination-controls">
              <button class="page-btn" :disabled="store.page === 1" @click="changePage(store.page - 1)">‹</button>
              <button v-for="p in totalPages" :key="p" class="page-btn"
                :class="{ active: p === store.page }" @click="changePage(p)">{{ p }}</button>
              <button class="page-btn" :disabled="store.page === totalPages" @click="changePage(store.page + 1)">›</button>
            </div>
          </div>
        </template>
      </div>
    </template>

    <!-- ── ONGLET 2 : Métriques ── -->
    <template v-if="activeTab === 'metrics'">
      <!-- 4 KPI compacts -->
      <div class="grid-4 mb-4">
        <div class="kpi-compact">
          <span class="kpi-compact-label">Durée moyenne d'exécution</span>
          <span class="kpi-compact-value">1m 18s</span>
        </div>
        <div class="kpi-compact">
          <span class="kpi-compact-label">Taux de succès des sessions</span>
          <span class="kpi-compact-value kpi-green">96.8%</span>
        </div>
        <div class="kpi-compact">
          <span class="kpi-compact-label">Moyenne erreurs API/session</span>
          <span class="kpi-compact-value">0.2</span>
        </div>
        <div class="kpi-compact">
          <span class="kpi-compact-label">Total transactions traitées (30j)</span>
          <span class="kpi-compact-value">36 847</span>
        </div>
      </div>

      <div class="card">
        <h2 class="card-title mb-4" style="font-size:14px">Performances par session</h2>
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID SESSION</th>
                <th>DATE</th>
                <th>DURÉE</th>
                <th>APPELS API</th>
                <th>PAGES COLLECTÉES</th>
                <th>ERREURS</th>
                <th>SCORE</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in metricsRows" :key="log.id">
                <td><span class="id-badge">{{ log.id }}</span></td>
                <td class="text-sm">{{ formatDate(log.date) }}</td>
                <td class="text-sm">{{ log.duree }}</td>
                <td>{{ log.appelsApi }}</td>
                <td>{{ log.pagesCollectees }}</td>
                <td><span :class="log.erreurs > 0 ? 'val-error' : 'val-ok'">{{ log.erreurs }}</span></td>
                <td><span class="score-badge" :class="scoreBadgeClass(log.score)">{{ log.score }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- ── MODALE DÉTAIL EXÉCUTION ── -->
    <AppModal v-model="showDetailModal" :title="selectedLog ? `Détail de la session ${selectedLog.id}` : ''" width="560px">
      <template #header-extra v-if="selectedLog">
        <StatusBadge :status="selectedLog.statut" />
      </template>

      <template v-if="selectedLog">
        <!-- Bandeau erreur -->
        <div v-if="selectedLog.statut === 'ERREUR'" class="error-banner">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:16px;height:16px;flex-shrink:0">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          La session s'est terminée en erreur après 3 tentatives sur API-CORE. Les données collectées avant l'erreur ont été conservées.
        </div>

        <!-- Section 1 : Informations générales -->
        <p class="section-title">Informations générales</p>
        <div class="detail-grid">
          <div class="detail-row"><span class="detail-label">ID Session</span><span class="mono">{{ selectedLog.id }}</span></div>
          <div class="detail-row"><span class="detail-label">Date d'exécution</span><span>{{ formatDate(selectedLog.date) }}</span></div>
          <div class="detail-row"><span class="detail-label">Statut</span><StatusBadge :status="selectedLog.statut" /></div>
          <div class="detail-row"><span class="detail-label">Durée totale</span><span>{{ selectedLog.duree }}</span></div>
        </div>

        <!-- Section 2 : Métriques de collecte -->
        <p class="section-title mt-4">Métriques de collecte</p>
        <div class="table-wrapper" style="margin-top:8px">
          <table style="font-size:12px">
            <thead>
              <tr>
                <th>Source</th>
                <th style="text-align:right">Éléments collectés</th>
                <th style="text-align:right">Pages parcourues</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in getMetricsForLog(selectedLog)" :key="row.source">
                <td>{{ row.source }}</td>
                <td style="text-align:right">{{ row.elements.toLocaleString('fr-FR') }}</td>
                <td style="text-align:right">{{ row.pages }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Section 3 : Résultats du rapprochement -->
        <p class="section-title mt-4">Résultats du rapprochement</p>
        <div class="results-grid">
          <div class="result-card">
            <span class="result-label">Transactions matchées</span>
            <span class="result-value">{{ getResultsForLog(selectedLog).matched.toLocaleString('fr-FR') }}</span>
          </div>
          <div class="result-card">
            <span class="result-label">Écarts détectés</span>
            <span class="result-value" :class="getResultsForLog(selectedLog).ecarts > 0 ? 'text-error' : ''">
              {{ getResultsForLog(selectedLog).ecarts }}
            </span>
          </div>
          <div class="result-card">
            <span class="result-label">Erreurs API</span>
            <span class="result-value" :class="getResultsForLog(selectedLog).erreurs > 0 ? 'text-error' : ''">
              {{ getResultsForLog(selectedLog).erreurs }}
            </span>
          </div>
          <div class="result-card">
            <span class="result-label">Appels API total</span>
            <span class="result-value">{{ getResultsForLog(selectedLog).appels }}</span>
          </div>
        </div>
      </template>

      <template #footer>
        <button class="btn btn-secondary" @click="showDetailModal = false">Fermer</button>
        <router-link v-if="selectedLog" :to="`/sessions/${selectedLog.id}`" class="modal-session-link" @click="showDetailModal = false">
          Voir le détail de la session →
        </router-link>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useLogsStore } from '@/stores/logs'
import StatusBadge from '@/components/common/StatusBadge.vue'
import AppModal from '@/components/common/AppModal.vue'
import { formatDate } from '@/utils/format'

const store = useLogsStore()
const activeTab = ref('logs')
const showDetailModal = ref(false)
const selectedLog = ref(null)

const totalPages = computed(() => Math.max(1, Math.ceil(store.total / store.pageSize)))

onMounted(() => store.fetchList())

function applyFilters() { store.page = 1; store.fetchList() }
function changePage(p) { if (p < 1 || p > totalPages.value) return; store.page = p; store.fetchList() }
function resetFilters() { store.filters = { date_debut: '', date_fin: '' }; store.page = 1; store.fetchList() }

function openDetail(log) {
  selectedLog.value = log
  showDetailModal.value = true
}

// Métriques pour la modale
function getMetricsForLog(log) {
  if (log.statut === 'ERREUR') {
    return [
      { source: 'API-MOBILE (TX simples)', elements: 0, pages: 0 },
      { source: 'API-MOBILE (TX PI)',      elements: 0, pages: 0 },
      { source: 'API-CORE',               elements: 0, pages: 0 },
      { source: 'API-PI',                 elements: 0, pages: 0 }
    ]
  }
  return [
    { source: 'API-MOBILE (TX simples)', elements: log.txMb,   pages: Math.ceil(log.txMb / 200)   },
    { source: 'API-MOBILE (TX PI)',      elements: log.cyclesPi, pages: Math.ceil(log.cyclesPi / 100) },
    { source: 'API-CORE',               elements: log.txCbs,  pages: Math.ceil(log.txCbs / 200)  },
    { source: 'API-PI',                 elements: log.cyclesPi, pages: Math.ceil(log.cyclesPi / 100) }
  ]
}

function getResultsForLog(log) {
  return {
    matched: log.txMb || 0,
    ecarts:  log.ecarts || 0,
    erreurs: log.erreurs || 0,
    appels:  Math.ceil((log.txMb + log.cyclesPi) / 100) * 4 || 16
  }
}

// Score de performance pour onglet métriques
const metricsRows = computed(() => store.list.map(log => ({
  ...log,
  appelsApi: Math.ceil(((log.txMb || 0) + (log.cyclesPi || 0)) / 100) * 4 || 0,
  pagesCollectees: Math.ceil((log.txMb || 0) / 200) * 2 + Math.ceil((log.cyclesPi || 0) / 100) * 2 || 0,
  score: computeScore(log)
})))

function computeScore(log) {
  if (log.statut === 'ERREUR') return 'Échec'
  const dureeMin = parseDuree(log.duree)
  if (log.erreurs > 0) return 'Dégradé'
  if (dureeMin < 2) return 'Excellent'
  return 'Correct'
}

function parseDuree(dureeStr) {
  if (!dureeStr) return 99
  const m = dureeStr.match(/(\d+)m\s*(\d+)s/)
  if (!m) return 99
  return parseInt(m[1]) + parseInt(m[2]) / 60
}

function scoreBadgeClass(score) {
  if (score === 'Excellent') return 'score-excellent'
  if (score === 'Correct')   return 'score-correct'
  if (score === 'Dégradé')   return 'score-degrade'
  if (score === 'Échec')     return 'score-echec'
  return ''
}
</script>

<style scoped>
.filter-actions { display: flex; gap: 8px; align-items: flex-end; }

.tabs {
  display: flex; gap: 0; border-bottom: 2px solid var(--color-border);
}
.tab-btn {
  padding: 9px 18px; font-size: 13px; font-weight: 500;
  background: none; border: none; cursor: pointer;
  color: var(--color-text-muted); border-bottom: 2px solid transparent;
  margin-bottom: -2px; transition: all 0.15s;
}
.tab-btn:hover { color: var(--color-text); }
.tab-btn.active { color: var(--color-primary); border-bottom-color: var(--color-primary); font-weight: 600; }

.id-badge {
  font-family: 'Courier New', monospace; font-size: 12px;
  background: #eef2ff; padding: 2px 8px; border-radius: 6px;
  color: #4338ca; font-weight: 600; white-space: nowrap;
}

.val-ok      { color: var(--color-success); font-weight: 600; }
.val-warning { color: var(--color-warning); font-weight: 600; }
.val-error   { color: var(--color-error);   font-weight: 600; }

/* KPI compacts */
.kpi-compact {
  background: #fff; border: 1px solid var(--color-border); border-radius: var(--radius);
  padding: 12px 16px; display: flex; flex-direction: column; gap: 5px;
  height: 70px; justify-content: center;
}
.kpi-compact-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: var(--color-text-muted); }
.kpi-compact-value { font-size: 22px; font-weight: 700; color: var(--color-text); line-height: 1.2; }
.kpi-green { color: var(--color-success); }

/* Score badge */
.score-badge { display: inline-block; padding: 2px 9px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.score-excellent { background: #dcfce7; color: #15803d; }
.score-correct   { background: #dbeafe; color: #1d4ed8; }
.score-degrade   { background: #fef3c7; color: #d97706; }
.score-echec     { background: #fee2e2; color: #dc2626; }

/* Modale détail */
.error-banner {
  display: flex; align-items: flex-start; gap: 8px;
  background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5;
  border-radius: 8px; padding: 10px 12px; font-size: 13px; line-height: 1.5;
  margin-bottom: 16px;
}

.section-title {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.06em; color: var(--color-text-muted);
  margin-bottom: 8px;
}
.mt-4 { margin-top: 16px; }

.detail-grid { display: flex; flex-direction: column; gap: 0; }
.detail-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 7px 0; border-bottom: 1px solid #f8fafc; font-size: 13px;
}
.detail-row:last-child { border-bottom: none; }
.detail-label { color: var(--color-text-muted); flex-shrink: 0; min-width: 140px; }
.mono { font-family: 'Courier New', monospace; font-size: 12px; }

.results-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 8px;
}
.result-card {
  background: #f8fafc; border: 1px solid var(--color-border); border-radius: 8px;
  padding: 10px 12px; display: flex; flex-direction: column; gap: 5px;
}
.result-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: var(--color-text-muted); }
.result-value { font-size: 20px; font-weight: 700; color: var(--color-text); }
.text-error { color: var(--color-error); }

.modal-session-link {
  font-size: 13px; color: var(--color-primary); text-decoration: none; font-weight: 500;
  display: inline-flex; align-items: center;
}
.modal-session-link:hover { text-decoration: underline; }
</style>
