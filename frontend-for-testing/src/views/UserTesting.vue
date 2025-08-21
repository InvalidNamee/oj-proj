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

// ---------- 查询用户 ----------
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

// ---------- 创建用户 ----------
const createUser = async () => {
  error.value = message.value = '';
  try {
    const res = await axios.post('/users', newUser.value, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    });
    message.value = '创建成功';
  } catch (e) {
    error.value = e.response?.data?.error || '创建失败';
  }
};

// ---------- 修改密码 ----------
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

// ---------- 删除用户 ----------
const deleteUsers = async () => {
  error.value = message.value = '';
  const ids = deleteIds.value.split(',').map(i => i.trim()).filter(Boolean);
  try {
    const res = await axios.delete('/users', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      data: { user_ids: ids }
    });
    message.value = `删除完成，成功: ${res.data.success}, 失败: ${res.data.fail}`;
  } catch (e) {
    error.value = e.response?.data?.error || '删除失败';
  }
};

// ---------- 批量导入用户 ----------
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

// ---------- 修改用户 ----------
const updateUserId = ref('');
const updateUserData = ref({ username: '', school: '', profession: '', password: '' });
const updateUser = async () => {
  error.value = message.value = '';
  if (!updateUserId.value) {
    error.value = '请填写用户ID';
    return;
  }
  // 只发送有值的字段
  const payload = {};
  Object.entries(updateUserData.value).forEach(([k, v]) => {
    if (v) payload[k] = v;
  });
  try {
    const res = await axios.put(`/users/${updateUserId.value}`, payload, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    });
    message.value = '修改成功';
    queriedUser.value = res.data.user;
  } catch (e) {
    error.value = e.response?.data?.error || '修改失败';
  }
};

// ---------- 用户列表（分页+筛选） ----------
const userList = ref([]);
const userListPage = ref(1);
const userListPerPage = ref(10);
const userListTotal = ref(0);
const userListFilters = ref({ username: '', usertype: '', school: '', profession: '', course_id: '' });

const listUsers = async () => {
  error.value = message.value = '';
  const params = {
    page: userListPage.value,
    per_page: userListPerPage.value,
    ...Object.fromEntries(Object.entries(userListFilters.value).filter(([_, v]) => v))
  };
  try {
    const res = await axios.get('/users', { params, headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } });
    userList.value = res.data.users;
    userListTotal.value = res.data.total;
    message.value = `获取用户列表成功，共 ${res.data.total} 条`;
  } catch (e) {
    error.value = e.response?.data?.error || '获取失败';
  }
};

// ---------- 修改用户课程 ----------
const modifyCoursesUserId = ref('');
const modifyCoursesIds = ref('');
const modifyCoursesResult = ref(null);
const modifyUserCourses = async () => {
  error.value = message.value = '';
  if (!modifyCoursesUserId.value) {
    error.value = '请填写用户ID';
    return;
  }
  // 逗号分隔转数组并去重
  const ids = modifyCoursesIds.value.split(',').map(i => parseInt(i.trim())).filter(Boolean);
  try {
    const res = await axios.patch(`/users/${modifyCoursesUserId.value}/courses`, { course_ids: ids }, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    });
    message.value = '课程修改成功';
    modifyCoursesResult.value = res.data;
  } catch (e) {
    error.value = e.response?.data?.error || '课程修改失败';
    modifyCoursesResult.value = null;
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

    <div class="section">
      <h3>修改用户信息（管理员/教师）</h3>
      <input v-model="updateUserId" placeholder="用户ID" />
      <input v-model="updateUserData.username" placeholder="新用户名" />
      <input v-model="updateUserData.school" placeholder="新学校" />
      <input v-model="updateUserData.profession" placeholder="新专业" />
      <input v-model="updateUserData.password" type="password" placeholder="新密码" />
      <button @click="updateUser">修改</button>
      <pre v-if="queriedUser">{{ JSON.stringify(queriedUser, null, 2) }}</pre>
    </div>

    <div class="section">
      <h3>用户列表（分页+筛选）</h3>
      <input v-model="userListFilters.username" placeholder="用户名模糊搜索" />
      <select v-model="userListFilters.usertype">
        <option value="">全部类型</option>
        <option value="student">学生</option>
        <option value="teacher">教师</option>
        <option value="admin">管理员</option>
      </select>
      <input v-model="userListFilters.school" placeholder="学校" />
      <input v-model="userListFilters.profession" placeholder="专业" />
      <input v-model="userListFilters.course_id" placeholder="课程ID" />
      <input v-model="userListPage" type="number" min="1" placeholder="页码" />
      <input v-model="userListPerPage" type="number" min="1" placeholder="每页数量" />
      <button @click="listUsers">查询</button>
      <div>总数: {{ userListTotal }}</div>
      <ul>
        <li v-for="u in userList" :key="u.id">
          {{ u.id }} - {{ u.username }} - {{ u.usertype }} - {{ u.school }} - {{ u.profession }}
        </li>
      </ul>
    </div>

    <div class="section">
      <h3>修改用户课程（管理员/教师）</h3>
      <input v-model="modifyCoursesUserId" placeholder="用户ID" />
      <input v-model="modifyCoursesIds" placeholder="课程ID, 逗号分隔" />
      <button @click="modifyUserCourses">修改课程</button>
      <pre v-if="modifyCoursesResult">{{ JSON.stringify(modifyCoursesResult, null, 2) }}</pre>
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
