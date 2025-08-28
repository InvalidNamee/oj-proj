<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import CourseSelector from '@/components/CourseSelector.vue';
import '@/assets/users.css';
import '@/assets/pr3.css';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const userId = route.params.id;

// 表单数据
const form = ref({
  username: '',
  school: '',
  profession: '',
  password: '',
  course_list: []
});

const error = ref('');
const success = ref('');

// 可选择课程，只显示教师自己有权限的课程
const courses = computed(() => userStore.courses || []);

// 获取用户信息
const fetchUser = async () => {
  if (!userId) {
    error.value = '用户 ID 缺失';
    return;
  }
  try {
    const res = await axios.get(`/api/users/${userId}`);
    Object.assign(form.value, {
      username: res.data.username,
      school: res.data.school,
      profession: res.data.profession,
      course_list: res.data.courses.map(c => c.id)
    });
  } catch (err) {
    error.value = '获取用户信息失败';
  }
};

// 保存修改
const submit = async () => {
  error.value = '';
  success.value = '';
  if (!userId) {
    error.value = '用户 ID 缺失';
    return;
  }
  try {
    // 更新基本信息
    const res = await axios.put(`/api/users/${userId}`, form.value);
    if (res.data.success) {
      success.value = '修改成功';
    }
  } catch (err) {
    error.value = err.response?.data?.error || '修改失败';
  }

  // 更新课程
  try {
    await axios.patch(`/api/users/${userId}/courses`, {
      course_ids: form.value.course_list
    });
    success.value = '修改成功';
  } catch (err) {
    error.value = err.response?.data?.error || '更新课程失败';
  }
};

onMounted(fetchUser);
</script>

<template>
  <div class="user-edit-container">
    <div class="user-edit-header">
      <h2 class="user-edit-title">修改用户信息</h2>
    </div>

    <div v-if="error" class="user-edit-error">{{ error }}</div>
    <div v-if="success" class="user-edit-success">{{ success }}</div>

    <div class="space-y-4">
      <input v-model="form.username" placeholder="用户名" class="user-edit-input" />
      <input v-model="form.school" placeholder="学校" class="user-edit-input" />
      <input v-model="form.profession" placeholder="专业" class="user-edit-input" />
      <input v-model="form.password" placeholder="新密码，留空不重置" class="user-edit-input" />

      <!-- 课程选择 -->
      <div class="user-edit-course-selector">
        <CourseSelector v-model="form.course_list" :courses="courses" />
      </div>

      <button @click="submit" class="user-edit-button">
        保存修改
      </button>
    </div>
  </div>
</template>
