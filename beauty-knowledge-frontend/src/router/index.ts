import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginPage from '../views/LoginPage.vue'
import AdminLayout from '../layouts/AdminLayout.vue'
import UserLayout from '../layouts/UserLayout.vue'
import ChatPage from '../views/user/Chat.vue'
import UserHomePage from '../views/user/Home.vue'
import UserFavoritesPage from '../views/user/Favorites.vue'
import AdminOverviewPage from '../views/admin/Overview.vue'
import FileUploadPage from '../views/admin/knowledge/FileUpload.vue'
import KnowledgeListPage from '../views/admin/knowledge/KnowledgeList.vue'
import CategoryTreePage from '../views/admin/category/CategoryTree.vue'
import ExtractConfirmPage from '../views/admin/entity/ExtractConfirm.vue'
import TaskMonitorPage from '../views/admin/task/TaskMonitor.vue'
import UserManagePage from '../views/admin/user/UserManage.vue'
import NoticeManagePage from '../views/admin/system/NoticeManage.vue'
import AdminReportPage from '../views/admin/Report.vue'

const routes: RouteRecordRaw[] = [
  { path: '/login', component: LoginPage, meta: { requiresAuth: false } },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      { path: 'overview', component: AdminOverviewPage },
      { path: 'report', component: AdminReportPage },
      { path: 'knowledge/upload', component: FileUploadPage },
      { path: 'knowledge/list', component: KnowledgeListPage },
      { path: 'category/tree', component: CategoryTreePage },
      { path: 'entity/confirm', component: ExtractConfirmPage },
      { path: 'task/monitor', component: TaskMonitorPage },
      { path: 'user/manage', component: UserManagePage },
      { path: 'system/notice', component: NoticeManagePage },
      { path: '', redirect: '/admin/overview' }
    ]
  },
  {
    path: '/user',
    component: UserLayout,
    meta: { requiresAuth: true, role: 'user' },
    children: [
      { path: 'home', component: UserHomePage },
      { path: 'chat', component: ChatPage },
      { path: 'favorites', component: UserFavoritesPage },
      { path: '', redirect: '/user/home' }
    ]
  },
  { path: '/', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth === false) {
    return true
  }
  if (!auth.isLoggedIn || !auth.token) {
    return '/login'
  }
  const role = String(auth.userInfo?.role || '').toLowerCase()
  if (to.meta.role && role !== String(to.meta.role)) {
    return role === 'admin' ? '/admin' : '/user/home'
  }
  return true
})

export default router
