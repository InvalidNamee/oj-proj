<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useUserStore } from '@/stores/user';
import router from '@/router';

const uid = ref('');
const password = ref('');
const loginType = ref('admin');
const userStore = useUserStore();
const errorMsg = ref('');

const handleLogin = async () => {
  errorMsg.value = '';
  try {
    const response = await axios.post('/api/auth/login', {
      uid: uid.value,
      password: password.value,
      login_type: loginType.value
    });
    const { access_token, refresh_token, user } = response.data;
    userStore.setUser(user, access_token, refresh_token);
    console.log('登录成功:', user);
    console.log('User Store after login:', userStore);
    router.push('/');
    window.location.reload();
  } catch (error) {
    errorMsg.value = error.response?.data?.error || '登录失败';
  }
};

onMounted(() => {
  // 检查是否已登录
  if (userStore.id) {
    router.push('/');
  }
});
</script>

<template>
  <div class="flex justify-center mt-16">
    <div class="bg-white shadow-md rounded-lg p-8 w-full max-w-sm">
      <h1 class="text-2xl font-bold text-gray-800 mb-6 text-center">登录</h1>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-gray-700 mb-1" for="uid">用户 ID</label>
          <input
            id="username"
            type="text"
            v-model="uid"
            class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="请输入用户ID"
            required
          />
        </div>

        <div>
          <label class="block text-gray-700 mb-1" for="password">密码</label>
          <input
            id="password"
            type="password"
            v-model="password"
            class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
            placeholder="请输入密码"
            required
          />
        </div>

        <div>
          <label class="block text-gray-700 mb-1" for="type">登录类型</label>
          <select
            id="type"
            v-model="loginType"
            class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option value="admin">管理员</option>
            <option value="teacher">教师</option>
            <option value="student">学生</option>
          </select>
        </div>

        <div v-if="errorMsg" class="text-red-500 text-sm">{{ errorMsg }}</div>

        <button
          type="submit"
          class="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600 transition-colors font-semibold"
        >
          登录
        </button>
      </form>
    </div>
  </div>
</template>
