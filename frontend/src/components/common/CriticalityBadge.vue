<template>
  <span class="badge" :class="cls">{{ criticite }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ criticite: { type: String, required: true } })

const cls = computed(() => {
  switch (props.criticite) {
    case 'Critique':  return 'badge-critique'
    case 'Important': return 'badge-important'
    case 'Faible':    return 'badge-faible'
    default:          return 'badge-faible'
  }
})
</script>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11.5px;
  font-weight: 600;
  letter-spacing: 0.03em;
  white-space: nowrap;
}
.badge-critique  { background: var(--color-error-bg);   color: var(--color-error); }
.badge-important { background: var(--color-warning-bg); color: var(--color-warning); }
.badge-faible    { background: var(--color-success-bg); color: var(--color-success); }
</style>
