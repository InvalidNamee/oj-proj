<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const psid = Number(route.params.id)
const userStore = useUserStore()

const problems = ref([])
const ranklist = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await axios.get(`/api/problemsets/${psid}/ranklist`)
    if (res.data.success) {
      problems.value = res.data.problems
      ranklist.value = res.data.ranklist
    }
  } catch (err) {
    console.error('加载排行榜失败', err)
  } finally {
    loading.value = false
  }
})

const downloadRanklist = () => {
  window.open(`/api/problemsets/${psid}/ranklist/download`, '_blank')
}
</script>

<template>
  <div class="ranklist-container">
    <h2>题单排行榜</h2>
    <button
      v-if="userStore.usertype !== 'student'"
      @click="downloadRanklist"
      class="btn mb-2"
    >
      下载 Excel
    </button>

    <table v-if="!loading" class="ranklist-table">
      <thead>
        <tr>
          <th>学号</th>
          <th>姓名</th>
          <th v-for="p in problems" :key="p.id">{{ p.name }}</th>
          <th>总分</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="student in ranklist" :key="student.student_id">
          <td>{{ student.student_uid }}</td>
          <td>{{ student.student_name }}</td>
          <td v-for="score in student.scores" :key="score.problem_id">
            {{ score.score !== null ? score.score : '-' }}
          </td>
          <td>{{ student.total_score }}</td>
        </tr>
      </tbody>
    </table>
    <p v-if="loading">加载中...</p>
  </div>
</template>

<style scoped>
.ranklist-table {
  width: 100%;
  border-collapse: collapse;
}
.ranklist-table th, .ranklist-table td {
  border: 1px solid #ccc;
  padding: 4px 8px;
  text-align: center;
}
.ranklist-table th {
  background-color: #f3f3f3;
}
</style>
