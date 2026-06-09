<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-logo">
        <div class="login-logo-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21M3 21h18M12 6.75h.008v.008H12V6.75z" />
          </svg>
        </div>
        <div>
          <h1 class="login-brand">LICELI Technologies</h1>
          <p class="login-module">Module Rapprochement MB/CBS/PI</p>
        </div>
      </div>

      <div class="login-divider" />
      <h2 class="login-title">Connexion</h2>
      <p class="login-subtitle">Accès réservé aux utilisateurs autorisés</p>

      <div class="alert-error" v-if="auth.error">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
        </svg>
        {{ auth.error }}
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <!-- Champ Identifiant avec icône personne à gauche -->
        <div class="form-group">
          <label class="form-label" for="username">Identifiant</label>
          <div class="input-icon-wrap">
            <svg class="input-icon-left" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
            </svg>
            <input id="username" v-model="form.username" type="text"
              class="form-control input-with-icon-left"
              placeholder="Votre identifiant" autocomplete="username" required />
          </div>
        </div>

        <!-- Champ Mot de passe avec label+lien sur la même ligne, icône cadenas à gauche, œil à droite -->
        <div class="form-group">
          <div class="password-label-row">
            <label class="form-label" for="password">Mot de passe</label>
            <button type="button" class="forgot-link" @click="showForgot = true">
              Mot de passe oublié ?
            </button>
          </div>
          <div class="input-icon-wrap">
            <svg class="input-icon-left" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
            </svg>
            <input id="password" v-model="form.password" :type="showPassword ? 'text' : 'password'"
              class="form-control input-with-icon-left input-with-icon-right"
              placeholder="Votre mot de passe" autocomplete="current-password" required />
            <button type="button" class="password-toggle" @click="showPassword = !showPassword" :title="showPassword ? 'Masquer' : 'Afficher'">
              <svg v-if="!showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
              </svg>
            </button>
          </div>
        </div>

        <button type="submit" class="btn btn-primary login-btn" :disabled="auth.loading">
          <span v-if="auth.loading" class="spinner-sm" />
          {{ auth.loading ? 'Connexion en cours…' : 'Se connecter' }}
        </button>
      </form>

      <div class="demo-separator">
        <span>ou</span>
      </div>

      <button @click="accesDemo" :disabled="auth.loading"
        style="width:100%;margin-top:8px;padding:10px;background:transparent;border:1px solid #0d2b5e;color:#0d2b5e;border-radius:8px;cursor:pointer;font-size:13px;">
        Accès démo (sans connexion)
      </button>

      <p class="login-footer">Accès sécurisé — LICELI Technologies &copy; {{ new Date().getFullYear() }}</p>
    </div>

    <!-- Modal mot de passe oublié -->
    <div class="modal-overlay" v-if="showForgot" @click.self="showForgot = false">
      <div class="forgot-modal">
        <h3>Mot de passe oublié</h3>
        <p>Pour réinitialiser votre mot de passe, veuillez contacter votre administrateur système.</p>
        <div class="forgot-contact">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:18px;height:18px;flex-shrink:0">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
          </svg>
          admin@liceli.ci
        </div>
        <button class="btn btn-primary" style="width:100%;justify-content:center;margin-top:16px" @click="showForgot = false">
          Fermer
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const form = reactive({ username: '', password: '' })
const showPassword = ref(false)
const showForgot = ref(false)

async function handleLogin() {
  const ok = await auth.login(form.username, form.password)
  if (ok) router.push('/dashboard')
}

function accesDemo() {
  auth.demoLogin()
  router.push('/dashboard')
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0d2b5e 0%, #1a4a9e 50%, #0d2b5e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.login-card {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 25px 60px rgba(0,0,0,0.3);
}

.login-logo { display: flex; align-items: center; gap: 14px; margin-bottom: 24px; }

