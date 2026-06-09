<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Écarts détectés</h1>
        <p class="page-subtitle">{{ store.total }} écart(s) correspondant aux filtres</p>
      </div>
      <button class="btn btn-secondary" @click="exportExcel">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:16px;height:16px"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" /></svg>
        Export Excel
      </button>
    </div>

    <!-- Filtres -->
    <div class="filters-bar">
      <div class="form-group">
        <label class="form-label">Type de flux</label>
        <select v-model="store.filters.type_flux" class="form-control">
          <option value="">Tous</option>
          <option>MB→CBS</option><option>CBS→PI</option><option>PI→MB</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Criticité</label>
        <select v-model="store.filters.criticite" class="form-control">
          <option value="">Toutes</option>
          <option>Critique</option><option>Important</option><option>Faible</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Statut</label>
        <select v-model="store.filters.statut" class="form-control">
          <option value="">Tous</option>
          <option>À TRAITER</option><option>EN COURS</option><option>RÉSOLUS</option>
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

    <!-- Tableau -->
    <div class="card">
      <div v-if="store.loading" class="loading-state"><div class="spinner" />Chargement…</div>
      <template v-else>
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>CODE</th><th>TYPE FLUX</th><th>DATE</th><th>SESSION</th>
                <th>COMPTE</th><th>MONTANT</th><th>CRITICITÉ</th><th>STATUT</th><th>ACTION</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!store.list.length"><td colspan="9"><div class="empty-state">Aucun écart trouvé.</div></td></tr>
              <tr v-for="e in store.list" :key="e.id">
                <td class="mono">{{ e.code }}</td>
                <td><span class="flux-badge">{{ e.type_flux }}</span></td>
                <td class="text-sm">{{ formatDateOnly(e.date) }}</td>
                <td class="mono text-sm">{{ e.session_id }}</td>
                <td class="mono text-sm">{{ e.compte }}</td>
                <td class="amount">{{ formatAmount(e.montant) }}</td>
                <td><CriticalityBadge :criticite="e.criticite" /></td>
                <td><StatusBadge :status="e.statut" /></td>
                <td><button class="btn btn-secondary btn-sm" @click="openDetail(e)">Détail</button></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination">
          <span>{{ store.total }} résultat(s)</span>
          <div class="pagination-controls">
            <button class="page-btn" :disabled="store.page === 1" @click="changePage(store.page - 1)">‹</button>
            <button v-for="p in totalPages" :key="p" class="page-btn" :class="{ active: p === store.page }" @click="changePage(p)">{{ p }}</button>
            <button class="page-btn" :disabled="store.page === totalPages" @click="changePage(store.page + 1)">›</button>
          </div>
        </div>
      </template>
    </div>

    <!-- ───── MODALE DÉTAIL ÉCART ───── -->
    <AppModal v-model="showDetailModal" :title="`Détail de l'écart ${selected?.code ?? ''}`" width="580px">
      <template #header-extra v-if="selected">
        <CriticalityBadge :criticite="selected.criticite" />
        <StatusBadge :status="selected.statut" />
      </template>

      <template v-if="selected">
        <div class="modal-cols">
          <!-- Colonne gauche -->
          <div class="modal-col">
            <p class="col-title">Informations générales</p>

            <div class="field-list">
              <div class="field-row"><span>Code écart</span><span class="mono">{{ selected.code }}</span></div>
              <div class="field-row"><span>Flux de données</span><span class="flux-badge">{{ selected.type_flux }}</span></div>
              <div class="field-row"><span>Date de constatation</span><span>{{ formatDate(selected.date) }}</span></div>
              <div class="field-row"><span>Session</span><span class="mono">{{ selected.session_id }}</span></div>
            </div>

            <!-- Étape échouée -->
            <div class="etape-box">
              <div class="etape-header">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:15px;height:15px;flex-shrink:0"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>
                Étape échouée : <strong>{{ selected.etape_echouee }}</strong>
              </div>
              <p class="etape-msg">{{ selected.message_echouee }}</p>
            </div>

            <!-- Montant mis en valeur -->
            <div class="montant-block">
              <span class="montant-label">Montant de l'écart</span>
              <span class="montant-value">{{ formatAmount(selected.montant) }}</span>
            </div>
          </div>

          <!-- Séparateur vertical -->
          <div class="col-divider" />

          <!-- Colonne droite -->
          <div class="modal-col">
            <p class="col-title">Détails techniques</p>

            <div class="field-list">
              <div class="field-row">
                <span>Compte débiteur</span>
                <div class="copyable">
                  <span class="mono">{{ selected.compte_debiteur }}</span>
                  <button class="copy-btn" @click="copyText(selected.compte_debiteur, 'debiteur')" :title="'Copier'">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:13px;height:13px"><path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184" /></svg>
                    <span v-if="copied === 'debiteur'" class="copy-tip">Copié !</span>
                  </button>
                </div>
              </div>
              <div class="field-row">
                <span>Compte créditeur</span>
                <div class="copyable">
                  <span class="mono">{{ selected.compte_crediteur }}</span>
                  <button class="copy-btn" @click="copyText(selected.compte_crediteur, 'crediteur')" :title="'Copier'">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:13px;height:13px"><path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184" /></svg>
                    <span v-if="copied === 'crediteur'" class="copy-tip">Copié !</span>
                  </button>
                </div>
              </div>
              <div class="field-row"><span>Message ID</span><span class="mono">{{ selected.message_id }}</span></div>
              <div class="field-row"><span>E2E ID</span><span class="mono">{{ selected.e2e_id }}</span></div>
              <div class="field-row"><span>Horodatage serveur</span><span>{{ formatDate(selected.date) }}</span></div>
            </div>

            <!-- Historique -->
            <div class="historique-section">
              <p class="col-title" style="margin-top:14px">Historique</p>
              <div v-if="!selected.historique?.length" class="historique-empty">
                Aucune action n'a été effectuée sur cet écart.
              </div>
              <div v-else class="mini-timeline">
                <div v-for="(h, i) in selected.historique" :key="i" class="mini-tl-item">
                  <div class="mini-tl-dot" />
                  <div class="mini-tl-body">
                    <span class="mini-tl-action">{{ h.action }}</span>
                    <span class="mini-tl-meta">{{ h.auteur }} · {{ formatDate(h.date) }}</span>
                    <p class="mini-tl-detail">{{ h.detail }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <template #footer>
        <button class="btn btn-secondary" @click="showDetailModal = false">Fermer</button>
        <button
          class="btn btn-primary"
          :disabled="selected?.statut !== 'À TRAITER'"
          :title="selected?.statut !== 'À TRAITER' ? `Disponible uniquement pour les écarts À TRAITER (statut actuel : ${selected?.statut})` : ''"
          @click="goAnnotate"
        >
          Prendre en charge
        </button>
      </template>
    </AppModal>

    <!-- ───── MODALE PRENDRE EN CHARGE ───── -->
    <AppModal v-model="showAnnotateModal" :title="`Prise en charge — ${selected?.code ?? ''}`" width="520px">
      <template v-if="selected">
        <!-- Rappel contexte -->
        <div class="annotate-context">
          <div class="ac-item">
            <span class="ac-label">Code</span>
            <span class="ac-code mono">{{ selected.code }}</span>
          </div>
          <div class="ac-divider" />
          <div class="ac-item">
            <span class="ac-label">Criticité</span>
            <CriticalityBadge :criticite="selected.criticite" />
          </div>
          <div class="ac-divider" />
          <div class="ac-item">
            <span class="ac-label">Montant</span>
            <span class="ac-value-big">{{ formatAmount(selected.montant) }}</span>
          </div>
        </div>

        <div class="annotate-form">
          <div class="form-group">
            <label class="form-label">Nouveau statut <span class="required">*</span></label>
            <div class="statut-radio-group">
              <label v-for="opt in STATUT_OPTIONS" :key="opt.value" class="statut-radio"
                :class="{ selected: annotationForm.statut === opt.value }">
                <input type="radio" v-model="annotationForm.statut" :value="opt.value" />
                <StatusBadge :status="opt.value" />
                <span class="radio-hint">{{ opt.hint }}</span>
              </label>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">
              Commentaire <span class="required">*</span>
              <span class="char-counter" :class="{ 'counter-warn': annotationForm.commentaire.length > 450 }">
                {{ annotationForm.commentaire.length }}/500
              </span>
            </label>
            <textarea
              v-model="annotationForm.commentaire"
              class="form-control"
              rows="5"
              maxlength="500"
              placeholder="Décrivez les actions prises, les vérifications effectuées ou la raison de ce changement de statut…"
            />
          </div>

          <div class="form-error" v-if="annotateError">{{ annotateError }}</div>
        </div>
      </template>

      <template #footer-note>
        <div class="ct06-warning">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:14px;height:14px;flex-shrink:0">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          Cette action sera enregistrée de manière immuable (CT-06)
        </div>
      </template>

      <template #footer>
        <button class="btn btn-secondary" @click="backToDetail">Annuler</button>
        <button
          class="btn btn-primary"
          :disabled="!canSubmit || annotating"
          @click="confirmerAnnotation"
        >
          <span v-if="annotating" class="spinner-sm" />
          Confirmer la prise en charge
        </button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useEcartsStore } from '@/stores/ecarts'
