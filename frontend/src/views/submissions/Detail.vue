<script setup>
import axios from "axios"
import { ref, onMounted, computed } from "vue"
import { useRoute } from "vue-router"
import { useUserStore } from "@/stores/user"
import MonacoEditor from "@/components/MonacoEditor.vue"
import StatusBadge from "@/components/StatusBadge.vue"

const route = useRoute()
const submission = ref(null)
const userStore = useUserStore()
const polling = ref(false)
let pollTimer = null

const expandedRows = ref(new Set())
const toggleExpand = (i) => {
  if (expandedRows.value.has(i)) {
    expandedRows.value.delete(i)
  } else {
    expandedRows.value.add(i)
  }
}

const editorData = computed({
  get: () => ({
    code: submission.value?.user_answer || "",
    language: submission.value?.language || "plaintext"
  }),
  set: (val) => {
    if (submission.value) submission.value.user_answer = val.code
  }
})

const fetchSubmission = async () => {
  const res = await axios.get(`/api/submissions/${route.params.id}`)
  submission.value = res.data
}

const rejudge = async () => {
  if (!submission.value) return
  await axios.patch(`/api/submissions/${submission.value.submission_id}`)
  submission.value.status = "Pending"
  submission.value.score = 0
  polling.value = true
  startPolling()
}

const startPolling = () => {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    if (!polling.value) return
    await fetchSubmission()
    if (submission.value.status !== "Pending" && submission.value.status !== "Judging") {
      clearInterval(pollTimer)
      polling.value = false
    }
  }, 2000)
}

onMounted(fetchSubmission)
</script>

<template>
  <div class="submissions-list-wrapper">
    <div class="submission-detail-container">
    <div class="submission-detail-header">
      <h2 class="submission-detail-title">提交详情</h2>
      <button class="rejudge-btn" @click="rejudge">重判</button>
    </div>

      <div class="submission-detail-grid">
        <div class="submission-detail-info-item"><b>提交编号：</b>{{ submission?.submission_id }}</div>
        <div class="submission-detail-info-item"><b>题目编号：</b>{{ submission?.problem_id }}</div>
        <div class="submission-detail-info-item"><b>用户：</b>{{ submission?.user?.username }}</div>
        <div class="submission-detail-info-item"><b>语言：</b>{{ submission?.language || '无' }}</div>
        <div class="submission-detail-info-item"><b>结果：</b>
          <StatusBadge :status="submission?.status" :score="submission?.score" />
        </div>
        <div class="submission-detail-info-item"><b>内存：</b>{{ submission?.max_memory ? `${submission.max_memory} KB` : "--" }}</div>
        <div class="submission-detail-info-item"><b>时间：</b>{{ submission?.max_time ? `${submission.max_time} ms` : "--" }}</div>
        <div class="submission-detail-info-item col-span-2"><b>提交时间：</b>{{ submission?.time_stamp }}</div>
      </div>

      <div v-if="submission?.problem_type === 'coding'" class="submission-detail-code-container">
        <b class="submission-detail-code-title">代码：</b>
        <MonacoEditor v-if="submission" v-model="editorData" :readonly="true" height="auto" />
      </div>

      <div v-if="submission?.extra && submission.extra.length">
        <b>测试详情：</b>
        <div class="submission-detail-tests-container">
          <table class="submission-detail-tests-table">
            <thead class="submission-detail-tests-thead">
              <tr>
                <th class="submission-detail-tests-th">测试点</th>
                <th class="submission-detail-tests-th">结果</th>
                <th class="submission-detail-tests-th">时间</th>
                <th class="submission-detail-tests-th">内存</th>
                <th class="submission-detail-tests-th">信息</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="(t, i) in submission.extra" :key="i">
                <tr class="submission-detail-tests-tbody-tr">
                  <td class="submission-detail-tests-td">{{ t.name }}</td>
                  <td class="submission-detail-tests-td">
                    <StatusBadge :status="t.status" :score="null" />
                  </td>
                  <td class="submission-detail-tests-td">{{ t.time ? `${t.time} ms` : "--" }}</td>
                  <td class="submission-detail-tests-td">{{ t.memory ? `${t.memory} KB` : "--" }}</td>
                  <td class="submission-detail-tests-td">
                    <div>
                      <template v-if="t.status === 'WA' && t.diff">
                        <button class="diff-toggle-btn" @click="toggleExpand(i)">
                          {{ expandedRows.has(i) ? "收起diff" : "展开diff" }}
                        </button>
                      </template>
                      <template v-else>
                        {{ t.message || "--" }}
                      </template>
                    </div>
                  </td>
                </tr>
                <tr v-if="t.status === 'WA' && t.diff && expandedRows.has(i)">
                  <td colspan="5" class="diff-pre-cell">
                    <pre class="diff-pre">{{ t.diff }}</pre>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.diff-toggle-btn {
  margin-left: 8px;
  color: #2563eb;
  background: none;
  border: none;
  text-decoration: underline;
  cursor: pointer;
  font-size: 13px;
  padding: 0;
}
.diff-pre-cell {
  background: #f9fafb;
  padding: 0;
}
.diff-pre {
  margin: 0;
  padding: 12px;
  background: #f3f4f6;
  border-radius: 4px;
  font-size: 13px;
  max-height: 200px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>

<style scoped>
.submission-detail-header {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.submission-detail-title {
  flex-grow: 1;
  text-align: center;
}

.rejudge-btn {
  position: absolute;
  right: 0;
}

.rejudge-btn {
  background-color: #f59e0b; /* 橙色 */
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

.rejudge-btn:hover {
  background-color: #d97706; /* 深橙色 */
}
</style>