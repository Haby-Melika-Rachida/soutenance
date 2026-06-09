<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Journaux d'audit</h1>
        <p class="page-subtitle">Traçabilité chronologique de toutes les actions système — lecture seule</p>
      </div>
    </div>

    <!-- Filtres -->
    <div class="filters-bar">
      <div class="form-group">
        <label class="form-label">Utilisateur</label>
        <input v-model="store.filters.utilisateur" type="text" class="form-control" placeholder="Username…" />
      </div>
      <div class="form-group">
        <label class="form-label">Type d'action</label>
        <select v-model="store.filters.action" class="form-control">
          <option value="">Toutes les actions</option>
          <option v-for="a in ACTION_TYPES" :key="a" :value="a">{{ a }}</option>
        </select>
      </div>
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
                <th>DATE &amp; HEURE</th>
                <th>UTILISATEUR</th>
                <th>ACTION</th>
                <th>ENTITÉ</th>
                <th>ID ENTITÉ</th>
                <th>ADRESSE IP</th>
                <th>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!store.list.length">
                <td colspan="7"><div class="empty-state">Aucune entrée d'audit.</div></td>
              </tr>
              <tr v-for="entry in store.list" :key="entry.id">
                <td class="date-cell text-sm">{{ formatDate(entry.date) }}</td>
                <td>
                  <div class="user-cell">
                    <div class="user-dot">{{ entry.utilisateur[0].toUpperCase() }}</div>
                    <span class="mono">{{ entry.utilisateur }}</span>
                  </div>
                </td>
                <td>
                  <span class="action-badge" :class="actionClass(entry.action)">
                    {{ entry.action }}
                  </span>
                </td>
                <td class="text-sm">{{ entry.entite }}</td>
                <td class="mono text-sm">{{ entry.id_entite }}</td>
                <td class="mono text-sm text-muted">{{ entry.ip }}</td>
                <td>
                  <button class="btn btn-secondary btn-sm" @click="openDetail(entry)">Détail</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="pagination">
          <span>Affichage de {{ store.list.length }} sur {{ store.total }} entrées</span>
          <div class="pagination-controls">
            <button class="page-btn" :disabled="store.page === 1" @click="changePage(store.page - 1)">‹</button>
            <button v-for="p in totalPages" :key="p" class="page-btn" :class="{ active: p === store.page }" @click="changePage(p)">{{ p }}</button>
            <button class="page-btn" :disabled="store.page === totalPages" @click="changePage(store.page + 1)">›</button>
          </div>
        </div>
      </template>
    </div>

    <!-- ── MODALE DÉTAIL AUDIT ── -->
    <AppModal v-model="showDetailModal" title="Détail de l'action" width="520px">
      <template #header-extra v-if="selectedEntry">
        <span class="action-badge" :class="actionClass(selectedEntry.action)">{{ selectedEntry.action }}</span>
      </template>

      <template v-if="selectedEntry">
        <!-- Section 1 : Qui & Quand -->
        <p class="section-title">Qui &amp; Quand</p>
        <div class="detail-grid">
          <div class="detail-row">
            <span class="detail-label">Utilisateur</span>
            <span>{{ selectedEntry.utilisateur }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Date &amp; heure</span>
            <span>{{ formatDate(selectedEntry.date) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Adresse IP</span>
            <span class="mono">{{ selectedEntry.ip }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Session navigateur</span>
            <span class="text-muted">Firefox 125 — Windows 10</span>
          </div>
        </div>

        <!-- Section 2 : Action effectuée -->
        <p class="section-title" style="margin-top:16px">Action effectuée</p>
        <div class="detail-grid">
          <div class="detail-row">
            <span class="detail-label">Type d'action</span>
            <span class="action-badge" :class="actionClass(selectedEntry.action)">{{ selectedEntry.action }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Entité touchée</span>
            <span>{{ selectedEntry.entite }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Identifiant</span>
            <span class="mono">{{ selectedEntry.id_entite }}</span>
          </div>
        </div>
        <div class="detail-code">{{ selectedEntry.detail }}</div>

        <!-- Section 3 : Traçabilité -->
        <p class="section-title" style="margin-top:16px">Traçabilité</p>
        <div class="detail-grid">
          <div class="detail-row">
            <span class="detail-label">ID d'audit</span>
            <span class="mono">AUD-{{ String(selectedEntry.id).padStart(5, '0') }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Horodatage serveur</span>
            <span>{{ formatDate(selectedEntry.date) }} UTC</span>
          </div>
        </div>

        <div class="immuable-note">🔒 Entrée immuable — non modifiable</div>
      </template>

      <template #footer>
        <button class="btn btn-primary" style="margin:0 auto;display:block" @click="showDetailModal = false">
          Fermer
        </button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuditStore, ACTION_TYPES } from '@/stores/audit'
import AppModal from '@/components/common/AppModal.vue'
import { formatDate } from '@/utils/format'

const store = useAuditStore()
const totalPages = computed(() => Math.max(1, Math.ceil(store.total / store.pageSize)))

const showDetailModal = ref(false)
const selectedEntry   = ref(null)

onMounted(() => store.fetchList())

function applyFilters() { store.page = 1; store.fetchList() }
function changePage(p) { if (p < 1 || p > totalPages.value) return; store.page = p; store.fetchList() }
function resetFilters() {
  store.filters = { utilisateur: '', action: '', date_debut: '', date_fin: '' }
  store.page = 1; store.fetchList()
}

function openDetail(entry) {
  selectedEntry.value = entry
  showDetailModal.value = true
}

function actionClass(action) {
  if (action === 'CONNEXION')          return 'action-neutral'
  if (action === 'ANNOTATION')         return 'action-annotation'
  if (action === 'BATCH EXÉCUTÉ')      return 'action-batch'
  if (action === 'MODIFICATION CONFIG')return 'action-config'
  if (action === 'CRÉATION USER')      return 'action-user-create'
  return 'action-neutral'
}
</script>

<style scoped>
.filter-actions { display: flex; gap: 8px; align-items: flex-end; }
.mono { font-family: 'Courier New', monospace; font-size: 12px; }
.date-cell { white-space: nowrap; }

.user-cell { display: flex; align-items: center; gap: 8px; }
.user-dot {
  width: 26px; height: 26px; border-radius: 50%; background: var(--color-primary); color: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex-shrink: 0;
}

.action-badge {
  display: inline-block; padding: 3px 9px; border-radius: 4px;
  font-size: 12px; font-weight: 600; white-space: nowrap;
}
.action-neutral    { background: #f1f5f9; color: #475569; }
.action-annotation { background: #dbeafe; color: #1d4ed8; }
.action-batch      { background: #f0fdf4; color: #15803d; }
.action-config     { background: #fff7ed; color: #c2410c; }
.action-user-create{ background: #fdf4ff; color: #7c3aed; }

/* Modale détail */
.section-title {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.06em; color: var(--color-text-muted); margin-bottom: 8px;
}
.detail-grid { display: flex; flex-direction: column; }
.detail-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 7px 0; border-bottom: 1px solid #f8fafc; font-size: 13px;
}
.detail-row:last-child { border-bottom: none; }
.detail-label { color: var(--color-text-muted); flex-shrink: 0; min-width: 140px; }

.detail-code {
  margin-top: 10px; padding: 10px 12px;
  background: #f8fafc; border: 1px solid var(--color-border);
  border-radius: 6px; font-family: 'Courier New', monospace;
  font-size: 12px; line-height: 1.6; color: var(--color-text);
}

.immuable-note {
  margin-top: 14px; padding: 8px 12px;
  background: #f0f4ff; border: 1px solid #c7d2fe;
  border-radius: 6px; font-size: 12px; font-weight: 500; color: #4338ca;
  text-align: center;
}
</style>
