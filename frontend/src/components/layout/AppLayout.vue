<template>
  <div style="display:flex; min-height:100vh;">
    <AppSidebar />
    <main style="flex:1; margin-left:var(--sidebar-width); background:#f8fafc; overflow-y:auto; padding:16px 20px; min-height:100vh;">
      <RouterView />
    </main>
    <AppToast />
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import AppSidebar from './AppSidebar.vue'
import AppToast from '@/components/common/Toast.vue'
import { useAuthStore } from '@/stores/auth'
import { onMounted } from 'vue'

const auth = useAuthStore()
onMounted(() => { if (!auth.user) auth.fetchUser() })
</script>
