<template>
  <div class="admin-shell">
    <aside class="side">
      <h2 class="title">绠＄悊鍚庡彴</h2>

      <div class="menu-group">
        <p class="group-title">杩愯惀鐪嬫澘</p>
        <router-link to="/admin/overview">杩愯惀鎬昏</router-link>
        <router-link to="/admin/report">杩愯惀鎶ヨ〃</router-link>
      </div>

      <div class="menu-group">
        <p class="group-title">鍐呭绠＄悊</p>
        <router-link to="/admin/knowledge/list">鐭ヨ瘑鍒楄〃</router-link>
        <router-link to="/admin/knowledge/upload">鏂囦欢涓婁紶</router-link>
        <router-link to="/admin/category/tree">分类树</router-link>
        <router-link to="/admin/entity/confirm">瀹炰綋纭</router-link>
        <router-link to="/admin/entity/graph">知识图谱</router-link>
      </div>

      <div class="menu-group">
        <p class="group-title">绯荤粺绠＄悊</p>
        <router-link to="/admin/task/monitor">浠诲姟鐩戞帶</router-link>
        <router-link to="/admin/user/manage">鐢ㄦ埛绠＄悊</router-link>
        <router-link to="/admin/system/notice">鍏憡绠＄悊</router-link>
      </div>
    </aside>

    <main class="main">
      <header class="top">
        <strong>AI 美业知识库 · 管理端</strong>
        <div class="top-actions">
          <ThemeModeSwitch />
          <el-button size="small" @click="onLogout">退出登录</el-button>
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
  width: 250px;
  overflow-y: auto;
  padding: 20px 14px;
  background: var(--admin-side-bg);
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
  color: var(--admin-group-title);
  font-size: 12px;
  letter-spacing: 0.06em;
}

.side a {
  color: var(--admin-side-link);
  text-decoration: none;
  padding: 12px 14px;
  border-radius: 10px;
  transition: background-color 0.2s ease;
}

.side a:hover {
  background: var(--admin-side-hover);
}

.side a.router-link-active {
  background: var(--admin-side-link-active);
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
  background: var(--topbar-bg);
  color: var(--topbar-text);
  border-bottom: 1px solid var(--app-border);
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 8px;
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
