<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
import MarkdownArea from '@/components/MarkdownArea.vue'
import CodeMirrorEditor from "@/components/CodeMirrorEditor.vue"
import StatusBadge from '@/components/StatusBadge.vue'
import LegacyAnswerArea from '@/components/LegacyAnswerArea.vue' // 传统题答案组件

const route = useRoute()
const problemId = Number(route.params.id)
const psid = Number(route.query.psid)  // 可选题单 id
const problem = ref(null)
const userStore = useUserStore()
const sourceCode = ref("")  // 对于非代码题，也存储答案

const language = ref("cpp")
const submissionId = ref(null)
const submissionStatus = ref(null)
let pollTimer = null

onMounted(async () => {
  try {
    const res = await axios.get(`/api/problems/${problemId}?psid=${psid || ''}`)
    problem.value = res.data
    sourceCode.value = problem.value.user_answer || ''
  } catch (err) {
    console.error('加载题目失败', err)
  }
  if (pollTimer) clearInterval(pollTimer)
})

const pollStatus = async () => {
  if (!submissionId.value) return
  const res = await axios.get(`/api/submissions/${submissionId.value}/status`)
  submissionStatus.value = res.data
  if (["Accepted", "Rejected", "CE", "RE", "TLE", "MLE"].includes(res.data.status)) {
    clearInterval(pollTimer)
  }
}

const submitAnswer = async () => {
  if (problem.value.type === 'coding') {
    // 提交代码题
    const res = await axios.post(`/api/submissions/${problemId}`, {
      language: language.value,
      source_code: sourceCode.value,
      problem_set_id: psid || undefined
    })
    submissionId.value = res.data.submission_id
    submissionStatus.value = res.data
    pollTimer = setInterval(pollStatus, 2000)
  } else {
    // 提交传统题
    const res = await axios.post(`/api/submissions/${problemId}`, {
      user_answer: sourceCode.value,
      problem_set_id: psid || undefined
    })
    submissionStatus.value = res.data
  }
}
</script>

<template>
  <div class="p-6 bg-white rounded-lg shadow-md">
    <h1 class="text-2xl font-bold mb-4">{{ problem?.title || '加载中...' }}</h1>

    <!-- 限制条件 -->
    <div v-if="problem?.limitations" class="mb-6 text-gray-700 border border-gray-300 rounded-md p-3">
      <p><span class="font-semibold">时间限制：</span>{{ problem.limitations.maxTime }} 秒</p>
      <p><span class="font-semibold">内存限制：</span>{{ problem.limitations.maxMemory }} MB</p>
    </div>

    <!-- 题目描述 -->
    <MarkdownArea :markdown="problem?.description || ''" />

    <div class="mt-8">
      <h3 class="text-lg font-bold mb-2">提交答案</h3>

      <!-- 根据类型渲染输入区 -->
      <template v-if="problem?.type === 'coding'">
        <select v-model="language" class="border border-gray-500 p-2 rounded mb-3">
          <option value="cpp">C++</option>
          <option value="python">Python</option>
        </select>
        <CodeMirrorEditor v-model="sourceCode" :language="language" />
      </template>

      <template v-else>
        <LegacyAnswerArea
        :problem-data="problem"
          v-model="sourceCode"
        />
      </template>

      <button @click="submitAnswer" class="mt-4 bg-blue-600 text-white px-4 py-2 rounded">
        提交
      </button>

      <StatusBadge v-if="submissionStatus" :status="submissionStatus.status" :score="submissionStatus.score" class="ml-4" />
    </div>
  </div>
</template>

<style scoped>
.prose {
  line-height: 1.7;
}
</style>
