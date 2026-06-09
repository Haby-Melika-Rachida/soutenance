import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard',    name: 'Dashboard',     component: () => import('@/views/DashboardView.vue') },
      { path: 'sessions',     name: 'Sessions',      component: () => import('@/views/SessionsView.vue') },
      { path: 'sessions/:id', name: 'SessionDetail', component: () => import('@/views/SessionDetailView.vue') },
      { path: 'ecarts',       name: 'Ecarts',        component: () => import('@/views/EcartsView.vue') },
      { path: 'annotations',  name: 'Annotations',   component: () => import('@/views/AnnotationsView.vue') },
      { path: 'configuration',name: 'Configuration', component: () => import('@/views/ConfigurationView.vue') },
      { path: 'logs',         name: 'Logs',          component: () => import('@/views/LogsView.vue') },
      { path: 'utilisateurs', name: 'Utilisateurs',  component: () => import('@/views/UsersView.vue') },
      { path: 'audit',        name: 'Audit',         component: () => import('@/views/AuditView.vue') }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: 'Login' }
  }
  if (to.name === 'Login' && auth.isAuthenticated) {
    return { name: 'Dashboard' }
  }
})

export default router
