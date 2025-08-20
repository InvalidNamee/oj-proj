<script setup>
import { ref } from 'vue';
import axios from 'axios';

const uid = ref('');
const password = ref('');
const login_type = ref('student');
const user = ref(null);
const access_token = ref('');
const refresh_token = ref('');
const error = ref('');

const login = async () => {
  error.value = '';
  try {
    const res = await axios.post('/auth/login', {
      uid: uid.value,
      password: password.value,
      login_type: login_type.value,
    });
    user.value = res.data.user;
    access_token.value = res.data.access_token;
    refresh_token.value = res.data.refresh_token;
    localStorage.setItem('access_token', access_token.value);
  } catch (e) {
    error.value = e.response?.data?.error || '登录失败';
  }
};

const refreshToken = async () => {
  error.value = '';
  try {
    const res = await axios.post('/auth/refresh', {}, {
      headers: { 'Authorization': `Bearer ${refresh_token.value}` }
    });
    access_token.value = res.data.access_token;
  } catch (e) {
    error.value = e.response?.data?.msg || '刷新失败';
  }
};

const logout = async () => {
  error.value = '';
  try {
    const res = await axios.post('/auth/logout', {}, {
      headers: { 'Authorization': `Bearer ${access_token.value}` }
    });
    alert(res.data.success);
    user.value = null;
    access_token.value = '';
    refresh_token.value = '';
  } catch (e) {
    error.value = e.response?.data?.error || '登出失败';
  }
};
</script>

<template>
  <div class="auth-container">
    <h2>用户认证测试</h2>

    <div v-if="!user">
      <input v-model="uid" placeholder="UID" />
      <input v-model="password" type="password" placeholder="密码" />
      <select v-model="login_type">
        <option value="student">学生</option>
        <option value="teacher">教师</option>
        <option value="admin">管理</option>
      </select>
      <button @click="login">登录</button>
    </div>

    <div v-else>
      <h3>用户信息</h3>
      <p>用户名: {{ user.username }}</p>
      <p>UID: {{ user.uid }}</p>
      <p>类型: {{ user.usertype }}</p>

      <button @click="refreshToken">刷新 Access Token</button>
      <button @click="logout">登出</button>

      <div class="tokens">
        <p><strong>Access Token:</strong> {{ access_token }}</p>
        <p><strong>Refresh Token:</strong> {{ refresh_token }}</p>
      </div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<style scoped>
.auth-container {
  max-width: 400px;
  margin: 20px auto;
  padding: 15px;
  border: 1px solid #ccc;
  border-radius: 6px;
}
.auth-container input,
.auth-container select {
  display: block;
  margin-bottom: 10px;
  width: 100%;
  padding: 6px;
  box-sizing: border-box;
}
.auth-container button {
  margin-right: 10px;
  padding: 6px 12px;
}
.tokens {
  margin-top: 10px;
  word-break: break-all;
}
.error {
  margin-top: 10px;
  color: red;
}
</style>
