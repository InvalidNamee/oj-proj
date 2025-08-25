<script setup>
import { ref, onMounted, watch } from "vue"
import axios from "axios"
import { useRouter } from "vue-router"
import StatusBadge from "@/components/StatusBadge.vue"
import { useUserStore } from "@/stores/user"

const submissions = ref([])
const router = useRouter()
const userStore = useUserStore()  // 当前用户信息

// 筛选条件
const filters = ref({
  user_id: "",
  problem_id: "",
  problem_set_id: "",
})

// 分页
const page = ref(1)
const perPage = ref(20)
const total = ref(0)
const pages = ref(1)

// 获取数据
const fetchSubmissions = async () => {
  try {
    const res = await axios.get("/api/submissions/", {
      params: {
        ...filters.value,
        page: page.value,
        per_page: perPage.value
      }
    })
    submissions.value = res.data.items
    total.value = res.data.total
    pages.value = res.data.pages
  } catch (err) {
    console.error(err)
  }
}

// 点击跳转到提交详情
const goDetail = (submission) => {
  if (userStore.usertype === 'student' && submission.user.id !== userStore.id) {
    alert("学生只能查看自己的提交详情")
    return
  }
  router.push(`/submissions/${submission.submission_id}`)
}

// 点击跳转到用户详情
const goUser = (submission) => {
  router.push(`/users/${submission.user.id}`)
}

const goProblem = (submission) => {
  router.push(`/problems/${submission.problem_id}?${submission.problem_set_id ? `psid=${submission.problem_set_id}` : ''}`)
}

const goProblemSet = (submission) => {
  if (submission.problem_set_id) {
    router.push(`/problemsets/${submission.problem_set_id}`)
  }
}

// 改变页码
const changePage = (p) => {
  if (p >= 1 && p <= pages.value) {
    page.value = p
    fetchSubmissions()
  }
}

// 搜索按钮
const doSearch = () => {
  page.value = 1
  fetchSubmissions()
}

onMounted(fetchSubmissions)
</script>

<template>
  <div class="p-6">
    <h2 class="text-xl font-bold mb-4">提交记录</h2>

    <!-- 筛选 -->
    <div class="flex flex-wrap gap-3 mb-4">
      <input v-model="filters.user_id" placeholder="用户ID" class="border border-gray-500 px-2 py-1 rounded w-24" />
      <input v-model="filters.problem_id" placeholder="题目ID" class="border border-gray-500 px-2 py-1 rounded w-24" />
      <input v-model="filters.problem_set_id" placeholder="题单ID"
        class="border border-gray-500 px-2 py-1 rounded w-24" />
      <button @click="doSearch" class="px-2 py-1 bg-blue-500 text-white rounded">搜索</button>
    </div>

    <!-- 表格 -->
    <div class="bg-white shadow rounded-lg overflow-hidden w-full">
      <table class="w-full text-left text-sm">
        <thead class="bg-gray-50 text-gray-700">
          <tr>
            <th class="p-3">提交编号</th>
            <th class="p-3">用户</th>
            <th class="p-3">题目编号</th>
            <th class="p-3">题单编号</th>
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
            <td class="p-3 cursor-pointer text-blue-600 hover:underline" @click="goUser(s)">{{ s.user.username }}</td>
            <td class="p-3 cursor-pointer text-blue-600 hover:underline" @click="goProblem(s)">{{ s.problem_id }}</td>
            <td v-if="s.problem_set_id" class="p-3 curser-pointer text-blue-600 hover:underline" @click="goProblemSet(s)">{{ s.problem_set_id }}</td>
            <td v-else class="p-3">--</td>
            <td class="p-3">
              <StatusBadge :status="s.status" :score="s.score" />
            </td>
            <td class="p-3 cursor-pointer text-blue-600 hover:underline" @click="goDetail(s)"
              :class="{ 'cursor-not-allowed text-gray-400': userStore.usertype === 'student' && s.user.id !== userStore.id }">
              {{ s.language ? s.language : '无' }}
            </td>
            <td class="p-3">{{ s.max_memory ? `${s.max_memory} KB` : "--" }}</td>
            <td class="p-3">{{ s.max_time ? `${s.max_time} ms` : "--" }}</td>
            <td class="p-3">{{ s.time_stamp }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="mt-4 flex justify-center items-center gap-4">
      <button @click="changePage(page - 1)" :disabled="page <= 1"
        class="px-3 py-1 border rounded disabled:opacity-50">上一页</button>
      <span>第 {{ page }} / {{ pages }} 页 (共 {{ total }} 条)</span>
      <button @click="changePage(page + 1)" :disabled="page >= pages"
        class="px-3 py-1 border rounded disabled:opacity-50">下一页</button>
    </div>
  </div>
</template>
