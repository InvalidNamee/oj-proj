<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import axios from 'axios';
import '@/assets/users.css';

const route = useRoute();
const router = useRouter();
const userId = ref(route.params.id);
const userData = ref(null);
const userStore = useUserStore();
const courses = computed(() => userStore.courses || []);

// 修改密码相关
const currentPassword = ref('');
const newPassword = ref('');
const confirmPassword = ref('');
const changeError = ref('');
const changeSuccess = ref('');

onMounted(async () => {
  try {
    const res = await axios.get(`/api/users/${userId.value}`);
    userData.value = res.data;
  } catch (err) {
    if (err.response?.status === 403) {
      router.push('/403');
    } else if (err.response?.status === 404) {
      router.push('/404');
    } else {
      console.error('Failed to fetch user:', err);
    }
  }
});

const identity = computed(() => {
  switch (userData.value?.usertype) {
    case 'admin':
      return '管理员';
    case 'teacher':
      return '教师';
    case 'student':
      return '学生';
    default:
      return '';
  }
});

const canChangePassword = computed(() => userStore.id == userData.value?.id);

const changePassword = async () => {
  changeError.value = '';
  changeSuccess.value = '';
  if (newPassword.value !== confirmPassword.value) {
    changeError.value = '两次输入的新密码不一致';
    return;
  }
  try {
    await axios.patch('/api/users', {
      password: currentPassword.value,
      new_password: newPassword.value
    });
    changeSuccess.value = '密码修改成功，请重新登录';
    userStore.clearUser();
    router.push('/login');
  } catch (err) {
    changeError.value = err.response?.data?.error || '修改失败';
  }
};

const goToCourse = (courseId) => {
  router.push(`/courses/${courseId}`);
};
</script>

<template>
  <div class="user-detail-container">
    <h2 class="user-detail-title">用户信息</h2>

    <div class="user-detail-info">
      <div class="user-detail-info-header">
      </div>
      <div class="user-detail-info-content">
        <div class="user-detail-info-row">
          <span class="user-detail-info-label">ID:</span>
          <span class="user-detail-info-value">{{ userData?.id }}</span>
        </div>
        <div class="user-detail-info-row">
          <span class="user-detail-info-label">UID:</span>
          <span class="user-detail-info-value">{{ userData?.uid }}</span>
        </div>
        <div class="user-detail-info-row">
          <span class="user-detail-info-label">用户名:</span>
          <span class="user-detail-info-value">{{ userData?.username }}</span>
        </div>
        <div class="user-detail-info-row">
          <span class="user-detail-info-label">身份:</span>
          <span class="user-detail-info-value">{{ identity }}</span>
        </div>
        <div class="user-detail-info-row">
          <span class="user-detail-info-label">注册时间:</span>
          <span class="user-detail-info-value">{{ userData?.timestamp }}</span>
        </div>
        <div v-if="userData?.school" class="user-detail-info-row">
          <span class="user-detail-info-label">学校:</span>
          <span class="user-detail-info-value">{{ userData?.school }}</span>
        </div>
        <div v-if="userData?.profession" class="user-detail-info-row">
          <span class="user-detail-info-label">专业:</span>
          <span class="user-detail-info-value">{{ userData?.profession }}</span>
        </div>
      </div>
    </div>

    <!-- 新增课程展示区 -->
    <div v-if="courses.length" class="user-detail-course-section">
      <h3 class="user-detail-course-title">{{ canChangePassword ? "我的课程" : "ta 的课程" }}</h3>
      <ul class="user-detail-course-list">
        <li v-for="course in courses" :key="course.id">
          <button
            class="user-detail-course-button"
            @click="goToCourse(course.id)"
          >
            {{ course.name }}
          </button>
        </li>
      </ul>
    </div>

    <!-- 修改密码 -->
    <div v-if="canChangePassword" class="user-detail-password-section">
      <h3 class="user-detail-password-title">修改密码</h3>

      <div class="user-detail-password-form">
        <input
          v-model="currentPassword"
          type="password"
          placeholder="当前密码"
          class="user-detail-input"
        />
        <input
          v-model="newPassword"
          type="password"
          placeholder="新密码"
          class="user-detail-input"
        />
        <input
          v-model="confirmPassword"
          type="password"
          placeholder="确认新密码"
          class="user-detail-input"
        />
        <button
          @click="changePassword"
          class="user-detail-button"
        >
          修改密码
        </button>

        <p v-if="changeError" class="user-detail-error">{{ changeError }}</p>
        <p v-if="changeSuccess" class="user-detail-success">{{ changeSuccess }}</p>
      </div>
    </div>
  </div>
</template>


