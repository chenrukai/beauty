<template>
  <div class="admin-shell">
    <aside class="side">
      <h2 class="title">管理后台</h2>
      <router-link to="/admin/overview">运营总览</router-link>
      <router-link to="/admin/knowledge/upload">文件上传</router-link>
      <router-link to="/admin/knowledge/list">知识列表</router-link>
      <router-link to="/admin/category/tree">分类树</router-link>
      <router-link to="/admin/entity/confirm">实体确认</router-link>
      <router-link to="/admin/task/monitor">任务监控</router-link>
    </aside>

    <main class="main">
      <header class="top">
        <strong>AI美业知识官 · Admin</strong>
        <el-button size="small" @click="onLogout">退出登录</el-button>
      </header>
      <section class="content">
        <router-view />
      </section>
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
.admin-shell {
  min-height: 100vh;
}

.side {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 240px;
  overflow-y: auto;
  padding: 20px 12px;
  background: #123531;
  color: #fff;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.title {
  margin: 0 0 12px;
  font-size: 40px;
  line-height: 1.2;
}

.side a {
  color: #dcfce7;
  text-decoration: none;
  padding: 14px 16px;
  border-radius: 10px;
  transition: background-color 0.2s ease;
}

.side a:hover {
  background: rgba(15, 118, 110, 0.5);
}

.side a.router-link-active {
  background: #0f766e;
  color: #fff;
}

.main {
  margin-left: 240px;
  min-width: 0;
}

.top {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 16px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
}

.content {
  padding: 16px;
}

@media (max-width: 900px) {
  .side {
    position: static;
    width: 100%;
    height: auto;
    overflow-x: auto;
    overflow-y: hidden;
    display: grid;
    grid-auto-flow: column;
    grid-auto-columns: max-content;
    align-items: center;
  }

  .title {
    display: none;
  }

  .main {
    margin-left: 0;
  }

  .top {
    position: static;
  }
}
</style>
