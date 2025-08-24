<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import { useRouter } from "vue-router"
import StatusBadge from "@/components/StatusBadge.vue"

const submissions = ref([])
const router = useRouter()

const fetchSubmissions = async () => {
  const res = await axios.get("/api/submissions/")
  submissions.value = res.data.items
}

const goDetail = (id) => {
  router.push(`/submissions/${id}`)
}

const goUser = (id) => {
  router.push(`/users/${id}`)
}

onMounted(fetchSubmissions)
</script>

<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-bold">提交记录</h2>
    </div>

    <div class="bg-white shadow rounded-lg overflow-hidden w-4/5 mx-auto">
      <table class="w-full text-left text-sm">
        <thead class="bg-gray-50 text-gray-700">
          <tr>
            <th class="p-3">提交编号</th>
            <th class="p-3">用户</th>
            <th class="p-3">题目编号</th>
            <th class="p-3">结果</th>
            <th class="p-3">语言</th>
            <th class="p-3">内存</th>
            <th class="p-3">时间</th>
            <th class="p-3">提交时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in submissions" :key="s.submission_id" class="hover:bg-gray-50 border-b border-gray-200">
            <td class="p-3">{{ s.submission_id }}</td>
            <td class="p-3 cursor-pointer text-blue-600 hover:underline" @click="goUser(s.user.id)">{{ s.user.username }}</td>
            <td class="p-3">{{ s.problem_id }}</td>
            <td class="p-3">
              <StatusBadge :status="s.status" :score="s.score" />
            </td>
            <td class="p-3 cursor-pointer text-blue-600 hover:underline" @click="goDetail(s.submission_id)">
              {{ s.language }}
            </td>
            <td class="p-3">{{ s.max_memory ? `${s.max_memory} KB` : "--" }}</td>
            <td class="p-3">{{ s.max_time ? `${s.max_time} ms` : "--" }}</td>
            <td class="p-3">{{ s.time_stamp }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
