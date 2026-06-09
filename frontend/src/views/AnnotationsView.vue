<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Historique des annotations</h1>
        <p class="page-subtitle">Suivi des prises en charge sur les écarts détectés</p>
      </div>
      <label class="toggle-switch">
        <input type="checkbox" v-model="store.mineOnly" @change="refresh" />
        <span class="toggle-slider" />
        <span class="toggle-label">Mes annotations uniquement</span>
      </label>
    </div>

    <!-- Compteurs -->
    <div class="grid-3 mb-6">
      <div class="counter-card counter-blue">
        <span class="counter-value">{{ store.counters.EN_COURS }}</span>
        <span class="counter-label">EN COURS</span>
      </div>
      <div class="counter-card counter-green">
        <span class="counter-value">{{ store.counters.RESOLUS }}</span>
        <span class="counter-label">RÉSOLUS</span>
      </div>
      <div class="counter-card counter-gray">
        <span class="counter-value">{{ store.counters.IGNORE }}</span>
        <span class="counter-label">IGNORÉS</span>
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
                <th>CODE ÉCART</th><th>ID SESSION</th><th>DATE DE PRISE EN CHARGE</th>
                <th>ANALYSTE</th><th>TYPE FLUX</th><th>STATUT</th><th>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!store.list.length"><td colspan="7"><div class="empty-state">Aucune annotation.</div></td></tr>
              <tr v-for="a in store.list" :key="a.id">
                <td class="mono">{{ a.ecart_code }}</td>
                <td class="mono text-sm">{{ a.session_id }}</td>
                <td class="text-sm">{{ formatDate(a.date) }}</td>
                <td>
                  <div class="analyst-cell">
                    <div class="analyst-avatar">{{ initials(a.analyste) }}</div>
                    {{ a.analyste }}
                  </div>
                </td>
                <td><span class="flux-badge">{{ a.type_flux }}</span></td>
                <td><StatusBadge :status="a.statut" /></td>
                <td><button class="btn btn-secondary btn-sm" @click="openDetail(a)">Voir le détail</button></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination">
          <span>{{ store.total }} annotation(s)</span>
          <div class="pagination-controls">
            <button class="page-btn" :disabled="store.page === 1" @click="changePage(store.page - 1)">‹</button>
            <button v-for="p in totalPages" :key="p" class="page-btn" :class="{ active: p === store.page }" @click="changePage(p)">{{ p }}</button>
            <button class="page-btn" :disabled="store.page === totalPages" @click="changePage(store.page + 1)">›</button>
          </div>
        </div>
      </template>
    </div>

    <!-- ───── MODALE DÉTAIL ANNOTATION ───── -->
    <AppModal v-model="showModal" title="Détail de l'annotation" width="580px">
      <template #header-extra v-if="selected">
        <StatusBadge :status="selected.statut" />
      </template>

      <template v-if="selected">
        <div class="modal-cols">
          <!-- Colonne gauche -->
          <div class="modal-col">
            <p class="col-title">Informations de l'annotation</p>

            <div class="field-list">
              <div class="field-row"><span>Code écart</span><span class="mono">{{ selected.ecart_code }}</span></div>
              <div class="field-row"><span>Session</span><span class="mono">{{ selected.session_id }}</span></div>
              <div class="field-row"><span>Type de flux</span><span class="flux-badge">{{ selected.type_flux }}</span></div>
              <div class="field-row"><span>Criticité</span><CriticalityBadge :criticite="selected.criticite" /></div>

              <!-- Changement de statut -->
              <div class="field-row statut-flow-row">
                <span>Changement statut</span>
                <div class="statut-flow">
                  <StatusBadge :status="selected.statut_precedent" />
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px;color:#94a3b8;flex-shrink:0">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                  </svg>
                  <StatusBadge :status="selected.statut" />
                </div>
              </div>

              <div class="field-row"><span>Date action</span><span>{{ formatDate(selected.date) }}</span></div>
              <div class="field-row"><span>Auteur</span>
                <div class="analyst-cell">
                  <div class="analyst-avatar sm">{{ initials(selected.analyste) }}</div>
                  {{ selected.analyste }}
                </div>
              </div>
            </div>

            <div class="commentaire-block">
              <p class="col-title" style="margin-top:14px">Commentaire</p>
              <p class="commentaire-text">{{ selected.commentaire }}</p>
            </div>
          </div>

          <!-- Séparateur -->
          <div class="col-divider" />

          <!-- Colonne droite -->
          <div class="modal-col" v-if="selected.transaction_concernee">
            <p class="col-title">Transaction concernée</p>

            <div class="field-list">
              <div class="field-row"><span>ID Transaction</span><span class="mono">{{ selected.transaction_concernee.id }}</span></div>
              <div class="field-row">
                <span>Montant</span>
                <strong class="txn-amount">{{ formatAmount(selected.transaction_concernee.montant) }}</strong>
              </div>
              <div class="field-row"><span>End-to-End ID</span><span class="mono">{{ selected.transaction_concernee.e2e_id }}</span></div>
              <div class="field-row"><span>Message ID</span><span class="mono">{{ selected.transaction_concernee.message_id }}</span></div>
              <div class="field-row"><span>Compte débiteur</span><span class="mono">{{ selected.transaction_concernee.compte_debit }}</span></div>
              <div class="field-row"><span>Compte créditeur</span><span class="mono">{{ selected.transaction_concernee.compte_credit }}</span></div>
              <div class="field-row"><span>Date & Heure</span><span>{{ formatDate(selected.transaction_concernee.date) }}</span></div>
              <div class="field-row"><span>Statut</span><StatusBadge :status="selected.transaction_concernee.statut" /></div>
            </div>
          </div>

          <div class="modal-col no-txn" v-else>
            <p class="col-title">Transaction concernée</p>
            <p class="text-muted text-sm">Aucune transaction associée.</p>
          </div>
        </div>
      </template>

      <!-- Note CT-06 en pied de modale -->
      <template #footer-note v-if="selected">
        <div class="ct06-note">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:14px;height:14px;flex-shrink:0">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
          </svg>
          Enregistrement immuable — CT-06
          <span class="ct06-sep">·</span>
          Horodatage : {{ selected ? formatDate(selected.date) : '' }}
        </div>
      </template>

      <template #footer>
        <button class="btn btn-primary footer-center" @click="showModal = false">Fermer</button>
      </template>
    </AppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAnnotationsStore } from '@/stores/annotations'
