<script setup>
import { computed, ref } from 'vue'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
import '@/assets/users.css'

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
  <div class="user-import-container">
    <h2 class="user-import-title">批量导入用户</h2>

    <div class="user-import-instructions">
      <p>Excel文件第一行必须是：<br><strong class="user-import-field-names">username gender profession 班级 uid password school usertype</strong></p>
      <p>然后就可以在下方相应填写信息。</p>
      <p><strong>注意：</strong></p>
      <ul>
        <li>教师只能注册学生（usertype必须是student，注意大小写）</li>
        <li>管理员可以注册管理员（usertype为admin）、教师（usertype是teacher）、学生（usertype是student）</li>
      </ul>
    </div>

    <div class="user-import-info">
      当前课程：<span>{{ courseName }}</span>
    </div>

    <div>
      <label class="user-import-label">选择 Excel 文件 (.xlsx)</label>
      <input type="file" @change="handleFileChange" accept=".xlsx" class="user-import-input" />
    </div>

    <button
      @click="importUsers"
      :disabled="importing"
      class="user-import-button"
    >
      {{ importing ? '导入中...' : '开始导入' }}
    </button>

    <div v-if="errorMsg" class="user-import-error">{{ errorMsg }}</div>

    <div v-if="results.length" class="user-import-results">
      <h3 class="user-import-results-title">导入结果：</h3>
      <div class="user-import-results-list">
        <div v-for="(r, index) in results" :key="index" class="user-import-result-item">
          <span :class="r.status === 'success' ? 'user-import-result-success' : 'user-import-result-error'">
            {{ r.status.toUpperCase() }}
          </span>
          - {{ r.user.username }} ({{ r.user.uid }}) 
          <span v-if="r.error" class="user-import-result-error">: {{ r.error }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
