<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Configuration</h1>
        <p class="page-subtitle">Paramètres du batch de rapprochement nocturne</p>
      </div>
    </div>

    <div class="alert alert-success" v-if="store.success">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:18px;height:18px;flex-shrink:0"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
      {{ store.success }}
    </div>
    <div class="alert alert-error" v-if="store.error">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:18px;height:18px;flex-shrink:0"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>
      {{ store.error }}
    </div>

    <div class="config-grid">
      <!-- Paramètres batch -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Paramètres du batch</h2>
          <span class="badge-admin">Administrateur</span>
        </div>

        <form @submit.prevent="save" class="config-form">
          <div class="form-group">
            <label class="form-label">Heure d'exécution quotidienne (HH:MM)</label>
            <input v-model="form.heure_execution" type="time" class="form-control" step="900" />
            <small class="form-hint">Le batch se lancera chaque nuit à cette heure (UTC+0)</small>
          </div>

          <div class="form-group">
            <label class="form-label">Tolérance de date (jours)</label>
            <div class="input-with-unit">
              <input v-model.number="form.tolerance_date" type="number" class="form-control" min="0" max="5" />
              <span class="input-unit">jours</span>
            </div>
            <small class="form-hint">Écart maximal de date de valeur accepté entre MB/CBS/PI (0 – 5)</small>
          </div>

          <div class="form-group">
            <label class="form-label">Timeout API (secondes)</label>
            <div class="input-with-unit">
              <input v-model.number="form.timeout_api" type="number" class="form-control" min="10" max="120" />
              <span class="input-unit">sec</span>
            </div>
            <small class="form-hint">Délai maximum pour les appels CBS et PI (10 – 120 s)</small>
          </div>

          <div class="form-group">
            <label class="form-label">Nombre de retry (tentatives)</label>
            <div class="input-with-unit">
              <input v-model.number="form.nb_retry" type="number" class="form-control" min="0" max="10" />
              <span class="input-unit">fois</span>
            </div>
            <small class="form-hint">Tentatives automatiques en cas de timeout ou d'erreur réseau (0 – 10)</small>
          </div>

          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="cancelForm">Annuler</button>
            <button type="submit" class="btn btn-primary" :disabled="store.saving">
              <span v-if="store.saving" class="spinner-sm" />
              {{ store.saving ? 'Enregistrement…' : 'Enregistrer les modifications' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Déclenchement manuel -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">Déclenchement manuel</h2>
          <span class="badge-admin">Administrateur</span>
        </div>

        <!-- Alerte batch en cours -->
        <div class="batch-warning" v-if="batchEnCours">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:18px;height:18px;flex-shrink:0">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
          </svg>
          <div>
            <strong>Batch en cours d'exécution</strong>
            <p>Un batch est actuellement en cours (session S-2024-0136). Attendez sa fin avant de déclencher un nouveau rapprochement.</p>
          </div>
        </div>

        <div class="manual-section">
          <div class="manual-info">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:18px;height:18px;color:#2563eb;flex-shrink:0">
              <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
            </svg>
            <p>Lance un rapprochement hors planification sur la date de référence choisie. Cette opération est irréversible.</p>
          </div>

          <div class="form-group">
            <label class="form-label">Date de référence</label>
            <input v-model="triggerDate" type="date" class="form-control" :max="today" :disabled="batchEnCours" />
          </div>

          <div class="trigger-confirm" v-if="triggerDate && !batchEnCours">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:16px;height:16px;flex-shrink:0">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
            Le rapprochement pour le <strong>{{ formatDateOnly(triggerDate) }}</strong> sera lancé immédiatement.
          </div>

          <button
            class="btn btn-danger trigger-btn"
            :disabled="!triggerDate || store.triggering || batchEnCours"
            @click="triggerNow()"
          >
            <svg v-if="!store.triggering" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:16px;height:16px"><path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" /></svg>
            <span v-if="store.triggering" class="spinner-sm" />
            {{ store.triggering ? 'Déclenchement…' : 'Déclencher maintenant' }}
          </button>

          <!-- Résumé config actuelle -->
          <div class="config-summary">
            <h3 class="cs-title">Planification active</h3>
            <div class="cs-item"><span>Prochain déclenchement</span><strong>{{ store.settings.heure_execution }} — demain</strong></div>
            <div class="cs-item"><span>Tolérance date</span><strong>{{ store.settings.tolerance_date }} jour(s)</strong></div>
            <div class="cs-item"><span>Timeout API</span><strong>{{ store.settings.timeout_api }} s</strong></div>
            <div class="cs-item"><span>Retry</span><strong>{{ store.settings.nb_retry }} tentative(s)</strong></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Confirmation déclenchement manuel -->
  <ConfirmModal
    v-model="showTriggerConfirm"
    title="Déclencher le rapprochement ?"
    :message="`Un rapprochement manuel sera lancé immédiatement pour le ${formatDateOnly(triggerDate)}. Cette opération est irréversible et peut prendre plusieurs minutes.`"
    confirm-text="Déclencher"
    variant="warning"
    @confirm="doTrigger"
  />
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useConfigStore } from '@/stores/config'
import { formatDateOnly } from '@/utils/format'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

const store = useConfigStore()
const triggerDate = ref('')
const today = new Date().toISOString().split('T')[0]
const batchEnCours = ref(true) // mock: batch S-2024-0136 en cours
const showTriggerConfirm = ref(false)

const form = reactive({ heure_execution: '02:00', tolerance_date: 1, timeout_api: 30, nb_retry: 3 })

onMounted(async () => {
  await store.fetchSettings()
  Object.assign(form, store.settings)
})

function cancelForm() { Object.assign(form, store.settings) }

async function save() {
  await store.saveSettings({ ...form })
  Object.assign(form, store.settings)
}

function triggerNow() {
  showTriggerConfirm.value = true
}

async function doTrigger() {
  await store.triggerManual(triggerDate.value)
  triggerDate.value = ''
}
</script>

<style scoped>
.config-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: start; }

