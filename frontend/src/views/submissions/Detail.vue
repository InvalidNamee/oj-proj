<script setup>
import axios from "axios"
import { ref, onMounted, computed } from "vue"
import { useRoute } from "vue-router"
import CodeMirrorEditor from "@/components/CodeMirrorEditor.vue"
import StatusBadge from "@/components/StatusBadge.vue"
import '@/assets/submissions.css'

const route = useRoute()
const submission = ref(null)

const userAnswer = computed({
  get: () => submission.value?.user_answer || "",
  set: (val) => {
    if (submission.value) submission.value.user_answer = val
  },
})

onMounted(async () => {
  const res = await axios.get(`/api/submissions/${route.params.id}`)
  submission.value = res.data
})
</script>

<template>
  <div class="submission-detail-container">
    <h2 class="submission-detail-title">提交详情</h2>

    <!-- 上方详细信息 -->
    <div class="submission-detail-grid">
      <div class="submission-detail-info-item"><b>提交编号：</b>{{ submission?.submission_id }}</div>
      <div class="submission-detail-info-item"><b>题目编号：</b>{{ submission?.problem_id }}</div>
      <div class="submission-detail-info-item"><b>用户：</b>{{ submission?.user?.username }}</div>
      <div class="submission-detail-info-item"><b>语言：</b>{{ submission?.language || '无' }}</div>
      <div class="submission-detail-info-item"><b>结果：</b><StatusBadge :status="submission?.status" :score="submission?.score" /></div>
      <div class="submission-detail-info-item"><b>内存：</b>{{ submission?.max_memory ? `${submission.max_memory} KB` : "--" }}</div>
      <div class="submission-detail-info-item"><b>时间：</b>{{ submission?.max_time ? `${submission.max_time} ms` : "--" }}</div>
      <div class="submission-detail-info-item col-span-2"><b>提交时间：</b>{{ submission?.time_stamp }}</div>
    </div>

    <!-- 代码部分 -->
    <div v-if="submission?.problem_type === 'coding'" class="submission-detail-code-container">
      <b class="submission-detail-code-title">代码：</b>
      <CodeMirrorEditor
        v-if="submission"
        v-model="userAnswer"
        lang="cpp"
        :editable="false"
        :height="'auto'"
      />
    </div>

    <!-- 测试点详情 -->
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
            <tr
              v-for="(t, i) in submission.extra"
              :key="i"
              class="submission-detail-tests-tbody-tr"
            >
              <td class="submission-detail-tests-td">{{ t.name }}</td>
              <td class="submission-detail-tests-td">
                <StatusBadge :status="t.status" :score="null" />
              </td>
              <td class="submission-detail-tests-td">{{ t.time ? `${t.time} ms` : "--" }}</td>
              <td class="submission-detail-tests-td">{{ t.memory ? `${t.memory} KB` : "--" }}</td>
              <td class="submission-detail-tests-td">{{ t.message || "--" }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>