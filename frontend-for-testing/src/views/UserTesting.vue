<script setup>
import { ref } from 'vue';
import axios from 'axios';

const query_id = ref('');
const queriedUser = ref(null);
const newUser = ref({ uid: '', username: '', password: '', usertype: 'student' });
const oldPassword = ref('');
const newPassword = ref('');
const deleteIds = ref('');
const importJson = ref('');
const message = ref('');
const error = ref('');

const getUser = async () => {
  error.value = message.value = '';
  queriedUser.value = null;
  try {
    const res = await axios.get(`/users/${query_id.value}`);
    queriedUser.value = res.data;
  } catch (e) {
    error.value = e.response?.data?.error || '查询失败';
  }
};

const createUser = async () => {
  error.value = message.value = '';
  try {
    const res = await axios.post('/users/', newUser.value, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    });
    message.value = '创建成功';
  } catch (e) {
    error.value = e.response?.data?.error || '创建失败';
  }
};

const changePassword = async () => {
  error.value = message.value = '';
  try {
    await axios.patch('/users/', { password: oldPassword.value, new_password: newPassword.value }, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    });
    message.value = '修改成功';
  } catch (e) {
    error.value = e.response?.data?.error || '修改失败';
  }
};

const deleteUsers = async () => {
  error.value = message.value = '';
  const ids = deleteIds.value.split(',').map(i => i.trim()).filter(Boolean);
  try {
    const res = await axios.delete('/users/', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      data: { user_ids: ids }
    });
    message.value = `删除完成，成功: ${res.data.success}, 失败: ${res.data.fail}`;
  } catch (e) {
    error.value = e.response?.data?.error || '删除失败';
  }
};

const importUsers = async () => {
  error.value = message.value = '';
  let list;
  try {
    list = JSON.parse(importJson.value);
  } catch (e) {
    error.value = 'JSON 格式错误';
    return;
  }
  try {
    const res = await axios.post('/users/import', { user_list: list }, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    });
    message.value = `导入完成，成功: ${res.data.success_count}, 失败: ${res.data.fail_count}`;
  } catch (e) {
    error.value = e.response?.data?.error || '导入失败';
  }
};
</script>
<template>
  <div class="user-container">
    <h2>用户管理测试</h2>

    <div class="section">
      <h3>查询用户</h3>
      <input v-model="query_id" type="number" placeholder="用户 ID" />
      <button @click="getUser">查询</button>
      <pre v-if="queriedUser">{{ JSON.stringify(queriedUser, null, 2) }}</pre>
    </div>

    <div class="section">
      <h3>创建用户</h3>
      <input v-model="newUser.uid" placeholder="UID" />
      <input v-model="newUser.username" placeholder="用户名" />
      <input v-model="newUser.password" type="password" placeholder="密码" />
      <select v-model="newUser.usertype">
        <option value="student">学生</option>
        <option value="teacher">教师</option>
        <option value="admin">管理员</option>
      </select>
      <button @click="createUser">创建</button>
    </div>

    <div class="section">
      <h3>修改密码</h3>
      <input v-model="oldPassword" type="password" placeholder="旧密码" />
      <input v-model="newPassword" type="password" placeholder="新密码" />
      <button @click="changePassword">修改</button>
    </div>

    <div class="section">
      <h3>删除用户</h3>
      <input v-model="deleteIds" placeholder="用户 ID, 逗号分隔" />
      <button @click="deleteUsers">删除</button>
    </div>

    <div class="section">
      <h3>批量导入用户</h3>
      <textarea v-model="importJson" rows="5" placeholder='[{"uid":"1","username":"u1","password":"123","usertype":"student"}]'></textarea>
      <button @click="importUsers">导入</button>
    </div>

    <div v-if="message" class="message">{{ message }}</div>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<style scoped>
.user-container { max-width: 600px; margin: 20px auto; }
.section { margin-bottom: 20px; }
input, select, textarea { display: block; width: 100%; margin-bottom: 6px; padding: 6px; }
button { margin-top: 4px; padding: 6px 12px; }
.message { color: green; }
.error { color: red; }
</style>
