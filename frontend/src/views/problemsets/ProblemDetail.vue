<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import useClipboard from 'vue-clipboard3'
import axios from 'axios'
import TestCases from '@/components/TestCases.vue'
import EditableTestCases from '@/components/EditableTestCases.vue'
import MonacoEditor from '@/components/MonacoEditor.vue'
import MarkdownArea from '@/components/MarkdownArea.vue'
import LegacyAnswerArea from '@/components/LegacyAnswerArea.vue'
import '@/assets/problemsets.css'
import '@/assets/pr2.css'

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
    const res = await axios.post('/api/submissions/self_check', {
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
      const res = await axios.get(`/api/submissions/self_check/${id}`)
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

// 重判功能
const rejudgeProblem = async () => {
  if (!confirm('确定要重判此题的所有提交记录吗？')) return
  
  try {
    const res = await axios.patch(`/api/submissions/problem/${problemId}`)
    if (res.data.ok) {
      alert(`重判成功，共处理了 ${res.data.rejudged} 条提交记录`)
    } else {
      alert('重判失败')
    }
  } catch (err) {
    console.error('重判失败', err)
    alert('重判失败')
  }
}
</script>

<template>
  <div class="problem-detail-container">
    <div class="problem-detail-header">
      <h1 class="problem-detail-title">{{ problem?.title || '加载中...' }}</h1>
      <div class="button-group" v-if="problem?.type === 'coding'">
        <button 
          @click="rejudgeProblem" 
          class="rejudge-btn"
        >
          重判
        </button>
        <router-link 
          :to="`/problems/${problemId}/edit/testcases`" 
          class="manage-test-cases-btn"
        >
          管理测试用例
        </router-link>
      </div>
    </div>

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

      <h3>说明</h3>
      <!-- <p v-html="problem.description.notes.replace(/\n/g, '<br/>')"></p> -->
      <MarkdownArea :model-value="problem.description.notes" />

      <!-- 样例 -->
      <div v-if="problem.description.samples?.length">
        <h3>样例</h3>
        <div v-for="sample in problem.description.samples" :key="sample.id"
          >
          <h4>样例 {{ sample.id }}</h4>
          <div class="flex gap-2 items-start">
            <div class="flex-1">
              <strong>输入：<button class="btn copy-input-button inline" @click="copyToClipboard(sample.input)">复制</button></strong>
              <pre class="sample-pre">{{ sample.input }}</pre>
            </div>
          </div>
          <div class="flex gap-2 items-start mt-1">
            <div class="flex-1">
              <strong>输出：<button class="btn copy-output-button inline" @click="copyToClipboard(sample.output)">复制</button></strong>
              <pre class="sample-pre">{{ sample.output }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
    <div v-else>
      {{ problem?.description }}
    </div>


    <div class="mt-8">
      <h3 class="problem-detail-submission-title">提交答案</h3>

      <template v-if="problem?.type === 'coding'">
        <MonacoEditor v-model="solution" />
        <div class="flex gap-2">
          <button class="problem-detail-submit-button" :disabled="submitting" @click="submitAnswer">
            {{ submitting ? '提交中...' : '提交' }}
          </button>
          <button class="self-test-button" :disabled="submitting" @click="runSelfCheck">
            {{ submitting ? '运行中...' : '自测' }}
          </button>
        </div>
        <div v-if="submissionStatus" class="problem-detail-status mt-4" :class="submissionStatus.status">
          {{ submissionStatus.status }}
          <template
            v-if="['WA', 'TLE', 'MLE', 'OLE', 'RE'].includes(submissionStatus.status) && submissionStatus.score !== null">
            得分: {{ submissionStatus.score }}
          </template>
          <!-- 显示具体测试点错误信息 -->
          <div v-if="submissionStatus.result && submissionStatus.result.length > 0" class="test-case-details">
            <div v-for="(test, index) in submissionStatus.result" :key="index" 
                 class="test-case-item" 
                 :class="test.status">
              <div class="test-case-header">
                <span class="test-case-name">测试点 {{ test.name }}: {{ test.status }}</span>
                <span v-if="test.memory" class="test-case-memory">内存: {{ test.memory }} KB</span>
                <span v-if="test.time" class="test-case-time">时间: {{ test.time }} ms</span>
              </div>
              <div v-if="test.diff" class="test-case-diff">
                <pre>{{ test.diff }}</pre>
              </div>
            </div>
          </div>
        </div>
        <div class="self-test-section">
          <h3 class="self-test-title">代码自测区</h3>
          <p class="self-test-description">自测代码能否通过样例</p>
          <EditableTestCases v-model="cases" />
        </div>
      </template>


      <template v-else>
        <LegacyAnswerArea v-if="problem" :problem-data="problem" v-model="sourceCode" />
        <button class="problem-detail-submit-button" :disabled="submitting" @click="submitAnswer">
          {{ submitting ? '提交中...' : '提交' }}
        </button>
        <div v-if="submissionStatus" class="problem-detail-status mt-4" :class="submissionStatus.status">
          {{ submissionStatus.status }}
          <template
            v-if="['WA', 'TLE', 'MLE', 'OLE', 'RE'].includes(submissionStatus.status) && submissionStatus.score !== null">
            得分: {{ submissionStatus.score }}
          </template>
          <!-- 显示具体测试点错误信息 -->
          <div v-if="submissionStatus.result && submissionStatus.result.length > 0" class="test-case-details">
            <div v-for="(test, index) in submissionStatus.result" :key="index" 
                 class="test-case-item" 
                 :class="test.status">
              <div class="test-case-header">
                <span class="test-case-name">测试点 {{ test.name }}: {{ test.status }}</span>
                <span v-if="test.memory" class="test-case-memory">内存: {{ test.memory }} KB</span>
                <span v-if="test.time" class="test-case-time">时间: {{ test.time }} ms</span>
              </div>
              <div v-if="test.diff" class="test-case-diff">
                <pre>{{ test.diff }}</pre>
              </div>
            </div>
          </div>
        </div>
      </template>

      
    </div>
  </div>
</template>

<style scoped>
.problem-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.button-group {
  display: flex;
  align-items: center;
}

.problem-detail-title {
  margin-bottom: 0;
}

.manage-test-cases-btn {
  background-color: #42b983;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 14px;
  transition: background-color 0.3s;
}

.manage-test-cases-btn:hover {
  background-color: #359c6d;
}

.rejudge-btn {
  background-color: #f59e0b; /* 橙色 */
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 14px;
  transition: background-color 0.3s;
  margin-right: 10px; /* 与右侧按钮保持间距 */
  border: none;
  cursor: pointer;
}

.rejudge-btn:hover {
  background-color: #d97706; /* 深橙色 */
}

/* 样例区pre标签样式 */
pre.sample-pre {
  border: 1px solid #d1d5db !important; /* 浅灰色边框 */
  padding: 0.5rem !important; /* 内边距 */
  border-radius: 0.25rem !important; /* 圆角 */
  background-color: #f9fafb !important; /* 背景色 */
  overflow-x: auto; /* 允许水平滚动 */
  min-width: 600px; /* 最小宽度 */
  width: 100%; /* 宽度占满容器 */
  max-width: 100%; /* 最大宽度 */
}

/* 样例区复制按钮样式 */
.copy-input-button, .copy-output-button {
  width: auto;
  min-width: 60px;
  padding: 4px 8px;
  font-size: 14px;
}

.problem-detail-submit-button {
  background-color: #f0f0f0;
  color: #333;
  border: 1px solid #ccc;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-top: 1rem;
}

.problem-detail-submit-button:hover:not(:disabled) {
  background-color: #e0e0e0;
}

.problem-detail-submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.self-test-button {
  background-color: #f0f0f0;
  color: #333;
  border: 1px solid #ccc;
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-top: 1rem;
}

.self-test-button:hover:not(:disabled) {
  background-color: #e0e0e0;
}

.self-test-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 测试点详细信息样式 */
.test-case-details {
  margin-top: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  max-height: 300px;
  overflow-y: auto;
}

.test-case-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.test-case-item:last-child {
  border-bottom: none;
}

.test-case-item.AC {
  background-color: #f0fff0;
  color: green;
}

.test-case-item.WA {
  background-color: #fff0f0;
}

.test-case-item.TLE, .test-case-item.MLE {
  background-color: #fff8f0;
}

.test-case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  font-weight: bold;
}

.test-case-name {
  flex: 1;
}

.test-case-memory, .test-case-time {
  font-size: 0.9em;
  color: #666;
}

.test-case-diff {
  margin-top: 5px;
  padding: 8px;
  background-color: #f8f8f8;
  border: 1px solid #eee;
  border-radius: 3px;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
}

.test-case-diff pre {
  margin: 0;
  padding: 0;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
