<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Utilisateurs</h1>
        <p class="page-subtitle">{{ store.list.length }} compte(s) enregistré(s)</p>
      </div>
      <button class="btn btn-primary" @click="openCreate">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:16px;height:16px">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zM4 19.235v-.11a6.375 6.375 0 0112.75 0v.109A12.318 12.318 0 0110.374 21c-2.331 0-4.512-.645-6.374-1.766z" />
        </svg>
        Créer un utilisateur
      </button>
    </div>

    <div class="card">
      <div v-if="store.loading" class="loading-state"><div class="spinner" />Chargement…</div>
      <template v-else>
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>USERNAME</th><th>EMAIL</th><th>PROFIL</th>
                <th>STATUT</th><th>DERNIÈRE CONNEXION</th><th>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!store.list.length"><td colspan="6"><div class="empty-state">Aucun utilisateur.</div></td></tr>
              <tr v-for="user in store.list" :key="user.id">
                <td>
                  <div class="user-cell">
                    <div class="user-avatar">{{ user.username[0].toUpperCase() }}</div>
                    <span class="mono">{{ user.username }}</span>
                  </div>
                </td>
                <td class="text-sm">{{ user.email }}</td>
                <td><span class="profil-badge" :class="profilClass(user.profil)">{{ user.profil }}</span></td>
                <td>
                  <span class="status-dot" :class="user.actif ? 'dot-active' : 'dot-inactive'">
                    {{ user.actif ? 'Actif' : 'Inactif' }}
                  </span>
                </td>
                <td class="text-sm text-muted">{{ user.derniere_connexion ? formatDate(user.derniere_connexion) : 'Jamais' }}</td>
                <td>
                  <div class="action-btns">
                    <button class="btn-link" @click="openEdit(user)">Modifier</button>
                    <button class="btn-link" @click="openChangePwd(user)">Changer MDP</button>
                    <button class="btn-link" :class="user.actif ? 'btn-link-danger' : 'btn-link-success'" @click="askToggle(user)">
                      {{ user.actif ? 'Désactiver' : 'Activer' }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>

    <!-- ───── MODALE CRÉER / MODIFIER UTILISATEUR ───── -->
    <AppModal
      v-model="showUserModal"
      :title="editingUser ? `Modifier — ${editingUser.username}` : 'Créer un utilisateur'"
      width="520px"
    >
      <form @submit.prevent="submitForm" id="user-form" class="user-form">
        <div class="form-row-2">
          <div class="form-group">
            <label class="form-label">Nom d'utilisateur <span class="required">*</span></label>
            <input v-model="userForm.username" type="text" class="form-control"
              placeholder="ex: a.kone" required :disabled="!!editingUser" />
            <small v-if="editingUser" class="form-hint">Non modifiable.</small>
          </div>
          <div class="form-group">
            <label class="form-label">Profil <span class="required">*</span></label>
            <select v-model="userForm.profil" class="form-control" required>
              <option value="">Sélectionner…</option>
              <option v-for="p in PROFILS" :key="p" :value="p">{{ p }}</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Email <span class="required">*</span></label>
          <input v-model="userForm.email" type="email" class="form-control"
            placeholder="prenom.nom@liceli.bf" required />
        </div>

        <template v-if="!editingUser">
          <div class="form-group">
            <label class="form-label">Mot de passe <span class="required">*</span></label>
            <div class="password-field">
              <input v-model="userForm.password" :type="showPwd ? 'text' : 'password'"
                class="form-control" placeholder="Mot de passe initial" required minlength="8" />
              <button type="button" class="password-toggle" @click="showPwd = !showPwd">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:18px;height:18px">
                  <path v-if="!showPwd" stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path v-else stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                </svg>
              </button>
            </div>
            <small class="form-hint">Minimum 8 caractères.</small>
          </div>
          <div class="form-group">
            <label class="form-label">Confirmer le mot de passe <span class="required">*</span></label>
            <div class="password-field">
              <input v-model="userForm.passwordConfirm" :type="showPwd2 ? 'text' : 'password'"
                class="form-control" placeholder="Répéter le mot de passe" required />
              <button type="button" class="password-toggle" @click="showPwd2 = !showPwd2">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:18px;height:18px">
                  <path v-if="!showPwd2" stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path v-else stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                </svg>
              </button>
            </div>
            <small v-if="pwdMismatch" class="form-error-inline">Les mots de passe ne correspondent pas.</small>
          </div>
        </template>

        <div class="form-error" v-if="store.error">{{ store.error }}</div>
      </form>

      <template #footer>
        <button class="btn btn-secondary" @click="showUserModal = false">Annuler</button>
        <button class="btn btn-primary" type="submit" form="user-form" :disabled="store.saving">
          <span v-if="store.saving" class="spinner-sm" />
          {{ editingUser ? 'Enregistrer' : 'Créer le compte' }}
        </button>
      </template>
    </AppModal>

    <!-- ───── MODALE CHANGER MOT DE PASSE ───── -->
    <AppModal v-model="showPwdModal" :title="pwdUser ? `Changer le mot de passe — ${pwdUser.username}` : ''" width="420px">
      <div class="user-form">
        <div class="form-group">
          <label class="form-label">Nouveau mot de passe</label>
          <div class="password-field">
            <input v-model="pwdForm.password" :type="showNewPwd ? 'text' : 'password'"
              class="form-control" placeholder="Nouveau mot de passe" />
            <button type="button" class="password-toggle" @click="showNewPwd = !showNewPwd">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:18px;height:18px">
                <path v-if="!showNewPwd" stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path v-else stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
              </svg>
            </button>
          </div>
          <!-- Indicateur de force -->
          <div v-if="pwdForm.password" class="pwd-strength-wrap">
            <div class="pwd-strength-bar">
              <div class="pwd-strength-fill" :class="pwdStrengthClass" :style="{ width: pwdStrengthPct + '%' }"></div>
            </div>
            <span class="pwd-strength-label" :class="pwdStrengthClass">{{ pwdStrengthLabel }}</span>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Confirmer le mot de passe</label>
          <div class="password-field">
            <input v-model="pwdForm.confirm" :type="showConfPwd ? 'text' : 'password'"
              class="form-control" placeholder="Répéter le mot de passe" />
            <button type="button" class="password-toggle" @click="showConfPwd = !showConfPwd">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="width:18px;height:18px">
                <path v-if="!showConfPwd" stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path v-else stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
              </svg>
            </button>
          </div>
          <small v-if="pwdForm.confirm && pwdForm.password !== pwdForm.confirm" class="form-error-inline">
            Les mots de passe ne correspondent pas.
          </small>
        </div>
      </div>

      <template #footer>
        <button class="btn btn-secondary" @click="showPwdModal = false">Annuler</button>
        <button class="btn btn-primary" :disabled="!canSavePwd" @click="savePwd">
          Enregistrer le mot de passe
        </button>
      </template>
    </AppModal>

    <!-- ───── MODALE CONFIRMATION DÉSACTIVATION ───── -->
    <ConfirmModal
      v-model="showConfirm"
      :title="confirmData.title"
      :message="confirmData.message"
      :confirm-text="confirmData.confirmText"
      :variant="confirmData.variant"
      @confirm="executeToggle"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useUsersStore, PROFILS } from '@/stores/users'