import StatusBadge from '@/components/common/StatusBadge.vue'
import CriticalityBadge from '@/components/common/CriticalityBadge.vue'
import AppModal from '@/components/common/AppModal.vue'
import { formatDate, formatDateOnly, formatAmount } from '@/utils/format'

const store = useEcartsStore()
const showDetailModal   = ref(false)
const showAnnotateModal = ref(false)
const selected  = ref(null)
const annotating = ref(false)
const annotateError = ref('')
const copied = ref('')
const annotationForm = reactive({ statut: '', commentaire: '' })

const STATUT_OPTIONS = [
  { value: 'EN COURS', hint: 'Traitement en cours' },
  { value: 'RÉSOLU',   hint: 'Écart résolu' },
  { value: 'IGNORÉ',   hint: 'Classé sans suite' }
]

const totalPages = computed(() => Math.max(1, Math.ceil(store.total / store.pageSize)))
const canSubmit  = computed(() => annotationForm.statut !== '' && annotationForm.commentaire.trim().length >= 10)

onMounted(() => store.fetchList())
function applyFilters() { store.page = 1; store.fetchList() }
function changePage(p) { if (p < 1 || p > totalPages.value) return; store.page = p; store.fetchList() }
function resetFilters() {
  store.filters = { type_flux: '', criticite: '', statut: '', date_debut: '', date_fin: '' }
  store.page = 1; store.fetchList()
}

