<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Tableau de bord</h1>
        <p class="page-subtitle">Vue d'ensemble des rapprochements MB/CBS/PI</p>
      </div>
      <span class="last-update">{{ today }}</span>
    </div>

    <!-- KPI Cards -->
    <div class="grid-4 mb-6">
      <template v-if="store.kpi">
        <KpiCard label="Taux moyen" :value="formatPercent(store.kpi.taux_moyen)"
          sub="30 derniers jours" :icon="iconTaux" variant="blue" />
        <KpiCard label="Transactions lettrées" :value="store.kpi.transactions_lettrees.toLocaleString('fr-FR')"
          sub="Ce mois" :icon="iconLettrees" variant="green" />
        <KpiCard label="Écarts détectés" :value="store.kpi.ecarts_detectes"
          sub="En attente de traitement" :icon="iconEcarts" variant="orange" />
        <KpiCard label="Écarts critiques" :value="store.kpi.ecarts_critiques"
          sub="Action requise" :icon="iconCritiques" variant="red" />
      </template>
      <div v-else class="kpi-skeleton" v-for="i in 4" :key="i" />
    </div>

    <!-- Dernière session — carte dégradé bleu marine -->
    <div class="session-card mb-6" v-if="store.lastSession">
      <div class="session-card-header">
        <h2 class="session-card-title">Dernière session de rapprochement</h2>
        <router-link to="/sessions" class="btn btn-outline-white btn-sm">
          Historique des sessions
        </router-link>
      </div>

      <div class="session-grid">
        <div class="session-item">
          <span class="s-label">Identifiant</span>
          <span class="s-val s-mono">{{ store.lastSession.id }}</span>
        </div>
        <div class="session-item">
          <span class="s-label">Date d'exécution</span>
          <span class="s-val">{{ formatDate(store.lastSession.date) }}</span>
        </div>
        <div class="session-item">
          <span class="s-label">Statut</span>
          <StatusBadge :status="store.lastSession.statut" />
        </div>
        <div class="session-item">
          <span class="s-label">Transactions matchées</span>
          <span class="s-val s-big">{{ store.lastSession.nb_lettrees?.toLocaleString('fr-FR') }}</span>
        </div>
        <div class="session-item">
          <span class="s-label">Taux de lettrage</span>
          <span class="s-val s-big s-taux">{{ store.lastSession.taux ?? store.lastSession.taux_lettrage }}%</span>
        </div>
        <div class="session-item">
          <span class="s-label">Écarts détectés</span>
          <span class="s-val s-big" :class="store.lastSession.nb_ecarts > 0 ? 's-warn' : 's-muted'">
            {{ store.lastSession.nb_ecarts }}
          </span>
        </div>
        <div class="session-item">
          <span class="s-label">Écarts critiques</span>
          <span class="s-val s-big" :class="(store.lastSession.nb_critiques ?? 0) > 0 ? 's-error' : 's-muted'">
            {{ store.lastSession.nb_critiques ?? 0 }}
          </span>
        </div>
        <div />
      </div>
    </div>

    <!-- Graphiques -->
    <div class="grid-2">
      <div class="card">
        <h2 class="card-title mb-4">Nombre d'écarts par semaine</h2>
        <div class="chart-container">
          <canvas ref="weeklyChart" />
        </div>
      </div>
      <div class="card">
        <h2 class="card-title mb-4">Écarts des 30 derniers jours</h2>
        <div class="chart-container">
          <canvas ref="monthlyChart" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import {
  Chart, BarController, BarElement,
  LineController, LineElement, PointElement,
  LinearScale, CategoryScale, Tooltip, Filler
} from 'chart.js'
import { useDashboardStore } from '@/stores/dashboard'
import KpiCard from '@/components/common/KpiCard.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { formatDate, formatPercent } from '@/utils/format'

Chart.register(BarController, BarElement, LineController, LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Filler)

const store = useDashboardStore()
const weeklyChart  = ref(null)
const monthlyChart = ref(null)
let chartW = null, chartM = null

