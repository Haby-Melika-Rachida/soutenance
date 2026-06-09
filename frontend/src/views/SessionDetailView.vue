<template>
  <div>
    <div class="page-header">
      <div>
        <router-link to="/sessions" class="back-link">← Retour à l'historique</router-link>
        <h1 class="page-title">Session {{ route.params.id }}</h1>
      </div>
      <div class="flex gap-2">
        <button class="btn btn-secondary" @click="exportExcel">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:16px;height:16px"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" /></svg>
          Export Excel
        </button>
        <button class="btn btn-secondary" @click="exportPdf">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:16px;height:16px"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /></svg>
          Export PDF
        </button>
      </div>
    </div>

    <div v-if="store.loadingDetail" class="loading-state card"><div class="spinner" />Chargement…</div>

    <template v-else-if="store.detail">
      <!-- En-tête métriques + donut -->
      <div class="detail-header mb-6">
        <div class="card donut-card">
          <h2 class="card-title mb-4">Répartition des transactions</h2>
          <div class="donut-wrapper">
            <div class="donut-canvas-wrap"><canvas ref="donutCanvas" /></div>
            <div class="donut-stats">
              <div class="donut-metric">
                <span class="dm-value">{{ store.detail.taux_lettrage?.toFixed(1) }} %</span>
                <span class="dm-label">Taux de lettrage</span>
              </div>
              <div class="donut-metric">
                <span class="dm-value">{{ store.detail.nb_transactions?.toLocaleString('fr-FR') }}</span>
                <span class="dm-label">Opérations total</span>
              </div>
              <div class="donut-metric warn">
                <span class="dm-value">{{ store.detail.nb_ecarts }}</span>
                <span class="dm-label">Écarts détectés</span>
              </div>
              <div class="donut-legend">
                <div class="leg-item"><span class="leg-dot" style="background:#0d2b5e"/>Lettrées ({{ store.detail.nb_lettrees?.toLocaleString('fr-FR') }})</div>
                <div class="leg-item"><span class="leg-dot" style="background:#f97316"/>Écarts ({{ store.detail.nb_ecarts }})</div>
              </div>
            </div>
          </div>
        </div>

        <div class="card info-card">
          <h2 class="card-title mb-4">Informations</h2>
          <div class="info-rows">
            <div class="info-row"><span>Identifiant</span><span class="mono">{{ store.detail.id }}</span></div>
            <div class="info-row"><span>Statut</span><StatusBadge :status="store.detail.statut" /></div>
            <div class="info-row"><span>Date d'exécution</span><span>{{ formatDate(store.detail.date) }}</span></div>
            <div class="info-row"><span>Transactions lettrées</span><span class="val-success">{{ store.detail.nb_lettrees?.toLocaleString('fr-FR') }}</span></div>
            <div class="info-row"><span>Transactions non lettrées</span><span class="val-warning">{{ store.detail.nb_ecarts }}</span></div>
          </div>
        </div>
      </div>

      <!-- Onglets -->
      <div class="card">
        <div class="tabs mb-4">
          <button class="tab-btn" :class="{ active: tab === 'ecarts' }" @click="tab = 'ecarts'">
            Écarts détectés ({{ store.detail.ecarts?.length ?? 0 }})
          </button>
          <button class="tab-btn" :class="{ active: tab === 'transactions' }" @click="tab = 'transactions'">
            Transactions traitées ({{ store.detail.transactions?.length ?? 0 }})
          </button>
        </div>

        <!-- Onglet Écarts -->
        <div v-if="tab === 'ecarts'" class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>CODE</th>
                <th>TYPE FLUX</th>
                <th>DATE</th>
                <th>SESSION</th>
                <th>COMPTE</th>
                <th>MONTANT</th>
                <th>CRITICITÉ</th>
                <th>STATUT</th>
                <th>ACTION</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!store.detail.ecarts?.length"><td colspan="9" class="empty-state">Aucun écart.</td></tr>
              <tr v-for="e in store.detail.ecarts" :key="e.code">
                <td class="mono">{{ e.code }}</td>
                <td><span class="flux-badge">{{ e.type_flux }}</span></td>
                <td class="text-sm">{{ formatDateOnly(e.date ?? store.detail.date) }}</td>
                <td class="mono text-sm">{{ e.session_id ?? store.detail.id }}</td>
                <td class="mono text-sm">{{ e.compte ?? '—' }}</td>
                <td class="amount">{{ formatAmount(e.montant) }}</td>
                <td><CriticalityBadge :criticite="e.criticite" /></td>
                <td><StatusBadge :status="e.statut" /></td>
                <td>
                  <router-link to="/ecarts" class="btn btn-secondary btn-sm">Détail</router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Onglet Transactions -->
        <div v-else class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>TYPE FLUX</th>
                <th>DATE</th>
                <th>COMPTE DÉBIT</th>
                <th>COMPTE CRÉDIT</th>
                <th>MONTANT</th>
                <th>STATUT</th>
                <th>STATUT TRAITEMENT</th>
                <th>ACTION</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!store.detail.transactions?.length"><td colspan="9" class="empty-state">Aucune transaction.</td></tr>
              <tr v-for="t in store.detail.transactions" :key="t.ref">
                <td class="mono text-sm">{{ t.ref }}</td>
                <td><span class="flux-badge">{{ t.type_flux }}</span></td>
                <td class="text-sm">{{ formatDate(t.date) }}</td>
                <td class="mono text-sm">{{ t.compte_debit ?? t.ref }}</td>
                <td class="mono text-sm">{{ t.compte_credit ?? '—' }}</td>
                <td class="amount">{{ formatAmount(t.montant) }}</td>
                <td><StatusBadge :status="t.statut" /></td>
                <td>
                  <span :class="['traitement-badge', t.statut_traitement === 'OK' ? 'tr-ok' : 'tr-err']">
                    {{ t.statut_traitement ?? (t.statut === 'Lettrée' ? 'OK' : 'En attente') }}
                  </span>
                </td>
                <td><button class="btn btn-secondary btn-sm">Voir</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Chart, DoughnutController, ArcElement, Tooltip, Legend } from 'chart.js'
