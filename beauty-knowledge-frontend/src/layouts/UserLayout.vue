<template>
  <div class="user-shell">
    <header class="topbar">
      <div class="brand">
        <span class="brand-badge">Beauty Desk</span>
        <div>
          <strong>AI 美业知识台</strong>
          <p>面向咨询、学习和日常接待的用户工作区</p>
        </div>
      </div>

      <div class="actions">
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
  background:
    radial-gradient(circle at top left, rgba(255, 246, 220, 0.82), transparent 24%),
    linear-gradient(180deg, #f7f4ec 0%, #f0f5f2 100%);
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 20px 24px;
  background: rgba(15, 118, 110, 0.94);
  color: #fff;
  box-shadow: 0 16px 40px rgba(15, 118, 110, 0.2);
}

.brand {
  display: flex;
  align-items: center;
  gap: 16px;
}

.brand strong {
  display: block;
  font-size: 22px;
  letter-spacing: -0.02em;
}

.brand p {
  margin: 4px 0 0;
  color: rgba(255, 255, 255, 0.78);
}

.brand-badge {
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(255, 248, 223, 0.16);
  border: 1px solid rgba(255, 248, 223, 0.24);
  font-size: 12px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-pill {
  padding: 10px 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.1);
  min-width: 124px;
}

.user-pill .label {
  display: block;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.72);
}

.logout-btn {
  border: none;
  border-radius: 14px;
}

.shell-body {
  padding: 18px;
}

@media (max-width: 900px) {
  .topbar {
    padding: 18px;
    flex-direction: column;
    align-items: flex-start;
  }

  .actions {
    width: 100%;
    justify-content: space-between;
  }

  .shell-body {
    padding: 12px;
  }
}
</style>
