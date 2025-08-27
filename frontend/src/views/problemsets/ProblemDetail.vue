<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
import MarkdownArea from '@/components/MarkdownArea.vue'
import CodeMirrorEditor from "@/components/CodeMirrorEditor.vue"
import LegacyAnswerArea from '@/components/LegacyAnswerArea.vue' // 传统题答案组件
import '@/assets/problemsets.css'

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
  <div class="problem-detail-container">
    <button 
      @click="$router.push(`/problems/${problemId}/edit/testcases`);" 
      class="edit-test-cases-button"
    >
      编辑测试用例
    </button>
    <h1 class="problem-detail-title">{{ problem?.title || '加载中...' }}</h1>

    <div v-if="problem?.limitations" class="problem-detail-limitations">
      <p><span class="font-semibold">时间限制：</span>{{ problem.limitations.maxTime }} 秒</p>
      <p><span class="font-semibold">内存限制：</span>{{ problem.limitations.maxMemory }} MB</p>
    </div>

    <MarkdownArea :markdown="problem?.description || ''" />

    <div class="mt-8">
      <h3 class="problem-detail-submission-title">提交答案</h3>

      <template v-if="problem?.type === 'coding'">
        <select v-model="language" class="problem-detail-language-select">
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
        class="problem-detail-submit-button"
      >
        {{ submitting ? '提交中...' : '提交' }}
      </button>

      <!-- 显示结果 -->
      <div v-if="submissionStatus" class="problem-detail-status"
           :class="submissionStatus.status"
      >
        {{ submissionStatus.status }}
        <template v-if="['WA','TLE','MLE','OLE','RE'].includes(submissionStatus.status) && submissionStatus.score !== null">
          得分: {{ submissionStatus.score }}
        </template>
      </div>
    </div>
  </div>
</template>
