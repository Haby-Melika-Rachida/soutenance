<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Historique des sessions</h1>
        <p class="page-subtitle">{{ store.total }} session(s) au total</p>
      </div>
      <div class="taux-moyen-card" v-if="tauxMoyen !== null">
        <span class="taux-moyen-label">Taux moyen de réussite</span>
        <span class="taux-moyen-value">{{ tauxMoyen }}</span>
      </div>
    </div>

    <!-- Filtres -->
    <div class="filters-bar">
      <div class="form-group">
        <label class="form-label">Date début</label>
        <input v-model="store.filters.date_debut" type="date" class="form-control" />
      </div>
      <div class="form-group">
        <label class="form-label">Date fin</label>
        <input v-model="store.filters.date_fin" type="date" class="form-control" />
      </div>
      <div class="form-group">
        <label class="form-label">Statut</label>
        <select v-model="store.filters.statut" class="form-control">
          <option value="">Tous les statuts</option>
          <option>TERMINÉ</option>
          <option>ERREUR</option>
          <option>EN COURS</option>
        </select>
      </div>
      <div class="filter-actions">
        <button class="btn btn-primary" @click="applyFilters">Appliquer</button>
        <button class="btn btn-secondary" @click="resetFilters">Réinitialiser</button>
      </div>
    </div>

    <!-- Tableau -->
    <div class="card">
      <div v-if="store.loading" class="loading-state">
        <div class="spinner" />Chargement des sessions...
      </div>
      <template v-else>
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID SESSION</th>
                <th>DATE D'EXÉCUTION</th>
                <th>STATUT</th>
                <th>NB TRANSACTIONS</th>
                <th>TAUX DE LETTRAGE</th>
                <th>NB ÉCARTS</th>
                <th>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="store.list.length === 0">
                <td colspan="7">
                  <div class="empty-state">Aucune session trouvée pour ces critères.</div>
                </td>
              </tr>
              <tr v-for="s in store.list" :key="s.id">
                <td><span class="id-badge">{{ s.id }}</span></td>
                <td>{{ formatDate(s.date) }}</td>
                <td><StatusBadge :status="s.statut" /></td>
                <td>{{ s.nb_transactions > 0 ? s.nb_transactions.toLocaleString('fr-FR') : '—' }}</td>
                <td>
                  <div v-if="s.statut !== 'ERREUR' && (s.taux ?? s.taux_lettrage) > 0"
                    style="display:flex;align-items:center;gap:8px;">
                    <div style="flex:1;height:6px;background:#e2e8f0;border-radius:3px;">
                      <div :style="{
                        width: (s.taux ?? s.taux_lettrage) + '%',
                        height: '100%', borderRadius: '3px',
                        background: (s.taux ?? s.taux_lettrage) >= 95 ? '#16a34a'
                                  : (s.taux ?? s.taux_lettrage) >= 80 ? '#d97706' : '#dc2626'
                      }"></div>
                    </div>
                    <span style="font-size:12px;font-weight:600;width:42px;text-align:right;">
                      {{ s.taux ?? s.taux_lettrage }}%
                    </span>
                  </div>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <span v-if="s.statut === 'ERREUR'" class="text-muted">—</span>
                  <span v-else-if="s.nb_ecarts > 0" class="ecarts-nonzero">{{ s.nb_ecarts }}</span>
                  <span v-else class="ecarts-zero">{{ s.nb_ecarts }}</span>
                </td>
                <td>
                  <router-link :to="`/sessions/${s.id}`" class="btn btn-secondary btn-sm">
                    Voir le détail
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="pagination">
          <span>{{ store.total }} résultat(s)</span>
          <div class="pagination-controls">
            <button class="page-btn" :disabled="store.page === 1" @click="changePage(store.page - 1)">‹</button>
            <button v-for="p in totalPages" :key="p" class="page-btn"
              :class="{ active: p === store.page }" @click="changePage(p)">{{ p }}</button>
            <button class="page-btn" :disabled="store.page === totalPages" @click="changePage(store.page + 1)">›</button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useSessionsStore } from '@/stores/sessions'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { formatDate, formatPercent } from '@/utils/format'

const store = useSessionsStore()
const totalPages = computed(() => Math.max(1, Math.ceil(store.total / store.pageSize)))

const tauxMoyen = computed(() => {
  const valid = store.list.filter(s => s.statut === 'TERMINÉ' && s.taux_lettrage > 0)
  if (!valid.length) return null
  const avg = valid.reduce((sum, s) => sum + s.taux_lettrage, 0) / valid.length
  return formatPercent(avg)
})

function tauxBarClass(taux) {
  if (taux >= 95) return 'taux-bar--green'
  if (taux >= 80) return 'taux-bar--orange'
  return 'taux-bar--red'
}

onMounted(() => store.fetchList())

function applyFilters() { store.page = 1; store.fetchList() }
function changePage(p) {
  if (p < 1 || p > totalPages.value) return
  store.page = p; store.fetchList()
}
function resetFilters() {
  store.filters = { date_debut: '', date_fin: '', statut: '' }
  store.page = 1; store.fetchList()
}
</script>

<style scoped>
/* Carte taux moyen — bleu marine */
.taux-moyen-card {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  background: linear-gradient(135deg, #0d2b5e, #1a3d7a);
  border-radius: var(--radius);
  padding: 10px 20px;
}
.taux-moyen-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: rgba(255,255,255,0.6);
}
.taux-moyen-value {
  font-size: 26px;
  font-weight: 700;
  color: #7dd3fc;
}

.filter-actions { display: flex; gap: 8px; align-items: flex-end; }

/* Badge ID session — style indigo */
.id-badge {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  background: #eef2ff;
  color: #4338ca;
  padding: 3px 8px;
  border-radius: 6px;
  font-weight: 600;
  letter-spacing: 0.02em;
  white-space: nowrap;
}

/* Barre de progression taux */
.taux-cell { display: flex; align-items: center; gap: 8px; }
.taux-bar-bg {
  width: 80px;
  height: 6px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}
.taux-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}
.taux-bar--green  { background: var(--color-success); }
.taux-bar--orange { background: var(--color-warning); }
.taux-bar--red    { background: var(--color-error); }

.taux-pct { font-size: 12px; font-weight: 600; color: var(--color-text); white-space: nowrap; }

.ecarts-nonzero { color: #d97706; font-weight: 600; font-size: 13px; }
.ecarts-zero    { color: var(--color-text-muted); font-size: 13px; }
</style>