.badge-admin {
  font-size: 11px; font-weight: 600; padding: 3px 10px;
  background: #f3e8ff; color: #7c3aed; border-radius: 20px;
}

.config-form { display: flex; flex-direction: column; gap: 20px; }

.input-with-unit { display: flex; align-items: center; }
.input-with-unit .form-control { border-radius: var(--radius) 0 0 var(--radius); flex: 1; }
.input-unit {
  padding: 9px 12px; background: #f8fafc; border: 1px solid var(--color-border);
  border-left: none; border-radius: 0 var(--radius) var(--radius) 0;
  font-size: 13px; color: var(--color-text-muted); white-space: nowrap;
}

.form-hint { font-size: 12px; color: var(--color-text-muted); }

.form-actions {
  display: flex; gap: 12px; justify-content: flex-end;
  padding-top: 4px; border-top: 1px solid var(--color-border);
}

.batch-warning {
  display: flex; gap: 12px; align-items: flex-start;
  padding: 14px 16px; background: var(--color-warning-bg); color: var(--color-warning);
  border-radius: 8px; border: 1px solid #fed7aa; margin-bottom: 16px; font-size: 13px;
}
.batch-warning strong { display: block; font-size: 13.5px; margin-bottom: 4px; }
.batch-warning p { line-height: 1.4; margin: 0; color: #92400e; }

.manual-section { display: flex; flex-direction: column; gap: 16px; }

.manual-info {
  display: flex; gap: 12px; align-items: flex-start;
  background: var(--color-info-bg); padding: 12px 14px; border-radius: 8px; font-size: 13px; line-height: 1.5;
}

.trigger-confirm {
  display: flex; align-items: center; gap: 8px; padding: 10px 14px;
  background: var(--color-warning-bg); color: var(--color-warning);
  border-radius: 8px; font-size: 13px;
}

.trigger-btn { width: 100%; justify-content: center; }
.trigger-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.config-summary {
  padding: 14px 16px; background: #f8fafc;
  border-radius: var(--radius); border: 1px solid var(--color-border);
}
.cs-title {
  font-size: 11px; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.05em; color: var(--color-text-muted); margin-bottom: 10px;
}
.cs-item {
  display: flex; justify-content: space-between; font-size: 13px;
  padding: 6px 0; border-bottom: 1px solid var(--color-border); color: var(--color-text-muted);
}
.cs-item:last-child { border-bottom: none; }
.cs-item strong { color: var(--color-text); }

.alert {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; border-radius: 8px; font-size: 13.5px; font-weight: 500; margin-bottom: 20px;
}
.alert-success { background: var(--color-success-bg); color: var(--color-success); }
.alert-error   { background: var(--color-error-bg);   color: var(--color-error); }

.spinner-sm {
  width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
