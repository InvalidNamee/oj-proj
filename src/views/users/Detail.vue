<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import axios from 'axios';

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
  <div class="max-w-xl mx-auto mt-8 p-6 bg-white shadow rounded">
    <h2 class="text-2xl font-bold mb-4 text-gray-800">用户信息</h2>

    <div class="space-y-2 text-gray-700">
      <p><span class="font-semibold">ID:</span> {{ userData?.id }}</p>
      <p><span class="font-semibold">UID:</span> {{ userData?.uid }}</p>
      <p><span class="font-semibold">用户名:</span> {{ userData?.username }}</p>
      <p><span class="font-semibold">身份:</span> {{ identity }}</p>
      <p><span class="font-semibold">注册时间:</span> {{ userData?.timestamp }}</p>
      <p v-if="userData?.school"><span class="font-semibold">学校:</span> {{ userData?.school }}</p>
      <p v-if="userData?.profession"><span class="font-semibold">专业:</span> {{ userData?.profession }}</p>
    </div>

    <!-- 新增课程展示区 -->
    <div v-if="courses.length" class="mt-6">
      <h3 class="text-lg font-semibold mb-2 text-gray-800">我的课程</h3>
      <ul class="space-y-1">
        <li v-for="course in courses" :key="course.id">
          <button
            class="text-blue-600 hover:underline"
            @click="goToCourse(course.id)"
          >
            {{ course.name }}
          </button>
        </li>
      </ul>
    </div>

    <!-- 修改密码 -->
    <div v-if="canChangePassword" class="mt-6 border-t pt-4">
      <h3 class="text-xl font-semibold mb-3 text-gray-800">修改密码</h3>

      <div class="space-y-3">
        <input
          v-model="currentPassword"
          type="password"
          placeholder="当前密码"
          class="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <input
          v-model="newPassword"
          type="password"
          placeholder="新密码"
          class="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <input
          v-model="confirmPassword"
          type="password"
          placeholder="确认新密码"
          class="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <button
          @click="changePassword"
          class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          修改密码
        </button>

        <p v-if="changeError" class="text-red-500">{{ changeError }}</p>
        <p v-if="changeSuccess" class="text-green-600">{{ changeSuccess }}</p>
      </div>
    </div>
  </div>
</template>


