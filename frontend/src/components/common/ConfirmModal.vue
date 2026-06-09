<template>
  <teleport to="body">
    <transition name="modal">
      <div v-if="modelValue" class="confirm-overlay" @click.self="cancel">
        <div class="confirm-container">

          <div class="confirm-icon" :class="`icon-${variant}`">
            <svg v-if="variant === 'danger'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
            <svg v-else-if="variant === 'warning'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
            </svg>
          </div>

          <h3 class="confirm-title">{{ title }}</h3>
          <p class="confirm-message">{{ message }}</p>

          <div class="confirm-extra" v-if="$slots.default">
            <slot />
          </div>

          <div class="confirm-footer">
            <button class="btn btn-secondary" @click="cancel" :disabled="loading">
              {{ cancelText }}
            </button>
            <button class="btn" :class="confirmBtnClass" @click="confirm" :disabled="loading">
              <span v-if="loading" class="spinner-sm" />
              {{ confirmText }}
            </button>
          </div>

        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue:  { type: Boolean, required: true },
  title:       { type: String,  default: 'Confirmer l\'action' },
  message:     { type: String,  required: true },
  confirmText: { type: String,  default: 'Confirmer' },
  cancelText:  { type: String,  default: 'Annuler' },
  variant:     { type: String,  default: 'warning' },  // 'danger' | 'warning' | 'info'
  loading:     { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const confirmBtnClass = computed(() => {
  switch (props.variant) {
    case 'danger':  return 'btn-danger'
    case 'warning': return 'btn-warning-confirm'
    default:        return 'btn-primary'
  }
})

function confirm() { emit('confirm'); emit('update:modelValue', false) }
function cancel()  { emit('cancel');  emit('update:modelValue', false) }
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 20, 40, 0.65);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  padding: 24px;
}

.confirm-container {
  background: #fff;
  border-radius: 12px;
  width: 100%;
  max-width: 420px;
  padding: 32px 28px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow:
    0 4px 6px rgba(0,0,0,0.05),
    0 10px 40px rgba(0,0,0,0.18);
}

.confirm-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}
.confirm-icon svg { width: 28px; height: 28px; }

.icon-danger  { background: var(--color-error-bg);   color: var(--color-error); }
.icon-warning { background: var(--color-warning-bg); color: var(--color-warning); }
.icon-info    { background: var(--color-info-bg);    color: var(--color-info); }

.confirm-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 8px;
}

.confirm-message {
  font-size: 14px;
  color: var(--color-text-muted);
  line-height: 1.6;
  margin-bottom: 8px;
}

.confirm-extra {
  width: 100%;
  margin-top: 8px;
  margin-bottom: 4px;
}

.confirm-footer {
  display: flex;
  gap: 10px;
  width: 100%;
  margin-top: 20px;
}
.confirm-footer .btn { flex: 1; justify-content: center; }

.btn-danger {
  background: var(--color-error);
  color: #fff;
}
.btn-danger:hover:not(:disabled) { background: #b91c1c; }
.btn-danger:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-warning-confirm {
  background: var(--color-warning);
  color: #fff;
}
.btn-warning-confirm:hover:not(:disabled) { background: #c2410c; }
.btn-warning-confirm:disabled { opacity: 0.6; cursor: not-allowed; }

.spinner-sm {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.modal-enter-active, .modal-leave-active { transition: opacity 0.18s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
