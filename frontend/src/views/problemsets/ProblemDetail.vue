<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
// import MarkdownArea from '@/components/MarkdownArea.vue'
import CodeMirrorEditor from "@/components/CodeMirrorEditor.vue"
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
const submitting = ref(false)   // 是否正在提交

let pollTimer = null

onMounted(async () => {
  try {
    const res = await axios.get(`/api/problems/${problemId}?psid=${psid || ''}`)
    problem.value = res.data
    language.value = problem.value.language || 'cpp'
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
  if (["AC", "WA", "CE", "RE", "TLE", "MLE", "IE"].includes(res.data.status)) {
    clearInterval(pollTimer)
    submitting.value = false
  }
}

const submitAnswer = async () => {
  if (submitting.value) return  // 防止重复提交
  submitting.value = true

  try {
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
      submitting.value = false
    }
  } catch (err) {
    console.error('提交失败', err)
    submitting.value = false
  }
}
</script>

<template>
  <div class="p-6 bg-white rounded-lg shadow-md">
    <h1 class="text-2xl font-bold mb-4">{{ problem?.title || '加载中...' }}</h1>

    <div v-if="problem?.limitations" class="mb-6 text-gray-700 border border-gray-300 rounded-md p-3">
      <p><span class="font-semibold">时间限制：</span>{{ problem.limitations.maxTime }} 秒</p>
      <p><span class="font-semibold">内存限制：</span>{{ problem.limitations.maxMemory }} MB</p>
    </div>

    <p>{{problem?.description}}</p>

    <div class="mt-8">
      <h3 class="text-lg font-bold mb-2">提交答案</h3>

      <template v-if="problem?.type === 'coding'">
        <select v-model="language" class="border border-gray-500 p-2 rounded mb-3">
          <option value="cpp">C++</option>
          <option value="python">Python</option>
        </select>
        <CodeMirrorEditor v-model="sourceCode" :language="language" />
      </template>

      <template v-else>
        <LegacyAnswerArea
          v-if="problem"
          :problem-data="problem"
          v-model="sourceCode"
        />
      </template>

      <button
        @click="submitAnswer"
        :disabled="submitting"
        class="mt-4 px-4 py-2 rounded text-white"
        :class="submitting ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'"
      >
        {{ submitting ? '提交中...' : '提交' }}
      </button>

      <!-- 显示结果 -->
      <div v-if="submissionStatus" class="mt-4 p-3 rounded font-medium"
           :class="{
             'bg-green-100 text-green-700': submissionStatus.status === 'AC',
             'bg-red-100 text-red-700': ['WA','TLE','MLE','OLE','RE'].includes(submissionStatus.status),
             'bg-blue-100 text-blue-700': submissionStatus.status === 'Judging',
             'bg-gray-100 text-gray-700': submissionStatus.status === 'Pending',
             'bg-orange-100 text-orange-700': submissionStatus.status === 'CE'
           }"
      >
        {{ submissionStatus.status }}
        <template v-if="['WA','TLE','MLE','OLE','RE'].includes(submissionStatus.status) && submissionStatus.score !== null">
          得分: {{ submissionStatus.score }}
        </template>
      </div>
    </div>
  </div>
</template>
