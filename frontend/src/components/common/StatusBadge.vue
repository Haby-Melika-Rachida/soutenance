<template>
  <span class="badge" :class="cls"><span class="badge-dot" />{{ label }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ status: { type: String, required: true } })

const MAP = {
  'TERMINÉ':     { cls: 'badge-success', label: 'TERMINÉ' },
  'RÉSOLU':      { cls: 'badge-success', label: 'RÉSOLU' },
  'RÉSOLUS':     { cls: 'badge-success', label: 'RÉSOLUS' },
  'ERREUR':      { cls: 'badge-error',   label: 'ERREUR' },
  'EN COURS':    { cls: 'badge-info',    label: 'EN COURS' },
  'À TRAITER':   { cls: 'badge-warning', label: 'À TRAITER' },
  'IGNORÉ':      { cls: 'badge-muted',   label: 'IGNORÉ' },
  'Lettrée':     { cls: 'badge-success', label: 'Lettrée' },
  'Non lettrée': { cls: 'badge-warning', label: 'Non lettrée' }
}

const cls   = computed(() => MAP[props.status]?.cls   ?? 'badge-muted')
const label = computed(() => MAP[props.status]?.label ?? props.status)
</script>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
  white-space: nowrap;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.badge-success { background: #dcfce7; color: #15803d; }
.badge-success .badge-dot { background: #15803d; }

.badge-error   { background: #fee2e2; color: #dc2626; }
.badge-error   .badge-dot { background: #dc2626; }

.badge-info    { background: #dbeafe; color: #1d4ed8; }
.badge-info    .badge-dot { background: #1d4ed8; }

.badge-warning { background: #fef3c7; color: #92400e; }
.badge-warning .badge-dot { background: #d97706; }

.badge-muted   { background: #f1f5f9; color: #64748b; }
.badge-muted   .badge-dot { background: #94a3b8; }
</style>
