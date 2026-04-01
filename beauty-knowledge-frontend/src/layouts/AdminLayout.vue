<template>
  <div class="admin-shell">
    <aside class="side">
      <div class="brand">
        <h2 class="title">管理后台</h2>
        <p class="subtitle">Beauty Knowledge Console</p>
      </div>

      <div class="menu-group">
        <p class="group-title">运营看板</p>
        <router-link to="/admin/overview">运营总览</router-link>
        <router-link to="/admin/report">运营报表</router-link>
      </div>

      <div class="menu-group">
        <p class="group-title">内容管理</p>
        <router-link to="/admin/knowledge/list">知识列表</router-link>
        <router-link to="/admin/knowledge/upload">文件上传</router-link>
        <router-link to="/admin/category/tree">分类树</router-link>
        <router-link to="/admin/entity/confirm">实体确认</router-link>
        <router-link to="/admin/entity/graph">知识图谱</router-link>
      </div>

      <div class="menu-group">
        <p class="group-title">系统管理</p>
        <router-link to="/admin/task/monitor">任务监控</router-link>
        <router-link to="/admin/user/manage">用户管理</router-link>
        <router-link to="/admin/system/notice">公告管理</router-link>
      </div>

      <p class="side-footer">统一录入、关系沉淀、问答展示</p>
    </aside>

    <main class="main">
      <header class="top">
        <strong class="top-title">AI 美业知识库 · 管理端</strong>
        <div class="top-actions">
          <ThemeModeSwitch />
          <el-button size="small" class="logout" @click="onLogout">退出登录</el-button>
        </div>
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
.admin-shell {
  min-height: 100vh;
  background: var(--admin-shell-bg);
}

.side {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 260px;
  overflow-y: auto;
  padding: 20px 14px;
  background: var(--admin-side-bg);
  color: #fff;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: 10px 0 32px rgba(2, 8, 23, 0.25);
}

.brand {
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.title {
  margin: 0;
  font-size: 32px;
  line-height: 1.15;
  letter-spacing: 0.01em;
}

.subtitle {
  margin: 8px 0 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.72);
}

.menu-group {
  display: grid;
  gap: 8px;
}

.group-title {
  margin: 0;
  color: var(--admin-group-title);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.side a {
  color: var(--admin-side-link);
  text-decoration: none;
  padding: 11px 14px;
  border-radius: 10px;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.side a:hover {
  background: var(--admin-side-hover);
  transform: translateX(2px);
}

.side a.router-link-active {
  background: var(--admin-side-link-active);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.25);
}

.side-footer {
  margin: auto 6px 4px;
  font-size: 12px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.62);
}

.main {
  margin-left: 260px;
  min-width: 0;
}

.top {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 18px;
  background: var(--topbar-bg);
  color: var(--topbar-text);
  border-bottom: 1px solid var(--app-border);
  backdrop-filter: blur(8px);
}

.top-title {
  letter-spacing: 0.01em;
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logout {
  border-radius: 10px;
}

.content {
  padding: 16px;
}

@media (max-width: 980px) {
  .side {
    position: static;
    width: 100%;
    height: auto;
    overflow-x: auto;
    overflow-y: hidden;
    display: flex;
    flex-direction: row;
    gap: 14px;
    padding: 10px;
    box-shadow: none;
  }

  .brand,
  .side-footer {
    display: none;
  }

  .menu-group {
    display: grid;
    grid-auto-flow: column;
    align-items: center;
    gap: 8px;
  }

  .group-title {
    display: none;
  }

  .main {
    margin-left: 0;
  }

  .top {
    position: static;
    height: auto;
    padding: 10px 12px;
    gap: 10px;
    flex-wrap: wrap;
  }
}
</style>
