import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/Home.vue'),
      meta: { title: '首页', requiresAuth: true }
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue')
    },
    {
      path: '/users',
      name: 'Users',
      component: () => import('@/views/users/Layout.vue'),
      meta: { title: '用户管理', requiresAuth: true },
      children: [
        {
          path: '',
          name: 'UserList',
          component: () => import('@/views/users/List.vue'),
          meta: { title: '用户列表', requiresAuth: true }
        },
        {
          path: ':id',
          name: 'UserDetail',
          component: () => import('@/views/users/Detail.vue'),
          meta: { title: '用户详情', requiresAuth: true }
        },
        {
          path: 'register',
          name: 'Register',
          component: () => import('@/views/users/Register.vue'),
          meta: { title: '单用户注册', requiresAuth: true }
        },
        {
          path: 'edit/:id',
          name: 'EditUser',
          component: () => import('@/views/users/EditUser.vue'),
          meta: { title: '编辑用户', requiresAuth: true }
        },
        {
          path: 'import',
          name: 'ImportUsers',
          component: () => import('@/views/users/Import.vue'),
          meta: { title: '批量导入用户', requiresAuth: true }
        }
      ]
    },
    {
      path: '/courses',
      name: 'Courses',
      component: () => import('@/views/courses/Layout.vue'),
      meta: { title: '课程管理', requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: '',
          name: 'CourseList',
          component: () => import('@/views/courses/List.vue'),
          meta: { title: '课程列表', requiresAuth: true, requiresAdmin: true }
        },
        {
          path: 'add',
          name: 'AddCourse',
          component: () => import('@/views/courses/AddCourse.vue'),
          meta: { title: '新增课程', requiresAuth: true, requiresAdmin: true }

        },
        {
          path: 'edit/:id',
          name: 'EditCourse',
          component: () => import('@/views/courses/EditCourse.vue'),
          meta: { title: '编辑课程', requiresAuth: true, requiresAdmin: true }
        }
      ]
    },
    {
      path: '/problemsets',
      name: 'ProblemSets',
      component: () => import('@/views/problemsets/Layout.vue'),
      meta: { title: '题单管理', requiresAuth: true, requiresTeacher: true }
    },
    {
      path: '/403',
      component: () => import('@/views/error/403.vue'),
    },
    {
      path: '/404',
      component: () => import('@/views/error/404.vue'),
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiresTeacher = to.matched.some(record => record.meta.requiresTeacher);
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin);
  const userStore = useUserStore();
  const accessToken = userStore.accessToken;
  const refreshToken = userStore.refreshToken;

  const isTokenExpired = async (token) => {
    if (!token) return true;
      try {
        await axios.get('/api/auth/check_token', {
          headers: { Authorization: `Bearer ${token}` }
        });
        return false; // 没报错，token 有效
      } catch (err) {
        if (err.response?.status === 403 || err.response?.status === 401) {
          return true; // 报错，token 过期
        }
        // 其他错误也视为过期
        return true;
      }
    };

  if (requiresAuth) {
    if (await isTokenExpired(accessToken)) {
      if (refreshToken) {
        try {
          const res = await axios.post('/api/auth/refresh', {}, {
            headers: { Authorization: `Bearer ${refreshToken}` }
          });
          const newAccessToken = res.data.access_token
          userStore.accessToken = newAccessToken
          axios.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
        } catch (err) {
          console.error('Refresh token failed', err)
          userStore.logout()
          return next('/login')
        }
      } else {
        userStore.logout()
        return next('/login')
      }
    }

    if (requiresTeacher && userStore.usertype !== 'teacher' && userStore.usertype !== 'admin') {
      return next('/403') // 或 403 页面
    }
    if (requiresAdmin && userStore.usertype !== 'admin') {
      return next('/403') // 或 403 页面
    }
  }

  document.title = to.meta.title || 'DawOj v2'

  next()
})

export default router
