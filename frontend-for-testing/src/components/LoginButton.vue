<script setup>
import { ref } from 'vue';
import axios from 'axios';

const accessToken = ref(localStorage.getItem('access_token') || '');
const loginStatus = ref('');
const uid = ref('')
const password = ref('')
const login_type = ref('admin')
const username = ref('')

const login = async () => {
  try {
    const res = await axios.post('/auth/login', {
      uid: uid.value,        // 写死用户名
      password: password.value,   // 写死密码
      login_type: login_type.value    // 或者 student/admin
    });

    accessToken.value = res.data.access_token;
    localStorage.setItem('access_token', accessToken.value);
    username.value = res.data.user.username;
    loginStatus.value = '登录成功';

    // 给 axios 默认加请求头
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`;
  } catch (err) {
    console.error(err);
    loginStatus.value = '登录失败';
  }
};

// 页面加载时如果有 token 就自动设置默认请求头
if (accessToken.value) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken.value}`;
}
</script>

<template>
  <div>
    <input type="text" v-model="uid" />
    <input type="password" v-model="password" />
    <select v-model="login_type">
      <option value="admin">admin</option>
      <option value="teacher">teacher</option>
      <option value="student">student</option>
    </select>
    <button @click="login">测试登录</button>
    <p>{{ loginStatus }}</p>
    <p>{{ username }}</p>
  </div>
</template>
