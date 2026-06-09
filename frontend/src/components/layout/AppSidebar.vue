<template>
  <aside class="sidebar">
    <!-- Logo -->
    <div class="sidebar-logo">
      <div class="logo-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21M3 21h18M12 6.75h.008v.008H12V6.75z" />
        </svg>
      </div>
      <div class="logo-text">
        <span class="logo-name">LICELI</span>
        <span class="logo-sub">Technologies</span>
      </div>
    </div>

    <div class="sidebar-divider" />

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <!-- Tableau de bord — tous les profils -->
      <RouterLink
        v-if="hasPermission('Administrateur', 'Responsable MB', 'Agent Back-Office')"
        to="/dashboard" class="nav-item" :class="{ active: isActive('/dashboard') }">
        <span class="nav-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
          </svg>
        </span>
        <span class="nav-label">Tableau de bord</span>
      </RouterLink>

      <!-- Historique des sessions — tous les profils -->
      <RouterLink
        v-if="hasPermission('Administrateur', 'Responsable MB', 'Agent Back-Office')"
        to="/sessions" class="nav-item" :class="{ active: isActive('/sessions') }">
        <span class="nav-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </span>
        <span class="nav-label">Historique des sessions</span>
      </RouterLink>

      <!-- Écarts détectés — tous les profils -->
      <RouterLink
        v-if="hasPermission('Administrateur', 'Responsable MB', 'Agent Back-Office')"
        to="/ecarts" class="nav-item" :class="{ active: isActive('/ecarts') }">
        <span class="nav-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
          </svg>
        </span>
        <span class="nav-label">Écarts détectés</span>
      </RouterLink>

      <!-- Historique des annotations — tous les profils -->
      <RouterLink
        v-if="hasPermission('Administrateur', 'Responsable MB', 'Agent Back-Office')"
        to="/annotations" class="nav-item" :class="{ active: isActive('/annotations') }">
        <span class="nav-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
          </svg>
        </span>
        <span class="nav-label">Historique des annotations</span>
      </RouterLink>

      <!-- Configuration — Administrateur seulement -->
      <RouterLink
        v-if="hasPermission('Administrateur')"
        to="/configuration" class="nav-item" :class="{ active: isActive('/configuration') }">
        <span class="nav-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </span>
        <span class="nav-label">Configuration</span>
      </RouterLink>

      <!-- Journaux d'exécution — Administrateur seulement -->
      <RouterLink
        v-if="hasPermission('Administrateur')"
        to="/logs" class="nav-item" :class="{ active: isActive('/logs') }">
        <span class="nav-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 6.75h12M8.25 12h12m-12 5.25h12M3.75 6.75h.007v.008H3.75V6.75zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zM3.75 12h.007v.008H3.75V12zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm-.375 5.25h.007v.008H3.75v-.008zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
          </svg>
        </span>
        <span class="nav-label">Journaux d'exécution</span>
      </RouterLink>

      <!-- Utilisateurs — Administrateur seulement -->
      <RouterLink
        v-if="hasPermission('Administrateur')"
        to="/utilisateurs" class="nav-item" :class="{ active: isActive('/utilisateurs') }">
        <span class="nav-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
          </svg>
        </span>
        <span class="nav-label">Utilisateurs</span>
      </RouterLink>

      <!-- Journaux d'audit — Administrateur seulement -->
      <RouterLink
        v-if="hasPermission('Administrateur')"
        to="/audit" class="nav-item" :class="{ active: isActive('/audit') }">
        <span class="nav-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
          </svg>
        </span>
        <span class="nav-label">Journaux d'audit</span>
      </RouterLink>
    </nav>

    <!-- Pied de sidebar : profil utilisateur + déconnexion -->
    <div class="sidebar-footer">
      <div class="sidebar-divider" />
      <div class="user-info" v-if="auth.user">
        <div class="user-avatar">{{ initials }}</div>
        <div class="user-details">
          <span class="user-name">{{ auth.user.prenom || auth.user.username }}</span>
          <span class="user-role">{{ auth.user.profil || auth.user.role || '' }}</span>
        </div>
      </div>
      <button class="nav-item logout-btn" @click="showLogoutConfirm = true">
        <span class="nav-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
          </svg>
        </span>
        <span class="nav-label">Déconnexion</span>
      </button>
    </div>
  </aside>

  <!-- Confirmation déconnexion -->
  <ConfirmModal
    v-model="showLogoutConfirm"
    title="Se déconnecter ?"
    message="Vous serez redirigé vers la page de connexion."
    confirm-text="Se déconnecter"
    variant="danger"
    @confirm="doLogout"
  />
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

const router = useRouter()
const route  = useRoute()
const auth   = useAuthStore()
const showLogoutConfirm = ref(false)

function hasPermission(...roles) {
  const userRole = auth.user?.profil ?? auth.user?.role ?? ''
  if (!userRole) return true
  return roles.includes(userRole)
}

const isActive = (to) => route.path === to || route.path.startsWith(to + '/')

const initials = computed(() => {
  if (!auth.user) return 'U'
  const u = auth.user
  if (u.prenom && u.nom) return (u.prenom[0] + u.nom[0]).toUpperCase()
  return (u.username || 'U')[0].toUpperCase()
})

function doLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  min-height: 100vh;
  background: #0d2b5e;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 100;
  overflow-y: auto;
}

/* Logo */
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 18px 16px;
  flex-shrink: 0;
}

.logo-icon {
  width: 36px; height: 36px;
  background: rgba(255,255,255,0.15);
  border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.logo-icon svg { width: 20px; height: 20px; color: #fff; }

.logo-text { display: flex; flex-direction: column; }
.logo-name { font-size: 15px; font-weight: 700; color: #fff; letter-spacing: 0.05em; line-height: 1.2; }
.logo-sub  { font-size: 10px; color: rgba(255,255,255,0.5); }

.sidebar-divider {
  height: 1px;
  background: rgba(255,255,255,0.1);
  margin: 0 16px;
  flex-shrink: 0;
}

/* Navigation */
.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px 8px;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 13px;
  border-radius: 7px;
  color: rgba(255,255,255,0.72);
  font-size: 13px;
  font-weight: 400;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
  cursor: pointer;
  background: none;
  border: none;
  width: 100%;
  text-align: left;
  box-sizing: border-box;
}

.nav-item:hover {
  background: rgba(255,255,255,0.08);
  color: #fff;
}

.nav-item.active {
  background: rgba(255,255,255,0.12);
  color: #fff;
  font-weight: 500;
  box-shadow: inset 3px 0 0 #4a9eff;
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 18px; height: 18px;
}
.nav-icon svg { width: 17px; height: 17px; }

.nav-label { line-height: 1.3; }

/* Pied */
.sidebar-footer {
  padding: 0 8px 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex-shrink: 0;
}

.user-info {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 10px 6px;
}

.user-avatar {
  width: 32px; height: 32px;
  background: rgba(255,255,255,0.18);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; color: #fff;
  flex-shrink: 0;
}

.user-details { display: flex; flex-direction: column; overflow: hidden; }
.user-name {
  font-size: 13px; font-weight: 500; color: #fff;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.user-role { font-size: 11px; color: rgba(255,255,255,0.45); }

/* Bouton déconnexion — rouge */
.logout-btn { color: #f87171; }
.logout-btn:hover {
  background: rgba(220,38,38,0.18);
  color: #dc2626;
}
</style>
