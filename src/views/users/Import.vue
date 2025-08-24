<script setup>
import { computed, ref } from 'vue'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const file = ref(null)
const importing = ref(false)
const results = ref([])
const errorMsg = ref('')

const userStore = useUserStore()
const courseName = computed(() => {
  const course = userStore.courses.find(c => c.id === userStore.currentCourseId);
  return course ? course.name : '';
});


const handleFileChange = (e) => {
  file.value = e.target.files[0]
}

const importUsers = async () => {
  if (!file.value) {
    errorMsg.value = '请选择一个 Excel 文件'
    return
  }

  importing.value = true
  errorMsg.value = ''
  results.value = []

  const formData = new FormData()
  formData.append('file', file.value)
  formData.append('course_id', userStore.currentCourseId)

  try {
    const res = await axios.post('/api/users/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    results.value = res.data.results || []
  } catch (err) {
    errorMsg.value = err.response?.data?.error || '导入失败'
  } finally {
    importing.value = false
  }
}
</script>

<template>
  <div class="max-w-lg mx-auto p-6 bg-white shadow rounded mt-6">
    <h2 class="text-xl font-bold mb-4">批量导入学生</h2>

    <div class="mb-4 text-sm text-gray-700">
      当前课程：<span class="font-medium">{{ courseName }}</span>
    </div>

    <div class="mb-3">
      <label class="block mb-1">选择 Excel 文件 (.xlsx)</label>
      <input type="file" @change="handleFileChange" accept=".xlsx" class="border px-2 py-1 w-full" />
    </div>

    <button
      @click="importUsers"
      :disabled="importing"
      class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
    >
      {{ importing ? '导入中...' : '开始导入' }}
    </button>

    <div v-if="errorMsg" class="text-red-500 mt-3">{{ errorMsg }}</div>

    <div v-if="results.length" class="mt-4">
      <h3 class="font-semibold mb-2">导入结果：</h3>
      <div class="max-h-64 overflow-y-auto border rounded p-2 bg-gray-50 text-sm">
        <div v-for="(r, index) in results" :key="index" class="mb-1">
          <span :class="r.status === 'success' ? 'text-green-600' : 'text-red-600'">
            {{ r.status.toUpperCase() }}
          </span>
          - {{ r.user.username }} ({{ r.user.uid }}) 
          <span v-if="r.error" class="text-red-500">: {{ r.error }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
