<script setup>
import { ref } from 'vue';
import axios from 'axios';

const accessToken = ref(localStorage.getItem('access_token') || '');
const loginStatus = ref('');

const login = async () => {
  try {
    const res = await axios.post('/auth/login', {
      uid: '2407040129',        // 写死用户名
      password: 'QWQQWQ',   // 写死密码
      login_type: 'admin'    // 或者 student/admin
    });

    accessToken.value = res.data.access_token;
    localStorage.setItem('access_token', accessToken.value);
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
    <button @click="login">测试登录</button>
    <p>{{ loginStatus }}</p>
  </div>
</template>