const today = new Intl.DateTimeFormat('fr-FR', { dateStyle: 'full' }).format(new Date())

const CHART_OPT_BAR = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: {
      min: 0,
      ticks: { stepSize: 1, font: { size: 11 } },
      grid: { color: '#f1f5f9' },
      border: { display: false }
    },
    x: {
      ticks: { font: { size: 11 } },
      grid: { display: false },
      border: { display: false }
    }
  }
}

const CHART_OPT_LINE = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: {
      min: 0,
      ticks: { stepSize: 1, font: { size: 11 } },
      grid: { color: '#f1f5f9' },
      border: { display: false }
    },
    x: {
      ticks: {
        font: { size: 11 },
        maxTicksLimit: 6,
        maxRotation: 0
      },
      grid: { display: false },
      border: { display: false }
    }
  }
}

function buildBarChart(canvas, data) {
  return new Chart(canvas, {
    type: 'bar',
    data: {
      labels: data.labels,
      datasets: [{
        data: data.data,
        backgroundColor: data.data.map(v => v > 0 ? '#dc2626cc' : '#0d2b5e33'),
        borderColor: data.data.map(v => v > 0 ? '#dc2626' : '#0d2b5e'),
        borderWidth: 1,
        borderRadius: 4
      }]
    },
    options: CHART_OPT_BAR
  })
}

function buildLineChart(canvas, data) {
  return new Chart(canvas, {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [{
        data: data.data,
        borderColor: '#0d2b5e',
        backgroundColor: 'rgba(13,43,94,0.06)',
        fill: false,
        tension: 0.3,
        borderWidth: 2,
        pointBackgroundColor: '#0d2b5e',
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: CHART_OPT_LINE
  })
}

onMounted(async () => {
  await store.fetchAll()
  if (store.weekly  && weeklyChart.value)  chartW = buildBarChart(weeklyChart.value,   store.weekly)
  if (store.monthly && monthlyChart.value) chartM = buildLineChart(monthlyChart.value, store.monthly)
})

watch(() => store.weekly, val => {
  if (!val) return
  if (chartW) { chartW.data.labels = val.labels; chartW.data.datasets[0].data = val.data; chartW.update() }
  else if (weeklyChart.value) chartW = buildBarChart(weeklyChart.value, val)
})

watch(() => store.monthly, val => {
  if (!val) return
  if (chartM) { chartM.data.labels = val.labels; chartM.data.datasets[0].data = val.data; chartM.update() }
  else if (monthlyChart.value) chartM = buildLineChart(monthlyChart.value, val)
})

const iconTaux     = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941" /></svg>`
const iconLettrees = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>`
const iconEcarts   = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>`
const iconCritiques= `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>`
</script>

<style scoped>
.last-update {
  font-size: 12px; color: var(--color-text-muted);
  background: #fff; border: 1px solid var(--color-border);
  border-radius: 6px; padding: 5px 11px; white-space: nowrap;
  text-transform: capitalize;
}

.kpi-skeleton {
  height: 80px; border-radius: 10px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%; animation: shimmer 1.5s infinite;
}
@keyframes shimmer { to { background-position: -200% 0; } }

.session-card {
  background: linear-gradient(135deg, #0d2b5e 0%, #1a3d7a 100%);
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  padding: 14px 20px;
}

.session-card-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px;
}

.session-card-title { font-size: 14px; font-weight: 600; color: #fff; }

.session-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px 16px;
}

.session-item { display: flex; flex-direction: column; gap: 4px; }

.s-label {
  font-size: 10px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.06em; color: rgba(255,255,255,0.55);
}

.s-val   { font-size: 13px; font-weight: 500; color: rgba(255,255,255,0.9); }
.s-mono  { font-family: 'Courier New', monospace; font-size: 12px; }
.s-big   { font-size: 17px; font-weight: 700; }
.s-taux  { color: #7dd3fc; }
.s-warn  { color: #fde68a; }
.s-error { color: #fca5a5; }
.s-muted { color: rgba(255,255,255,0.45); }

.chart-container { height: 200px; }
</style>
