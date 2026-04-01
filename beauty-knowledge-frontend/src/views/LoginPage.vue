<template>
  <div class="login-page">
    <section class="hero-panel">
      <div class="hero-copy">
        <p class="eyebrow">美业知识控制台</p>
        <h1>把门店知识、产品理解和用户问答放进一个更顺手的工作台。</h1>
        <p class="intro">
          面向真实业务场景的登录入口，既要清晰，也要好用。当前支持管理员与普通用户两类入口，注册仅开放普通用户。
        </p>
      </div>

      <div class="hero-metrics">
        <div class="metric-card">
          <span class="metric-label">适用场景</span>
          <strong>门店咨询 / 培训 / 知识问答</strong>
        </div>
        <div class="metric-card">
          <span class="metric-label">账号策略</span>
          <strong>仅注册普通用户</strong>
        </div>
        <div class="metric-card">
          <span class="metric-label">推荐路径</span>
          <strong>先登录，再进入用户问答台</strong>
        </div>
      </div>
    </section>

    <section class="auth-panel">
      <div class="panel-tools">
        <ThemeModeSwitch />
      </div>

      <div class="panel-head">
        <p class="panel-kicker">{{ isRegister ? '创建普通用户账号' : '欢迎回来' }}</p>
        <h2>{{ isRegister ? '注册后即可登录使用' : '登录 AI 美业知识库' }}</h2>
        <p class="panel-note">
          {{ isRegister ? '注册不会创建管理员权限，也不需要填写邮箱。' : '请输入你的账号和密码登录。' }}
        </p>
      </div>

      <el-form @submit.prevent class="auth-form">
        <el-form-item>
          <el-input
            v-model.trim="form.username"
            placeholder="用户名（3-32 位）"
            size="large"
            autocomplete="username"
          />
        </el-form-item>

        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码（6-64 位）"
            size="large"
            autocomplete="current-password"
            show-password
            @keyup.enter="submitPrimary"
          />
        </el-form-item>

        <el-form-item v-if="isRegister">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认密码"
            size="large"
            autocomplete="new-password"
            show-password
            @keyup.enter="submitPrimary"
          />
        </el-form-item>

        <el-button type="primary" class="primary-btn" :loading="loading" @click="submitPrimary">
          {{ isRegister ? '注册普通用户' : '登录系统' }}
        </el-button>
      </el-form>

      <div class="switch-row">
        <span>{{ isRegister ? '已经有账号了？' : '还没有账号？' }}</span>
        <button class="mode-switch" type="button" @click="toggleMode">
          {{ isRegister ? '返回登录' : '点击注册' }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import ThemeModeSwitch from '../components/common/ThemeModeSwitch.vue'

const auth = useAuthStore()
const router = useRouter()
const loading = ref(false)
const mode = ref<'login' | 'register'>('login')

const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const isRegister = computed(() => mode.value === 'register')

function resetRegisterFields() {
  form.password = ''
  form.confirmPassword = ''
}

function toggleMode() {
  mode.value = isRegister.value ? 'login' : 'register'
  resetRegisterFields()
}

async function onLogin() {
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    const role = String(auth.userInfo?.role || '').toLowerCase()
    await router.push(role === 'admin' ? '/admin' : '/user/home')
  } catch (e: any) {
    ElMessage.error(e?.message || '登录失败')
  } finally {
    loading.value = false
  }
}

