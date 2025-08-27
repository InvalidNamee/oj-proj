<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import useClipboard from 'vue-clipboard3'
import axios from 'axios'
import TestCases from '@/components/TestCases.vue'
import MonacoEditor from '@/components/MonacoEditor.vue'
import MarkdownArea from '@/components/MarkdownArea.vue'
import LegacyAnswerArea from '@/components/LegacyAnswerArea.vue'
import '@/assets/problemsets.css'

const route = useRoute()
const problemId = Number(route.params.id)
const psid = Number(route.query.psid)  // 可选题单 id
const problem = ref(null)
const userStore = useUserStore()
const solution = ref({ language: 'python', code: '' }) // 代码题答案
const sourceCode = ref('') // 传统题答案
const submissionId = ref(null)
const submissionStatus = ref(null)
const submitting = ref(false)
const cases = ref([])
const { toClipboard } = useClipboard()

let pollTimer = null

// 加载题目
onMounted(async () => {
  try {
    const res = await axios.get(`/api/problems/${problemId}?psid=${psid || ''}`)
    problem.value = res.data

    cases.value = problem.value.description.samples
    solution.value.language = problem.value.language || 'cpp'
    solution.value.code = problem.value.user_answer || ''

    // 传统题答案
    sourceCode.value = problem.value.user_answer || ''
  } catch (err) {
    console.error('加载题目失败', err)
  }
  if (pollTimer) clearInterval(pollTimer)
})

// ---- 自测 ----
const runSelfCheck = async () => {
  if (!solution.value.language || !solution.value.code) return
  submitting.value = true
  submissionStatus.value = null

  try {
    const res = await axios.post('/api/self_check', {
      language: solution.value.language,
      source_code: solution.value.code,
      test_cases: cases.value
    })
    const subId = res.data.submission_id
    pollSelfCheck(subId)
  } catch (err) {
    console.error(err)
    submitting.value = false
  }
}

const pollSelfCheck = (id) => {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    try {
      const res = await axios.get(`/api/self_check/${id}`)
      if (res.data.status && !['Pending', 'Judging'].includes(res.data.status)) {
        submissionStatus.value = res.data
        submitting.value = false
        clearInterval(pollTimer)
      }
    } catch (err) {
      console.error(err)
      submitting.value = false
      clearInterval(pollTimer)
    }
  }, 2000)
}

// ---- 正式提交 ----
const submitAnswer = async () => {
  if (submitting.value) return
  submitting.value = true
  submissionStatus.value = null

  try {
    if (problem.value.type === 'coding') {
      const res = await axios.post(`/api/submissions/${problemId}`, {
        language: solution.value.language,
        source_code: solution.value.code,
        problem_set_id: psid || undefined
      })
      submissionId.value = res.data.submission_id
      pollSubmission(submissionId.value)
    } else {
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

const pollSubmission = (id) => {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    try {
      const res = await axios.get(`/api/submissions/${id}/status`)
      if (res.data.status && !['Pending', 'Judging'].includes(res.data.status)) {
        submissionStatus.value = res.data
        submitting.value = false
        clearInterval(pollTimer)
      }
    } catch (err) {
      console.error(err)
      submitting.value = false
      clearInterval(pollTimer)
    }
  }, 2000)
}


const copyToClipboard = async (text) => {
  try {
    await toClipboard(text)
    alert('已复制到剪贴板')
  } catch (err) {
    console.error('复制失败', err)
    alert('复制失败')
  }
}
</script>

<template>
  <div class="problem-detail-container">
    <h1 class="problem-detail-title">{{ problem?.title || '加载中...' }}</h1>

    <div v-if="problem?.limitations" class="problem-detail-limitations">
      <p><span class="font-semibold">时间限制：</span>{{ problem.limitations.maxTime }} 秒</p>
      <p><span class="font-semibold">内存限制：</span>{{ problem.limitations.maxMemory }} MB</p>
    </div>

    <div v-if="problem?.type === 'coding'">
    <div v-if="problem?.description">
      <h3>题目描述</h3>
      <MarkdownArea :model-value="problem.description.description" />

      <h3>输入格式</h3>
      <MarkdownArea :model-value="problem.description.input_format" />

      <h3>输出格式</h3>
      <MarkdownArea :model-value="problem.description.output_format" />

      <!-- 样例 -->
      <div v-if="problem.description.samples?.length">
        <h3>样例</h3>
        <div v-for="sample in problem.description.samples" :key="sample.id"
          class="sample-block border p-2 mb-2 rounded">
          <h4>样例 {{ sample.id }}</h4>
          <div class="flex gap-2 items-start">
            <div class="flex-1">
              <strong>输入：</strong>
              <pre>{{ sample.input }}</pre>
            </div>
            <button class="btn" @click="copyToClipboard(sample.input)">复制输入</button>
          </div>
          <div class="flex gap-2 items-start mt-1">
            <div class="flex-1">
              <strong>输出：</strong>
              <pre>{{ sample.output }}</pre>
            </div>
            <button class="btn" @click="copyToClipboard(sample.output)">复制输出</button>
          </div>
        </div>
      </div>

      <h3>说明</h3>
      <!-- <p v-html="problem.description.notes.replace(/\n/g, '<br/>')"></p> -->
      <MarkdownArea :model-value="problem.description.notes" />
    </div>
    </div>
    <div v-else>
      {{ problem?.description }}
    </div>


    <div class="mt-8">
      <h3 class="problem-detail-submission-title">提交答案</h3>

      <template v-if="problem?.type === 'coding'">
        <MonacoEditor v-model="solution" />
        <TestCases v-model="cases" />
        <div class="flex gap-2 mt-2">
          <button class="btn" :disabled="submitting" @click="runSelfCheck">
            {{ submitting ? '运行中...' : '自测' }}
          </button>
          <button class="btn" :disabled="submitting" @click="submitAnswer">
            {{ submitting ? '提交中...' : '提交' }}
          </button>
        </div>
      </template>


      <template v-else>
        <LegacyAnswerArea v-if="problem" :problem-data="problem" v-model="sourceCode" />
        <button class="btn mt-2" :disabled="submitting" @click="submitAnswer">
          {{ submitting ? '提交中...' : '提交' }}
        </button>
      </template>

      <div v-if="submissionStatus" class="problem-detail-status mt-4" :class="submissionStatus.status">
        {{ submissionStatus.status }}
        <template
          v-if="['WA', 'TLE', 'MLE', 'OLE', 'RE'].includes(submissionStatus.status) && submissionStatus.score !== null">
          得分: {{ submissionStatus.score }}
        </template>
      </div>
    </div>
  </div>
</template>