import StatusBadge from '@/components/common/StatusBadge.vue'
import CriticalityBadge from '@/components/common/CriticalityBadge.vue'
import AppModal from '@/components/common/AppModal.vue'
import { formatDate, formatAmount } from '@/utils/format'

const store = useAnnotationsStore()
const showModal = ref(false)
const selected = ref(null)
const totalPages = computed(() => Math.max(1, Math.ceil(store.total / store.pageSize)))

onMounted(() => store.fetchList())
function refresh()  { store.page = 1; store.fetchList() }
function changePage(p) { if (p < 1 || p > totalPages.value) return; store.page = p; store.fetchList() }
function openDetail(a) { selected.value = a; showModal.value = true }
function initials(name) { return name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) ?? 'U' }
</script>

<style scoped>
.toggle-switch { display: flex; align-items: center; gap: 10px; cursor: pointer; }
.toggle-switch input { display: none; }
.toggle-slider { width: 40px; height: 22px; background: #e2e8f0; border-radius: 11px; position: relative; transition: background 0.2s; }
.toggle-slider::after { content: ''; position: absolute; top: 3px; left: 3px; width: 16px; height: 16px; background: #fff; border-radius: 50%; transition: transform 0.2s; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }
.toggle-switch input:checked + .toggle-slider { background: var(--color-primary); }
.toggle-switch input:checked + .toggle-slider::after { transform: translateX(18px); }
.toggle-label { font-size: 13px; font-weight: 500; color: var(--color-text); }

.counter-card { background: #fff; border-radius: var(--radius); box-shadow: var(--shadow); padding: 20px 24px; display: flex; flex-direction: column; align-items: center; gap: 6px; border-top: 4px solid; }
.counter-blue  { border-color: var(--color-info); }
.counter-green { border-color: var(--color-success); }
.counter-gray  { border-color: #94a3b8; }
.counter-value { font-size: 36px; font-weight: 700; color: var(--color-text); }
.counter-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--color-text-muted); }

.mono { font-family: 'Courier New', monospace; font-size: 12px; }
.flux-badge { display: inline-block; padding: 2px 8px; background: #f1f5f9; border-radius: 4px; font-size: 12px; font-weight: 600; font-family: monospace; color: var(--color-primary); }
.analyst-cell { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.analyst-avatar { width: 28px; height: 28px; border-radius: 50%; background: var(--color-primary); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; flex-shrink: 0; }
.analyst-avatar.sm { width: 22px; height: 22px; font-size: 10px; }

/* ─── Layout 2 colonnes modal ─── */
.modal-cols { display: grid; grid-template-columns: 1fr 1px 1fr; gap: 0; min-height: 260px; }
.modal-col { padding: 4px 0; }
.modal-col:first-child { padding-right: 20px; }
.modal-col:last-child  { padding-left: 20px; }
.col-divider { background: var(--color-border); margin: 0 4px; }
.col-title { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--color-text-muted); margin-bottom: 12px; }
.no-txn { display: flex; flex-direction: column; }

.field-list { display: flex; flex-direction: column; }
.field-row {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 8px;
  padding: 6px 0; border-bottom: 1px solid #f8fafc; font-size: 13px;
}
.field-row:last-child { border-bottom: none; }
.field-row > span:first-child { color: var(--color-text-muted); flex-shrink: 0; min-width: 100px; }

.statut-flow-row { align-items: center; }
.statut-flow { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }

.txn-amount { font-size: 16px; font-weight: 700; color: var(--color-primary); }

.commentaire-block { margin-top: 4px; }
.commentaire-text {
  font-size: 13px; line-height: 1.6; color: var(--color-text);
  background: #f8fafc; padding: 10px 12px; border-radius: 6px;
  border-left: 3px solid var(--color-primary); margin: 0;
}

/* CT-06 footer note */
.ct06-note {
  display: flex; align-items: center; gap: 7px;
  font-size: 12px; font-weight: 500; color: var(--color-success);
}
.ct06-sep { opacity: 0.4; }

/* Bouton Fermer centré */
.footer-center { margin: 0 auto; min-width: 120px; justify-content: center; }
</style>