import { useSessionsStore } from '@/stores/sessions'
import StatusBadge from '@/components/common/StatusBadge.vue'
import CriticalityBadge from '@/components/common/CriticalityBadge.vue'
import { formatDate, formatDateOnly, formatAmount } from '@/utils/format'

Chart.register(DoughnutController, ArcElement, Tooltip, Legend)

const route = useRoute()
const store = useSessionsStore()
const tab = ref('ecarts')
const donutCanvas = ref(null)
let donutChart = null

onMounted(async () => {
  await store.fetchDetail(route.params.id)
  buildDonut()
})

function buildDonut() {
  if (!store.detail || !donutCanvas.value) return
  if (donutChart) donutChart.destroy()
  donutChart = new Chart(donutCanvas.value, {
    type: 'doughnut',
    data: {
      labels: ['Lettrées', 'Écarts'],
      datasets: [{
        data: [store.detail.nb_lettrees ?? 0, store.detail.nb_ecarts ?? 0],
        backgroundColor: ['#0d2b5e', '#f97316'], borderWidth: 0, hoverOffset: 4
      }]
    },
    options: {
      cutout: '72%',
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed.toLocaleString('fr-FR')}` } }
      }
    }
  })
}

watch(() => store.detail, () => { if (store.detail) buildDonut() })
function exportExcel() { alert('Export Excel en cours de génération…') }
function exportPdf()   { alert('Export PDF en cours de génération…') }
</script>

<style scoped>
.back-link { display: inline-flex; align-items: center; font-size: 13px; color: var(--color-text-muted); margin-bottom: 6px; transition: color 0.15s; }
.back-link:hover { color: var(--color-primary); }

.detail-header { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

.donut-card .donut-wrapper { display: flex; align-items: center; gap: 28px; }
.donut-canvas-wrap { width: 160px; height: 160px; flex-shrink: 0; }

.donut-stats { display: flex; flex-direction: column; gap: 14px; flex: 1; }

.donut-metric { display: flex; flex-direction: column; }
.dm-value { font-size: 22px; font-weight: 700; color: var(--color-text); }
.dm-label { font-size: 11px; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.04em; }
.donut-metric.warn .dm-value { color: var(--color-warning); }

.donut-legend { display: flex; flex-direction: column; gap: 6px; border-top: 1px solid var(--color-border); padding-top: 10px; }
.leg-item { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--color-text-muted); }
.leg-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

.info-rows { display: flex; flex-direction: column; gap: 0; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 11px 0; border-bottom: 1px solid #f1f5f9; font-size: 14px; }
.info-row:last-child { border-bottom: none; }
.info-row > span:first-child { color: var(--color-text-muted); }
.val-success { color: var(--color-success); font-weight: 600; }
.val-warning { color: var(--color-warning); font-weight: 600; }

.tabs { display: flex; border-bottom: 2px solid var(--color-border); }
.tab-btn { padding: 10px 20px; font-size: 14px; font-weight: 500; color: var(--color-text-muted); background: none; border: none; border-bottom: 2px solid transparent; margin-bottom: -2px; cursor: pointer; transition: all 0.15s; }
.tab-btn:hover { color: var(--color-text); }
.tab-btn.active { color: var(--color-primary); border-bottom-color: var(--color-primary); }

.mono { font-family: 'Courier New', monospace; font-size: 12px; }
.amount { font-weight: 500; }

.flux-badge { display: inline-block; padding: 2px 8px; background: #f1f5f9; border-radius: 4px; font-size: 12px; font-weight: 600; font-family: monospace; color: var(--color-primary); }

.traitement-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11.5px; font-weight: 600; }
.tr-ok  { background: var(--color-success-bg); color: var(--color-success); }
.tr-err { background: #f1f5f9; color: #475569; }
</style>
