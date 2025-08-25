<!-- filepath: src/views/problemsets/Detail.vue -->
<script setup>
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import axios from "axios"
import MarkdownIt from "markdown-it"
import StatusBadge from "@/components/StatusBadge.vue"

const route = useRoute()
const router = useRouter()
const id = route.params.id
const problemset = ref({})

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

function renderMarkdown(text) {
  return md.render(text || "")
}

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
  <div class="p-6">
    <!-- 题单标题 -->
    <h1 class="text-3xl font-bold mb-2">{{ problemset.title }}</h1>
    <p class="text-gray-500 mb-4">
      所属课程：{{ problemset.course?.title }}
      <span class="ml-4">创建时间：{{ problemset.timestamp }}</span>
    </p>

    <!-- 描述 markdown-it 渲染 -->
    <div
      v-html="renderMarkdown(problemset.description)"
      class="prose max-w-none mb-6"
    />

    <!-- 题目表格 -->
    <div class="bg-white shadow rounded-lg overflow-hidden w-4/5 mx-auto">
      <table class="w-full text-left text-sm">
        <thead class="bg-gray-50 text-gray-700">
          <tr>
            <th class="p-3">ID</th>
            <th class="p-3">标题</th>
            <th class="p-3">状态</th>
            <th class="p-3">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="problem in problemset.problems"
            :key="problem.id"
            class="hover:bg-gray-50 border-b border-gray-200 transition"
          >
            <td class="p-3">{{ problem.id }}</td>
            <td class="p-3 cursor-pointer text-blue-600 hover:underline" @click="goToProblem(problem.id)">
              {{ problem.title }}
            </td>
            <td class="p-3">
              <StatusBadge v-if="problem.submission_id" :status="problem.status" :score="problem.score" @click="goToSubmission(problem.submission_id)"/>
              <span v-else class="text-gray-500">未提交</span>
            </td>
            <td class="p-3">
              <button class="text-blue-500 hover:underline" @click="goToProblem(problem.id)">进入</button>
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