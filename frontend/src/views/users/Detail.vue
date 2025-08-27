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
      <p><span>ID:</span> {{ userData?.id }}</p>
      <p><span>UID:</span> {{ userData?.uid }}</p>
      <p><span>用户名:</span> {{ userData?.username }}</p>
      <p><span>身份:</span> {{ identity }}</p>
      <p><span>注册时间:</span> {{ userData?.timestamp }}</p>
      <p v-if="userData?.school"><span>学校:</span> {{ userData?.school }}</p>
      <p v-if="userData?.profession"><span>专业:</span> {{ userData?.profession }}</p>
    </div>

    <!-- 新增课程展示区 -->
    <div v-if="courses.length" class="mt-6">
      <h3 class="user-detail-course-title">{{ canChangePassword ? "我的课程" : "ta 的课程" }}</h3>
      <ul class="space-y-1" style="list-style-type: none; padding-left: 0;">
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

      <div class="space-y-3">
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