import AppModal from '@/components/common/AppModal.vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'
import { formatDate } from '@/utils/format'

const store = useUsersStore()
const showUserModal = ref(false)
const showPwd = ref(false)
const showPwd2 = ref(false)
const editingUser = ref(null)
const userForm = reactive({ username: '', email: '', profil: '', password: '', passwordConfirm: '' })

const showPwdModal = ref(false)
const pwdUser = ref(null)
const pwdForm = reactive({ password: '', confirm: '' })
const showNewPwd = ref(false)
const showConfPwd = ref(false)

const showConfirm = ref(false)
const confirmData = reactive({ title: '', message: '', confirmText: '', variant: 'warning' })
const pendingToggleUser = ref(null)

onMounted(() => store.fetchList())

const pwdMismatch = computed(() =>
  userForm.passwordConfirm.length > 0 && userForm.password !== userForm.passwordConfirm
)

const pwdStrength = computed(() => {
  const p = pwdForm.password
  if (!p) return 0
  let score = 0
  if (p.length >= 8)  score++
  if (p.length >= 12) score++
  if (/[A-Z]/.test(p)) score++
  if (/[0-9]/.test(p)) score++
  if (/[^A-Za-z0-9]/.test(p)) score++
  return score
})

const pwdStrengthPct = computed(() => [0, 33, 33, 66, 100, 100][pwdStrength.value] ?? 0)
const pwdStrengthLabel = computed(() => ['', 'Faible', 'Faible', 'Moyen', 'Fort', 'Fort'][pwdStrength.value] ?? '')
const pwdStrengthClass = computed(() => {
  const s = pwdStrength.value
  if (s <= 2) return 'strength-weak'
  if (s <= 3) return 'strength-medium'
  return 'strength-strong'
})

const canSavePwd = computed(() =>
  pwdForm.password.length >= 8 && pwdForm.password === pwdForm.confirm
)

function profilClass(p) {
  switch (p) {
    case 'Administrateur':    return 'profil-admin'
    case 'Responsable MB':    return 'profil-resp'
    case 'Agent Back-Office': return 'profil-agent'
    default: return 'profil-agent'
  }
}

function openCreate() {
  editingUser.value = null
  Object.assign(userForm, { username: '', email: '', profil: '', password: '', passwordConfirm: '' })
  store.error = null
  showPwd.value = false
  showPwd2.value = false
  showUserModal.value = true
}

