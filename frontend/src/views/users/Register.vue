<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import CourseSelector from '@/components/CourseSelector.vue';
import '@/assets/users.css';

const router = useRouter();
const userStore = useUserStore();
const courses = computed(() => userStore.courses || []);

const form = ref({
  uid: '',
  username: '',
  password: '',
  usertype: 'student',
  school: '',
  profession: '',
  course_list: []
});

const error = ref('');
const success = ref('');

const submit = async () => {
  error.value = '';
  success.value = '';
  try {
    const res = await axios.post('/api/users', form.value);
    if (res.data.status === 'success') {
      success.value = '注册成功';
      // 清空表单
      form.value = {
        uid: '',
        username: '',
        password: '',
        usertype: 'student',
        school: '',
        profession: '',
        course_list: []
      };
    }
  } catch (err) {
    error.value = err.response?.data?.error || '注册失败';
  }
};
</script>

<template>
  <div class="user-register-container">
    <h2 class="user-register-title">注册用户</h2>

    <div v-if="error" class="user-register-error">{{ error }}</div>
    <div v-if="success" class="user-register-success">{{ success }}</div>

    <div class="user-register-form">
      <input v-model="form.uid" placeholder="用户ID"
        class="user-register-input" />
      <input v-model="form.username" placeholder="用户名"
        class="user-register-input" />
      <input v-model="form.password" placeholder="密码"
        class="user-register-input" />

      <select v-model="form.usertype"
        class="user-register-select">
        <option value="student">学生</option>
        <option v-if="userStore.usertype === 'admin'" value="teacher">教师</option>
        <option v-if="userStore.usertype === 'admin'" value="admin">管理员</option>
      </select>

      <input v-model="form.school" placeholder="学校"
        class="user-register-input" />
      <input v-model="form.profession" placeholder="专业"
        class="user-register-input" />

      <!-- 多选课程 -->
      <CourseSelector v-model="form.course_list" :courses="courses" />

      <button @click="submit" class="user-register-button">
        注册
      </button>
    </div>
  </div>
</template>
