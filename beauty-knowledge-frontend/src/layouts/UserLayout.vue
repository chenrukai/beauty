<template>
  <div class="user-shell">
    <header class="topbar">
      <div class="brand">
        <span class="brand-badge">用户端</span>
        <div>
          <strong>AI 美业知识库</strong>
          <p>面向咨询、学习和日常接待的用户工作区。</p>
        </div>
      </div>

      <div class="actions">
        <nav class="main-nav">
          <router-link to="/user/home">首页</router-link>
          <router-link to="/user/chat">问答助手</router-link>
          <router-link to="/user/favorites">我的收藏</router-link>
        </nav>

        <ThemeModeSwitch />

        <div class="user-pill">
          <span class="label">当前账号</span>
          <strong>{{ auth.userInfo?.username || '未登录' }}</strong>
        </div>
        <el-button size="small" class="logout-btn" @click="onLogout">退出登录</el-button>
      </div>
    </header>

    <main class="shell-body">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import ThemeModeSwitch from '../components/common/ThemeModeSwitch.vue'

const auth = useAuthStore()
const router = useRouter()

async function onLogout() {
  try {
    await auth.logout()
    await router.push('/login')
  } catch {
    ElMessage.error('退出失败，请重试')
  }
}
</script>

<style scoped>
.user-shell {
  min-height: 100vh;
  background: var(--user-shell-bg);
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 16px 20px;
  background: var(--user-topbar-bg);
  color: var(--user-topbar-text);
  box-shadow: var(--user-topbar-shadow);
  backdrop-filter: blur(8px);
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand strong {
  display: block;
  font-size: 22px;
  letter-spacing: -0.02em;
}

.brand p {
  margin: 4px 0 0;
  color: var(--user-muted-text);
}

.brand-badge {
  padding: 9px 14px;
  border-radius: 999px;
  background: rgba(255, 248, 223, 0.16);
  border: 1px solid rgba(255, 248, 223, 0.24);
  font-size: 12px;
  letter-spacing: 0.04em;
}

.actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.main-nav {
  display: flex;
  align-items: center;
  gap: 8px;
}

.main-nav a {
  color: var(--user-nav-link);
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid transparent;
  transition: 0.2s ease;
}

.main-nav a:hover {
  border-color: var(--user-nav-border-hover);
}

.main-nav a.router-link-active {
  background: var(--user-nav-active-bg);
  color: var(--user-nav-active-text);
}

.user-pill {
  padding: 10px 14px;
  border-radius: 14px;
  background: var(--user-pill-bg);
  min-width: 124px;
}

.user-pill .label {
  display: block;
  font-size: 12px;
  color: var(--user-pill-label);
}

.logout-btn {
  border: none;
  border-radius: 12px;
}

.shell-body {
  padding: 18px;
}

@media (max-width: 980px) {
  .topbar {
    position: static;
    flex-direction: column;
    align-items: flex-start;
    padding: 14px;
  }

  .actions {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .shell-body {
    padding: 12px;
  }
}
</style>
