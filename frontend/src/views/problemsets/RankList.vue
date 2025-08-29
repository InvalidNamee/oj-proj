<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import '@/assets/pr2.css'

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

const downloadRanklist = async () => {
  try {
    const response = await axios.get(`/api/problemsets/${psid}/ranklist/download`, {
      responseType: 'blob'
    });
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `ranklist_${psid}.xlsx`);
    document.body.appendChild(link);
    link.click();
    
    // 清理
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert(err.response?.data?.error || "下载失败");
  }
}
</script>

<template>
  <div class="ranklist-container">
    <h2 class="ranklist-title">题单排行榜</h2>
    <button
      v-if="userStore.usertype !== 'student'"
      @click="downloadRanklist"
      class="ranklist-download-button"
    >
      下载 Excel
    </button>

    <table v-if="!loading" class="ranklist-table">
      <thead class="ranklist-table-header">
        <tr>
          <th class="ranklist-table-header-cell">学号</th>
          <th class="ranklist-table-header-cell">姓名</th>
          <th class="ranklist-table-header-cell" v-for="p in problems" :key="p.id">{{ p.name }}</th>
          <th class="ranklist-table-header-cell">总分</th>
        </tr>
      </thead>
      <tbody>
        <tr class="ranklist-table-row" v-for="student in ranklist" :key="student.student_id">
          <td class="ranklist-table-cell">{{ student.student_uid }}</td>
          <td class="ranklist-table-cell">{{ student.student_name }}</td>
          <td class="ranklist-table-cell" v-for="score in student.scores" :key="score.problem_id">
            {{ score.score !== null ? score.score : '-' }}
          </td>
          <td class="ranklist-table-cell">{{ student.total_score }}</td>
        </tr>
      </tbody>
    </table>
    <p v-if="loading">加载中...</p>
  </div>
</template>

<style scoped>
.ranklist-table {
  width: 100%;
  text-align: left;
  font-size: 0.875rem; /* text-sm */
  border-collapse: separate;
  border-spacing: 0;
  background-color: #fff; /* bg-white */
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); /* 更明显的阴影 */
  border-radius: 0 0 0.75rem 0.75rem; /* 只在底部保留圆角 */
  overflow: hidden;
  margin-top: 0; /* 移除顶部外边距 */
  border: 1px solid #e5e7eb; /* 添加边框 */
  border-top: none; /* 移除顶部边框 */
}

.ranklist-table-header {
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%); /* 渐变背景 */
  color: #1f2937; /* text-gray-800 */
  border-bottom: 2px solid #9ca3af; /* 更粗的底部边框 */
}

.ranklist-table-header-cell {
  padding: 1.25rem 1rem; /* 增加内边距 */
  font-weight: 700; /* font-bold */
  text-transform: uppercase; /* uppercase */
  letter-spacing: 0.05em; /* tracking-wide */
  font-size: 1rem; /* 从text-xs增大到text-sm */
  color: #374151; /* text-gray-700 */
  text-align: center;
}

.ranklist-table-row {
  transition: all 0.3s; /* 更平滑的过渡 */
  border-bottom: 1px solid #e5e7eb; /* 更浅的底部边框 */
}

.ranklist-table-row:last-child {
  border-bottom: none;
}

.ranklist-table-row:hover {
  background-color: #f9fafb; /* hover:bg-gray-50 */
  transform: scale(1.005); /* 轻微放大效果 */
}

.ranklist-table-cell {
  padding: 1.25rem 1rem; /* 增加内边距 */
  vertical-align: middle;
  border-bottom: 1px solid #e5e7eb; /* 更浅的底部边框 */
  transition: background-color 0.2s;
  text-align: center;
}
</style>
