<template>
  <teleport to="body">
    <div class="toast-container">
      <transition-group name="toast-slide">
        <div v-for="t in store.toasts" :key="t.id" class="toast" :class="`toast-${t.type}`">
          <svg v-if="t.type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width:17px;height:17px;flex-shrink:0">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="width:17px;height:17px;flex-shrink:0">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
          {{ t.message }}
        </div>
      </transition-group>
    </div>
  </teleport>
</template>

<script setup>
import { useToastStore } from '@/stores/toast'
const store = useToastStore()
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 11px 18px;
  border-radius: 8px;
  color: #fff;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 4px 14px rgba(0,0,0,0.18);
  min-width: 260px;
  pointer-events: all;
}

.toast-success { background: #15803d; }
.toast-error   { background: #dc2626; }
.toast-info    { background: #2563eb; }

.toast-slide-enter-active,
.toast-slide-leave-active { transition: all 0.28s ease; }
.toast-slide-enter-from   { opacity: 0; transform: translateX(40px); }
.toast-slide-leave-to     { opacity: 0; transform: translateX(40px); }
</style>
