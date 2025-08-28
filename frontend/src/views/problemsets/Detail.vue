<!-- filepath: src/views/problemsets/Detail.vue -->
<script setup>
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import axios from "axios"
import StatusBadge from "@/components/StatusBadge.vue"
import MarkdownArea from "@/components/MarkdownArea.vue"
import '@/assets/problemsets.css'

const route = useRoute()
const router = useRouter()
const id = route.params.id
const problemset = ref({})

async function fetchProblemset() {
  const res = await axios.get(`/api/problemsets/${id}`)
  problemset.value = res.data
}

function goToProblem(problemId) {
  router.push({ name: "ProblemDetail", params: { id: problemId }, query: { psid: id } })
}

function goToSubmission(submissionId) {
  router.push({ name: "SubmissionDetail", params: { id: submissionId } })
}

onMounted(fetchProblemset)
</script>

<template>
  <div class="problemset-detail-container">
    <!-- 题单标题 -->
    <h1 class="problemset-detail-title">{{ problemset.title }}</h1>
    <p class="problemset-detail-meta">
      所属课程：{{ problemset.course?.title }}
      <span>创建时间：{{ problemset.timestamp }}</span>
      <button class="problemset-detail-ranklist-button" @click="router.push(`/problemsets/${id}/ranklist`)">排行榜</button>
    </p>

    <!-- 描述 markdown-it 渲染 -->
    <MarkdownArea :model-value="problemset.description" />

    <!-- 题目表格 -->
    <div class="problemset-detail-table-container">
      <table class="problemset-detail-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>标题</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="problem in problemset.problems"
            :key="problem.id"
          >
            <td>{{ problem.id }}</td>
            <td class="problemset-detail-problem-title" @click="goToProblem(problem.id)">
              {{ problem.title }}
            </td>
            <td>
              <StatusBadge v-if="problem.submission_id" :status="problem.status" :score="problem.score" @click="goToSubmission(problem.submission_id)"/>
              <span v-else class="text-gray-500">未提交</span>
            </td>
            <td>
              <button class="problemset-detail-action-button" @click="goToProblem(problem.id)">进入</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.prose {
  line-height: 1.7;
}
</style>