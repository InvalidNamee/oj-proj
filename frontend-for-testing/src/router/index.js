import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/home',
      name: 'home',
      component: () => import('@/views/home.vue'),
      meta: { title: '首页' }
    },
    {
      path: '/auth-test',
      name: 'auth-test',
      component: () => import('@/views/AuthTesting.vue'),
      meta: { title: '认证测试'}
    },
    {
      path: '/user-test',
      name: 'user-test',
      component: () => import('@/views/UserTesting.vue'),
      meta: { title: '用户功能测试' }
    },
    {
      path: '/test',
      name: 'test',
      component: () => import('@/views/test.vue'),
      meta: { title: '测试性功能' }
    },
    {
      path: '/coding-test',
      name: 'coding-test',
      component: () => import('@/views/CodingTesting.vue'),
      meta: { title: '编程题测试'}
    },
    {
      path: '/legacy-test',
      name: 'legacy-test',
      component: () => import('@/views/LegacyTesting.vue'),
      meta: { title: '传统题测试'}
    },
    {
      path: '/problemset-test',
      name: 'problemset-test',
      component: () => import('@/views/ProblemsetTesting.vue'),
      meta: { title: '题单测试'}
    }
  ],
})

export default router
