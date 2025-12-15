/**
 * 路由配置
 * 定义应用的所有路由
 */
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/regulations',
    },
    {
      path: '/regulations',
      name: 'Regulations',
      component: () => import('@/views/Regulations.vue'),
      meta: { title: '制度文件管理' },
    },
    {
      path: '/documents',
      name: 'Documents',
      component: () => import('@/views/Documents.vue'),
      meta: { title: '员工文档管理' },
    },
    {
      path: '/reviews',
      name: 'Reviews',
      component: () => import('@/views/Reviews.vue'),
      meta: { title: '合规审查' },
    },
    {
      path: '/annotations',
      name: 'Annotations',
      component: () => import('@/views/Annotations.vue'),
      meta: { title: '标注管理' },
    },
  ],
})

export default router