function openEdit(user) {
  editingUser.value = user
  Object.assign(userForm, { username: user.username, email: user.email, profil: user.profil, password: '', passwordConfirm: '' })
  store.error = null
  showUserModal.value = true
}

function openChangePwd(user) {
  pwdUser.value = user
  Object.assign(pwdForm, { password: '', confirm: '' })
  showNewPwd.value = false
  showConfPwd.value = false
  showPwdModal.value = true
}

function savePwd() {
  if (!canSavePwd.value) return
  showPwdModal.value = false
}

async function submitForm() {
  if (!editingUser.value && userForm.password !== userForm.passwordConfirm) return
  if (editingUser.value) {
    const ok = await store.updateUser(editingUser.value.id, { email: userForm.email, profil: userForm.profil })
    if (ok) showUserModal.value = false
  } else {
    const ok = await store.createUser({ ...userForm })
    if (ok) showUserModal.value = false
  }
}

function askToggle(user) {
  pendingToggleUser.value = user
  if (user.actif) {
    Object.assign(confirmData, {
      title: `Désactiver ${user.username} ?`,
      message: `Cet utilisateur ne pourra plus accéder au système.`,
      confirmText: 'Désactiver',
      variant: 'danger'
    })
  } else {
    Object.assign(confirmData, {
      title: `Activer ${user.username} ?`,
      message: `Le compte ${user.username} sera réactivé. L'utilisateur pourra de nouveau accéder au système.`,
      confirmText: 'Activer',
      variant: 'info'
    })
  }
  showConfirm.value = true
}

async function executeToggle() {
  if (!pendingToggleUser.value) return
  await store.toggleActive(pendingToggleUser.value.id)
  pendingToggleUser.value = null
}
</script>

<style scoped>
.mono { font-family: 'Courier New', monospace; font-size: 12px; }
.user-cell { display: flex; align-items: center; gap: 10px; }
.user-avatar { width: 30px; height: 30px; border-radius: 50%; background: var(--color-primary); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; flex-shrink: 0; }
.profil-badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.profil-admin { background: #eef2ff; color: #4338ca; }
.profil-resp  { background: #f0fdf4; color: #15803d; }
.profil-agent { background: #fff7ed; color: #c2410c; }
.status-dot { display: flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 500; }
.status-dot::before { content: ''; width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.dot-active { color: var(--color-success); }
.dot-active::before { background: var(--color-success); }
.dot-inactive { color: var(--color-text-muted); }
.dot-inactive::before { background: #cbd5e1; }

/* Boutons texte discrets */
.action-btns { display: flex; gap: 10px; }
.btn-link { background: none; border: none; font-size: 12px; font-weight: 500; color: var(--color-primary); cursor: pointer; padding: 0; text-decoration: underline; text-underline-offset: 2px; }
.btn-link:hover { opacity: 0.75; }
.btn-link-danger { color: var(--color-error); }
.btn-link-danger:hover { color: #991b1b; }
.btn-link-success { color: var(--color-success); }
.btn-link-success:hover { color: #15803d; }

/* Modal form */
.user-form { display: flex; flex-direction: column; gap: 14px; }
.form-row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.required { color: var(--color-error); }
.form-hint { font-size: 12px; color: var(--color-text-muted); margin-top: 4px; display: block; }
.form-error-inline { font-size: 12px; color: var(--color-error); margin-top: 4px; display: block; }
.password-field { position: relative; }
.password-field .form-control { padding-right: 44px; width: 100%; box-sizing: border-box; }
.password-toggle { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; color: var(--color-text-muted); padding: 4px; display: flex; border-radius: 4px; }
.password-toggle:hover { color: var(--color-text); background: #f1f5f9; }
.form-error { padding: 10px 14px; background: var(--color-error-bg); color: var(--color-error); border-radius: 8px; font-size: 13px; }

/* Indicateur de force */
.pwd-strength-wrap { display: flex; align-items: center; gap: 10px; margin-top: 6px; }
.pwd-strength-bar { flex: 1; height: 4px; background: #e2e8f0; border-radius: 2px; overflow: hidden; }
.pwd-strength-fill { height: 100%; border-radius: 2px; transition: width 0.3s, background 0.3s; }
.pwd-strength-label { font-size: 12px; font-weight: 600; width: 50px; text-align: right; }
.strength-weak   .pwd-strength-fill, .strength-weak   { color: var(--color-error);   }
.strength-weak   .pwd-strength-fill { background: var(--color-error); }
.strength-medium .pwd-strength-fill, .strength-medium { color: var(--color-warning); }
.strength-medium .pwd-strength-fill { background: var(--color-warning); }
.strength-strong .pwd-strength-fill, .strength-strong { color: var(--color-success); }
.strength-strong .pwd-strength-fill { background: var(--color-success); }

.spinner-sm { width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.3); border-top-color: #fff; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
