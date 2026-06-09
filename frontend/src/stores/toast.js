import { defineStore } from 'pinia'

export const useToastStore = defineStore('toast', {
  state: () => ({
    toasts: []
  }),
  actions: {
    show(message, type = 'success') {
      const id = Date.now() + Math.random()
      this.toasts.push({ id, message, type })
      setTimeout(() => {
        const idx = this.toasts.findIndex(t => t.id === id)
        if (idx !== -1) this.toasts.splice(idx, 1)
      }, 3000)
    }
  }
})
