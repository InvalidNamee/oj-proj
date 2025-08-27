<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useUserStore } from '@/stores/user';
import router from '@/router';
import '@/assets/users.css';

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
  <div class="login-container">
    <div class="login-form-container">
      <h1 class="login-title">登录</h1>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="login-form-group">
          <label class="login-form-label" for="uid">用户 ID</label>
          <input
            id="username"
            type="text"
            v-model="uid"
            class="login-form-input"
            placeholder="请输入用户ID"
            required
          />
        </div>

        <div class="login-form-group">
          <label class="login-form-label" for="password">密码</label>
          <input
            id="password"
            type="password"
            v-model="password"
            class="login-form-input"
            placeholder="请输入密码"
            required
          />
        </div>

        <div class="login-form-group">
          <label class="login-form-label" for="type">登录类型</label>
          <select
            id="type"
            v-model="loginType"
            class="login-form-select"
          >
            <option value="admin">管理员</option>
            <option value="teacher">教师</option>
            <option value="student">学生</option>
          </select>
        </div>

        <div v-if="errorMsg" class="login-error-message">{{ errorMsg }}</div>

        <button
          type="submit"
          class="login-submit-button"
        >
          登录
        </button>
      </form>
    </div>
  </div>
</template>