function openDetail(e) {
  selected.value = e
  annotationForm.statut = ''
  annotationForm.commentaire = ''
  annotateError.value = ''
  showDetailModal.value = true
}

function goAnnotate() {
  showDetailModal.value = false
  showAnnotateModal.value = true
}

function backToDetail() {
  showAnnotateModal.value = false
  showDetailModal.value = true
}

async function confirmerAnnotation() {
  if (!canSubmit.value) return
  annotateError.value = ''
  annotating.value = true
  try {
    const ok = await store.prendreEnCharge(selected.value.id, {
      statut: annotationForm.statut,
      commentaire: annotationForm.commentaire
    })
    if (ok) { showAnnotateModal.value = false }
    else { annotateError.value = 'Erreur lors de la soumission. Réessayez.' }
  } finally { annotating.value = false }
}

async function copyText(text, field) {
  try {
    await navigator.clipboard.writeText(text)
    copied.value = field
    setTimeout(() => { copied.value = '' }, 1500)
  } catch {}
}

function exportExcel() { alert('Export Excel en cours de génération…') }
</script>

<style scoped>
.filter-actions { display: flex; gap: 8px; align-items: flex-end; }
.mono   { font-family: 'Courier New', monospace; font-size: 12px; }
.amount { font-weight: 500; }
.flux-badge { display: inline-block; padding: 2px 8px; background: #f1f5f9; border-radius: 4px; font-size: 12px; font-weight: 600; font-family: monospace; color: var(--color-primary); }

/* ─── Layout 2 colonnes modal ─── */
.modal-cols {
  display: grid;
  grid-template-columns: 1fr 1px 1fr;
  gap: 0;
  min-height: 280px;
}
.modal-col { padding: 4px 0; }
.modal-col:first-child { padding-right: 20px; }
.modal-col:last-child  { padding-left: 20px; }
.col-divider { background: var(--color-border); margin: 0 4px; }
.col-title {
  font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em;
  color: var(--color-text-muted); margin-bottom: 12px;
}

.field-list { display: flex; flex-direction: column; gap: 0; }
.field-row {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 8px;
  padding: 7px 0; border-bottom: 1px solid #f8fafc; font-size: 13px;
}
.field-row:last-child { border-bottom: none; }
.field-row > span:first-child { color: var(--color-text-muted); flex-shrink: 0; min-width: 110px; }

/* Étape échouée */
.etape-box {
  margin-top: 14px; background: #fff5f5; border: 1px solid #fecaca;
  border-radius: 8px; padding: 10px 12px;
}
.etape-header {
  display: flex; align-items: center; gap: 6px;
  font-size: 12.5px; color: var(--color-error); font-weight: 500; margin-bottom: 5px;
}
.etape-msg { font-size: 12px; color: #7f1d1d; line-height: 1.5; }

/* Montant */
.montant-block {
  margin-top: 14px; padding: 12px 14px;
  background: linear-gradient(135deg, #f0f4ff 0%, #e8ecf8 100%);
  border-radius: 8px; border-left: 3px solid var(--color-primary);
}
.montant-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--color-text-muted); display: block; margin-bottom: 4px; }
.montant-value { font-size: 22px; font-weight: 700; color: var(--color-primary); display: block; }

/* Copier */
.copyable { display: flex; align-items: center; gap: 5px; }
.copy-btn {
  background: none; border: none; cursor: pointer; padding: 3px; border-radius: 4px;
  color: var(--color-text-muted); display: flex; align-items: center; position: relative;
  transition: color 0.15s;
}
.copy-btn:hover { color: var(--color-primary); background: #f1f5f9; }
.copy-tip {
  position: absolute; right: 0; bottom: 100%; margin-bottom: 2px;
  background: var(--color-success); color: #fff;
  font-size: 11px; font-weight: 600; padding: 2px 6px; border-radius: 4px; white-space: nowrap;
}

/* Historique mini-timeline */
.historique-section { margin-top: 4px; }
.historique-empty {
  font-size: 12.5px; color: var(--color-text-muted); font-style: italic;
  padding: 8px 0;
}
.mini-timeline { display: flex; flex-direction: column; gap: 0; }
.mini-tl-item { display: flex; gap: 10px; padding-bottom: 12px; position: relative; }
.mini-tl-item::before {
  content: ''; position: absolute; left: 5px; top: 14px; bottom: 0;
  width: 1px; background: var(--color-border);
}
.mini-tl-item:last-child::before { display: none; }
.mini-tl-dot {
  width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0;
  background: var(--color-primary); border: 2px solid #fff;
  box-shadow: 0 0 0 2px var(--color-primary); margin-top: 2px;
}
.mini-tl-body { flex: 1; }
.mini-tl-action { font-size: 13px; font-weight: 600; color: var(--color-text); display: block; }
.mini-tl-meta   { font-size: 11px; color: var(--color-text-muted); display: block; margin: 2px 0; }
.mini-tl-detail { font-size: 12px; color: #475569; line-height: 1.4; margin: 0; }

/* ─── Modal Prendre en charge ─── */
.annotate-context {
  display: flex; align-items: center; gap: 0;
  background: #f8fafc; border: 1px solid var(--color-border);
  border-radius: 8px; padding: 14px 18px; margin-bottom: 20px;
}
.ac-item  { display: flex; flex-direction: column; align-items: flex-start; gap: 4px; flex: 1; }
.ac-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--color-text-muted); }
.ac-value-big { font-size: 18px; font-weight: 700; color: var(--color-primary); }
.ac-code { font-family: 'Courier New', monospace; font-size: 14px; font-weight: 600; color: var(--color-primary); }
.ac-divider { width: 1px; background: var(--color-border); height: 40px; margin: 0 18px; }

.annotate-form { display: flex; flex-direction: column; gap: 18px; }

.statut-radio-group { display: flex; gap: 10px; margin-top: 6px; flex-wrap: wrap; }
.statut-radio {
  display: flex; align-items: center; gap: 8px; cursor: pointer;
  padding: 8px 12px; border: 1.5px solid var(--color-border);
  border-radius: 8px; transition: all 0.15s;
  flex-direction: column; align-items: flex-start;
}
.statut-radio input[type=radio] { display: none; }
.statut-radio.selected { border-color: var(--color-primary); background: #f0f4ff; }
.statut-radio:hover { border-color: #94a3b8; }
.radio-hint { font-size: 11px; color: var(--color-text-muted); }

.char-counter {
  float: right; font-size: 11px; font-weight: 400;
  color: var(--color-text-muted); margin-left: 8px;
}
.counter-warn { color: var(--color-warning); }

.required { color: var(--color-error); }
.form-error { padding: 10px 14px; background: var(--color-error-bg); color: var(--color-error); border-radius: 8px; font-size: 13px; }

.spinner-sm {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.ct06-warning {
  display: flex; align-items: center; gap: 7px;
  font-size: 12px; font-weight: 500; color: var(--color-warning);
}
</style>