.login-logo-icon {
  width: 52px; height: 52px;
  background: var(--color-primary);
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.login-logo-icon svg { width: 28px; height: 28px; color: #fff; }

.login-brand  { font-size: 18px; font-weight: 700; color: var(--color-primary); line-height: 1.2; }
.login-module { font-size: 12px; color: var(--color-text-muted); margin-top: 2px; }

.login-divider { height: 1px; background: var(--color-border); margin-bottom: 24px; }
.login-title   { font-size: 22px; font-weight: 700; color: var(--color-text); margin-bottom: 4px; }
.login-subtitle { font-size: 13px; color: var(--color-text-muted); margin-bottom: 20px; }

.alert-error {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 12px 14px; background: var(--color-error-bg); color: var(--color-error);
  border-radius: 8px; font-size: 13px; margin-bottom: 16px; line-height: 1.4;
}
.alert-error svg { width: 18px; height: 18px; flex-shrink: 0; margin-top: 1px; }

.login-form { display: flex; flex-direction: column; gap: 16px; }

.password-label-row {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 0;
}

.forgot-link {
  font-size: 12px; color: var(--color-primary); background: none; border: none;
  cursor: pointer; text-decoration: underline; padding: 0; line-height: 1;
}
.forgot-link:hover { opacity: 0.75; }

/* Conteneur pour icône gauche (et optionnellement droite) */
.input-icon-wrap {
  position: relative; display: flex; align-items: center;
}

.input-icon-left {
  position: absolute; left: 11px; top: 50%; transform: translateY(-50%);
  width: 18px; height: 18px; color: #94a3b8; pointer-events: none; flex-shrink: 0;
}

/* Padding interne de l'input selon les icônes présentes */
.form-control.input-with-icon-left  { padding-left: 38px; }
.form-control.input-with-icon-right { padding-right: 44px; }

.password-toggle {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer; color: var(--color-text-muted);
  padding: 4px; border-radius: 4px; display: flex;
}
.password-toggle:hover { color: var(--color-text); background: #f1f5f9; }
.password-toggle svg { width: 18px; height: 18px; }

.login-btn {
  width: 100%; justify-content: center; padding: 12px; font-size: 15px; margin-top: 4px;
}
.login-btn:disabled { opacity: 0.7; cursor: not-allowed; }

.login-footer {
  text-align: center; font-size: 12px; color: var(--color-text-muted); margin-top: 24px;
}

.modal-overlay {
  position: fixed; inset: 0; background: rgba(15,23,42,0.5);
  display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 24px;
}

.forgot-modal {
  background: #fff; border-radius: 12px; padding: 28px; max-width: 380px; width: 100%;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}
.forgot-modal h3 { font-size: 18px; font-weight: 600; color: var(--color-text); margin-bottom: 12px; }
.forgot-modal p  { font-size: 14px; color: var(--color-text-muted); line-height: 1.5; }

.forgot-contact {
  display: flex; align-items: center; gap: 8px;
  margin-top: 16px; padding: 10px 14px;
  background: var(--color-info-bg); color: var(--color-info);
  border-radius: 8px; font-size: 14px; font-weight: 500;
}

.demo-separator {
  display: flex; align-items: center; gap: 12px; margin: 4px 0;
  color: var(--color-text-muted); font-size: 12px;
}
.demo-separator::before, .demo-separator::after {
  content: ''; flex: 1; height: 1px; background: var(--color-border);
}

.btn-demo {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  width: 100%; padding: 10px;
  background: #f8fafc; border: 1.5px dashed #94a3b8; border-radius: var(--radius);
  color: #475569; font-size: 13.5px; font-weight: 500; cursor: pointer;
  transition: all 0.15s;
}
.btn-demo:hover:not(:disabled) { background: #f1f5f9; border-color: var(--color-primary); color: var(--color-primary); }
.btn-demo:disabled { opacity: 0.6; cursor: not-allowed; }

.spinner-sm {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
