<script setup>
import { ref } from 'vue'
import axios from 'axios'
import TestCases from '@/components/TestCases.vue'
import CodeMirrorEditor from '@/components/CodeMirrorEditor.vue'

const test_cases = ref([
  {
    "id": 1,
    "input": "2 3\n",
    "output": "5\n"
  }
])
const source_code = ref('')  // 自测代码
const language = ref('cpp')
const loading = ref(false)
const result = ref(null)

let pollTimer = null

const runSelfCheck = async () => {
  if (loading.value) return
  loading.value = true
  result.value = null
  try {
    // 先提交
    const res = await axios.post('/api/submissions/self_check', {
      language: language.value,
      source_code: source_code.value,
      test_cases: test_cases.value
    })
    const { submission_id } = res.data

    // 开始轮询结果
    pollTimer = setInterval(async () => {
      const resp = await axios.get(`/api/submissions/self_check/${submission_id}`)
      result.value = resp.data
      if (resp.data.status !== "Pending") {
        clearInterval(pollTimer)
        loading.value = false
      }
    }, 1500)
  } catch (err) {
    console.error(err)
    result.value = { error: '自测失败' }
    loading.value = false
  }
}
</script>

<template>
  <div class="p-6 max-w-4xl mx-auto space-y-4">
    <h1 class="text-2xl font-bold mb-4">自测界面</h1>

    <TestCases v-model="test_cases" />

    <div>
      <label class="font-semibold mb-1 block">代码</label>
      <CodeMirrorEditor v-model="source_code" :language="language" />
    </div>

    <button
      @click="runSelfCheck"
      :disabled="loading"
      class="mt-3 px-4 py-2 rounded text-white bg-green-500 hover:bg-green-600 disabled:opacity-50"
    >
      {{ loading ? '自测中...' : '运行自测' }}
    </button>


    <pre class="bg-gray-100 p-2 rounded text-sm overflow-x-auto">
      {{ JSON.stringify(result, null, 2) }}
    </pre>

    <div v-if="result" class="mt-4 space-y-3">
      <div v-if="result.error" class="text-red-600">{{ result.error }}</div>

      <div v-else>
        <div v-for="c in result.cases" :key="c.name" class="p-2 border rounded bg-gray-50 space-y-1">
          <div class="flex justify-between items-center">
            <div>
              <strong>{{ c.name }}</strong> - 
              <span :class="{
                'text-green-700': c.status==='AC',
                'text-red-700': ['WA','RE','TLE','MLE','OLE'].includes(c.status),
                'text-orange-700': c.status==='CE'
              }">{{ c.status }}</span>
            </div>
          </div>


          <!-- WA diff 显示 -->
          <!-- <div v-if="c.status==='WA'" class="mt-1">
            <CodeMirrorEditor
              v-model="c.diff || ''"
              language="text"
              :read-only="true"
              :line-numbers="true"
              style="height: 200px;"
            />
          </div> -->
        </div>
      </div>
    </div>
  </div>
</template>

<!-- <script setup>
</script>
<template>
  <div class="max-w-4xl mx-auto mt-8 p-6 rounded-xl bg-white shadow">
    <h2 class="text-2xl font-bold mb-4">首页</h2>
    <p>欢迎使用在线评测系统！</p>
  </div>
</template> -->
