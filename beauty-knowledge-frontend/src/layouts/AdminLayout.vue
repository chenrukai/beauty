<template>
  <div class="admin-shell">
    <aside class="side">
      <h2 class="title">管理后台</h2>

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
      </div>

      <div class="menu-group">
        <p class="group-title">系统管理</p>
        <router-link to="/admin/task/monitor">任务监控</router-link>
        <router-link to="/admin/user/manage">用户管理</router-link>
        <router-link to="/admin/system/notice">公告管理</router-link>
      </div>
    </aside>

    <main class="main">
      <header class="top">
        <strong>AI 美业知识台 · 管理员</strong>
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
  background: #f4f7f7;
}

.side {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 250px;
  overflow-y: auto;
  padding: 20px 14px;
  background: linear-gradient(180deg, #123531 0%, #0c2522 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.title {
  margin: 0;
  font-size: 34px;
  line-height: 1.2;
  letter-spacing: 0.02em;
}

.menu-group {
  display: grid;
  gap: 8px;
}

.group-title {
  margin: 0;
  color: #8fd8c9;
  font-size: 12px;
  letter-spacing: 0.06em;
}

.side a {
  color: #dcfce7;
  text-decoration: none;
  padding: 12px 14px;
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
  margin-left: 250px;
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
    display: flex;
    flex-direction: row;
    gap: 18px;
    padding: 12px;
  }

  .title {
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
  }
}
</style>
