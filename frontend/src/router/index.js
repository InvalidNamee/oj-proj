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
          meta: { title: '单用户注册', requiresAuth: true, requiresTeacher: true }
        },
        {
          path: 'edit/:id',
          name: 'EditUser',
          component: () => import('@/views/users/EditUser.vue'),
          meta: { title: '编辑用户', requiresAuth: true, requiresTeacher: true }
        },
        {
          path: 'import',
          name: 'ImportUsers',
          component: () => import('@/views/users/Import.vue'),
          meta: { title: '批量导入用户', requiresAuth: true, requiresTeacher: true }
        }
      ]
    },
    {
      path: '/courses',
      name: 'Courses',
      component: () => import('@/views/courses/Layout.vue'),
      meta: { title: '课程管理', requiresAuth: true },
      children: [
        {
          path: '',
          name: 'CourseList',
          component: () => import('@/views/courses/List.vue'),
          meta: { title: '课程列表', requiresAuth: true, requiresAdmin: true }
        },
        {
          path: ':id',
          name: 'CourseDetail',
          component: () => import('@/views/courses/Detail.vue'),
          meta: { title: '课程详情', requiresAuth: true }
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
      meta: { title: '题单管理', requiresAuth: true,  },
      children: [
        {
          path: '',
          name: 'ProblemSetList',
          component: () => import('@/views/problemsets/List.vue'),
          meta: { title: '题单列表', requiresAuth: true,  }
        },
        {
          path: 'add',
          name: 'AddProblemSet',
          component: () => import('@/views/problemsets/AddProblemSet.vue'),
          meta: { title: '新增题单', requiresAuth: true, requiresTeacher: true }
        },
        {
          path: ':id/edit',
          name: 'EditProblemSet',
          component: () => import('@/views/problemsets/EditProblemSet.vue'),
          meta: { title: '编辑题单', requiresAuth: true, requiresTeacher: true }
        },
        {
          path: ':id',
          name: 'ProblemSetDetail',
          component: () => import('@/views/problemsets/Detail.vue'),
          meta: { title: '题单详情', requiresAuth: true }
        },
        {
          path: ':id/ranklist',
          name: 'RankList',
          component: () => import('@/views/problemsets/RankList.vue'),
          meta: { title: '排行榜', requiresAuth: true}
        }
      ]
    },
    {
      path: '/groups',
      name: 'Groups',
      component: () => import('@/views/groups/Layout.vue'),
      meta: { title: '编程组管理', requiresAuth: true },
      children: [
        {
          path: '',
          name: 'GroupList',
          component: () => import('@/views/groups/List.vue'),
          meta: { title: '组列表', requiresAuth: true }
        },
        {
          path: 'add',
          name: 'AddGroup',
          component: () => import('@/views/groups/AddGroup.vue'),
          meta: { title: '新增组', requiresAuth: true, requiresTeacher: true }
        },
        {
          path: ':id/edit',
          name: 'EditGroup',
          component: () => import('@/views/groups/EditGroup.vue'),
          meta: { title: '编辑组', requiresAuth: true, requiresTeacher: true }
        },
        {
          path: ':id',
          name: 'GroupDetail',
          component: () => import('@/views/groups/Detail.vue'),
          meta: { title: '组详情', requiresAuth: true }
        }
      ]
    },
    {
      path: '/problems',
      name: 'Problems',
      component: () => import('@/views/problemsets/Layout.vue'),
      meta: { title: '题目管理', requiresAuth: true,  },
      children: [
        {
          path: '',
          name: 'ProblemList',
          component: () => import('@/views/problemsets/ProblemList.vue'),
          meta: { title: '题目列表', requiresAuth: true,  }
        },
        {
          path: 'add',
          name: 'AddProblem',
          component: () => import('@/views/problemsets/AddProblem.vue'),
          meta: { title: '新增题目', requiresAuth: true, requiresTeacher: true },
          children: [
            {
              path: ':type',
              name: 'AddProblemByType',
              component: () => import('@/views/problemsets/AddProblem.vue'),
              meta: { title: '新增题目', requiresAuth: true, requiresTeacher: true }
            }
          ]
        },
        {
          path: ':id/edit',
          name: 'EditProblem',
          component: () => import('@/views/problemsets/EditProblem.vue'),
          meta: { title: '编辑题目', requiresAuth: true, requiresTeacher: true }
        },
        {
          path: ':id',
          name: 'ProblemDetail',
          component: () => import('@/views/problemsets/ProblemDetail.vue'),
          meta: { title: '题目详情', requiresAuth: true }
        },
        {
          path: ':id/edit/testcases',
          name: 'EditTestCases',
          component: () => import('@/views/problemsets/EditTestCases.vue'),
          meta: { title: '编辑测试数据', requiresAuth: true, requiresTeacher: true }
        }
      ]
    },
    {
      path: '/submissions',
      name: 'Submissions',
      component: () => import('@/views/submissions/List.vue'),
      meta: { title: '提交记录', requiresAuth: true  },
    },
    {
      path: '/submissions/:id',
      name: 'SubmissionDetail',
      component: () => import('@/views/submissions/Detail.vue'),
      meta: { title: '提交详情', requiresAuth: true  }
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
  
  if (to.path === '/courses') {
    if (userStore.usertype !== 'admin') {
      if (userStore.currentCourseId) {
        return next(`/courses/${userStore.currentCourseId}`)
      }
    }
  }

  if (requiresAuth) {
    if (!userStore.id) {
      return next('/login')
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
