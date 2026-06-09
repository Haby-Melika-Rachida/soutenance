<template>
  <div class="kpi-card" :class="`kpi-card--${variant}`">
    <div class="kpi-icon">
      <span v-html="icon" />
    </div>
    <span class="kpi-label">{{ label }}</span>
    <span class="kpi-value">{{ value }}</span>
    <span v-if="sub" class="kpi-sub">{{ sub }}</span>
  </div>
</template>

<script setup>
defineProps({
  label:   { type: String, required: true },
  value:   { type: [String, Number], required: true },
  sub:     { type: String, default: null },
  icon:    { type: String, required: true },
  variant: { type: String, default: 'blue' }
})
</script>

<style scoped>
.kpi-card {
  background: #fff;
  border-radius: 10px;
  padding: 16px 18px 18px;
  box-shadow: var(--shadow);
  position: relative;
  border-left: 4px solid;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.kpi-card--blue   { border-color: var(--color-info); }
.kpi-card--green  { border-color: var(--color-success); }
.kpi-card--orange { border-color: var(--color-warning); }
.kpi-card--red    { border-color: var(--color-error); }

.kpi-icon {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kpi-card--blue   .kpi-icon { background: #dbeafe; color: var(--color-info); }
.kpi-card--green  .kpi-icon { background: #dcfce7; color: var(--color-success); }
.kpi-card--orange .kpi-icon { background: #fef3c7; color: var(--color-warning); }
.kpi-card--red    .kpi-icon { background: #fee2e2; color: var(--color-error); }

.kpi-icon :deep(svg) { width: 20px; height: 20px; }

.kpi-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding-right: 54px;
}

.kpi-value {
  font-size: 26px;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1.15;
  margin-top: 2px;
}

.kpi-sub {
  font-size: 12px;
  color: var(--color-text-muted);
}
</style>
