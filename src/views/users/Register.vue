<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import CourseSelector from '@/components/CourseSelector.vue';

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
  <div class="max-w-md mx-auto mt-12 p-6 bg-white rounded-xl shadow">
    <h2 class="text-2xl font-bold mb-4">注册用户</h2>

    <div v-if="error" class="mb-2 text-red-500">{{ error }}</div>
    <div v-if="success" class="mb-2 text-green-500">{{ success }}</div>

    <div class="space-y-4">
      <input v-model="form.uid" placeholder="用户ID"
        class="w-full border border-gray-300 rounded px-2 py-1 text-gray-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none transition-all" />
      <input v-model="form.username" placeholder="用户名"
        class="w-full border border-gray-300 rounded px-2 py-1 text-gray-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none transition-all" />
      <input v-model="form.password" placeholder="密码"
        class="w-full border border-gray-300 rounded px-2 py-1 text-gray-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none transition-all" />

      <select v-model="form.usertype"
        class="w-full border border-gray-300 rounded px-2 py-1 text-gray-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none transition-all">
        <option value="student">学生</option>
        <option v-if="userStore.usertype === 'admin'" value="teacher">教师</option>
        <option v-if="userStore.usertype === 'admin'" value="admin">管理员</option>
      </select>

      <input v-model="form.school" placeholder="学校"
        class="w-full border border-gray-300 rounded px-2 py-1 text-gray-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none transition-all" />
      <input v-model="form.profession" placeholder="专业"
        class="w-full border border-gray-300 rounded px-2 py-1 text-gray-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none transition-all" />

      <!-- 多选课程 -->
      <CourseSelector v-model="form.course_list" :courses="courses" />

      <button @click="submit" class="w-full bg-blue-500 text-white px-3 py-2 rounded hover:bg-blue-600">
        注册
      </button>
    </div>
  </div>
</template>