async function onRegister() {
  if (form.password !== form.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  loading.value = true
  try {
    await auth.register(form.username, form.password)
    ElMessage.success('注册成功，请登录')
    mode.value = 'login'
    form.password = ''
    form.confirmPassword = ''
  } catch (e: any) {
    ElMessage.error(e?.message || '注册失败')
  } finally {
    loading.value = false
  }
}

async function submitPrimary() {
  if (isRegister.value) {
    await onRegister()
    return
  }
  await onLogin()
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  padding: 32px;
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(360px, 480px);
  gap: 28px;
  align-items: stretch;
}

.hero-panel,
.auth-panel {
  position: relative;
  overflow: hidden;
  border-radius: 28px;
  border: 1px solid rgba(26, 70, 62, 0.08);
  box-shadow: var(--app-shadow-md);
}

.hero-panel {
  padding: 48px;
  display: grid;
  align-content: space-between;
  background:
    radial-gradient(circle at top left, rgba(255, 247, 223, 0.9), transparent 32%),
    linear-gradient(135deg, #0f766e 0%, #17594f 48%, #f4ede0 48%, #f9f5ec 100%);
  color: #fcfaf3;
}

.hero-panel::after {
  content: '';
  position: absolute;
  inset: auto -60px -80px auto;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: rgba(255, 244, 214, 0.28);
  filter: blur(4px);
}

.hero-copy {
  max-width: 620px;
  position: relative;
  z-index: 1;
}

.eyebrow,
.panel-kicker,
.metric-label {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.eyebrow {
  color: rgba(255, 247, 223, 0.84);
}

h1 {
  margin: 18px 0 16px;
  font-size: clamp(34px, 4.4vw, 58px);
  line-height: 1.05;
  letter-spacing: -0.04em;
}

.intro {
  margin: 0;
  max-width: 520px;
  font-size: 17px;
  line-height: 1.8;
  color: rgba(252, 250, 243, 0.88);
}

.hero-metrics {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.metric-card {
  padding: 18px;
  border-radius: 20px;
  background: rgba(255, 251, 240, 0.12);
  border: 1px solid rgba(255, 251, 240, 0.18);
  backdrop-filter: blur(10px);
}

.metric-card strong {
  display: block;
  margin-top: 8px;
  font-size: 15px;
  line-height: 1.6;
}

.metric-label {
  color: rgba(255, 247, 223, 0.76);
}

.auth-panel {
  padding: 36px;
  align-self: center;
  background:
    radial-gradient(circle at top right, rgba(15, 118, 110, 0.08), transparent 32%),
    linear-gradient(180deg, #fffdf8 0%, #f8f4ea 100%);
}

.panel-tools {
  display: flex;
  justify-content: flex-end;
}

.panel-head h2 {
  margin: 8px 0 8px;
  font-size: 44px;
  line-height: 1.12;
  color: #0f4741;
  letter-spacing: -0.04em;
}

.panel-kicker {
  color: #9a7d4f;
}

.panel-note {
  margin: 0;
  color: #47625f;
  line-height: 1.8;
  font-size: 16px;
}

.auth-form {
  margin-top: 24px;
}

.auth-form :deep(.el-input__wrapper) {
  border-radius: 18px;
  padding: 10px 16px;
  box-shadow: 0 0 0 1px rgba(15, 71, 65, 0.1) inset;
}

.primary-btn {
  width: 100%;
  margin-top: 8px;
  height: 48px;
  border-radius: 20px;
  font-size: 18px;
  letter-spacing: 0.05em;
  background: linear-gradient(135deg, #0f766e 0%, #2f8f82 100%);
  border: none;
}

.switch-row {
  margin-top: 22px;
  display: flex;
  justify-content: center;
  gap: 8px;
  color: #5f726f;
  font-size: 16px;
}

.mode-switch {
  border: none;
  background: transparent;
  color: #0f766e;
  font-weight: 600;
  cursor: pointer;
  font-size: 16px;
}

html[data-theme='night'] .hero-panel {
  background:
    radial-gradient(circle at top left, rgba(125, 194, 255, 0.18), transparent 32%),
    linear-gradient(135deg, #19324d 0%, #18263b 48%, #111a2a 48%, #121d2e 100%);
  color: #eef5ff;
}

html[data-theme='night'] .auth-panel {
  background:
    radial-gradient(circle at top right, rgba(125, 194, 255, 0.12), transparent 32%),
    linear-gradient(180deg, #1b2739 0%, #162234 100%);
  border-color: rgba(125, 194, 255, 0.18);
}

html[data-theme='night'] .panel-head h2,
html[data-theme='night'] .panel-note,
html[data-theme='night'] .switch-row {
  color: #dbe8fb;
}

html[data-theme='night'] .panel-kicker {
  color: #9ec8ff;
}

html[data-theme='night'] .mode-switch {
  color: #9ec8ff;
}

@media (max-width: 1180px) {
  .login-page {
    grid-template-columns: 1fr;
    padding: 18px;
  }

  .hero-panel {
    min-height: 360px;
  }

  .hero-metrics {
    grid-template-columns: 1fr;
  }

  .auth-panel {
    padding: 26px;
  }
}
</style>
