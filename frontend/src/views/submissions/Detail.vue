<script setup>
import axios from "axios"
import { ref, onMounted, computed } from "vue"
import { useRoute } from "vue-router"
import CodeMirrorEditor from "@/components/CodeMirrorEditor.vue"
import StatusBadge from "@/components/StatusBadge.vue"

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
  <div class="max-w-4xl mx-auto mt-10 p-6 bg-white rounded shadow">
    <h2 class="text-xl font-bold mb-4">提交详情</h2>

    <!-- 上方详细信息 -->
    <div class="grid grid-cols-2 gap-x-6 gap-y-2 text-sm mb-4">
      <div><b>提交编号：</b>{{ submission?.submission_id }}</div>
      <div><b>题目编号：</b>{{ submission?.problem_id }}</div>
      <div><b>用户：</b>{{ submission?.user?.username }}</div>
      <div><b>语言：</b>{{ submission?.language || '无' }}</div>
      <div><b>结果：</b><StatusBadge :status="submission?.status" :score="submission?.score" /></div>
      <div><b>内存：</b>{{ submission?.max_memory ? `${submission.max_memory} KB` : "--" }}</div>
      <div><b>时间：</b>{{ submission?.max_time ? `${submission.max_time} ms` : "--" }}</div>
      <div class="col-span-2"><b>提交时间：</b>{{ submission?.time_stamp }}</div>
    </div>

    <!-- 代码部分 -->
    <div v-if="submission?.problem_type === 'coding'" class="mb-6">
      <b>代码：</b>
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
      <div class="mt-2 overflow-x-auto">
        <table class="table-auto text-sm border-collapse w-full text-center">
          <thead class="bg-gray-50 text-gray-700">
            <tr>
              <th class="px-3 py-2 border-b border-gray-200">测试点</th>
              <th class="px-3 py-2 border-b border-gray-200">结果</th>
              <th class="px-3 py-2 border-b border-gray-200">时间</th>
              <th class="px-3 py-2 border-b border-gray-200">内存</th>
              <th class="px-3 py-2 border-b border-gray-200">信息</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(t, i) in submission.extra"
              :key="i"
              class="hover:bg-gray-50 border-b border-gray-200"
            >
              <td class="px-3 py-2">{{ t.name }}</td>
              <td class="px-3 py-2">
                <StatusBadge :status="t.status" :score="null" />
              </td>
              <td class="px-3 py-2">{{ t.time ? `${t.time} ms` : "--" }}</td>
              <td class="px-3 py-2">{{ t.memory ? `${t.memory} KB` : "--" }}</td>
              <td class="px-3 py-2">{{ t.message || "--" }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>