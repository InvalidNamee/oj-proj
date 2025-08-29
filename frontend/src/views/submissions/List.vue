<script setup>
import '@/assets/submissions.css';
import { ref, onMounted, watch } from "vue"
import axios from "axios"
import { useRouter, useRoute } from "vue-router"
import StatusBadge from "@/components/StatusBadge.vue"
import UserSelectModal from "@/components/UserSelectModal.vue"
import CourseSelectModal from "@/components/CourseSelectModal.vue"
import ProblemSetSelectModal from "@/components/ProblemSetSelectModal.vue"
import { useUserStore } from "@/stores/user"

const submissions = ref([])
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()  // 当前用户信息

// 筛选条件 —— 从 URL query 初始化
const filters = ref({
  user_id: route.query.user_id || "",
  problem_id: route.query.problem_id || "",
  problem_set_id: route.query.problem_set_id || "",
})

// 弹窗控制
const showCourseSelectModal = ref(false)
const showUserSelectModal = ref(false)
const showProblemSetSelectModal = ref(false)

// 分页 —— 从 URL query 初始化
const page = ref(Number(route.query.page) || 1)
const perPage = ref(Number(route.query.per_page) || 20)
const total = ref(0)
const pages = ref(1)

// 同步 query 到 URL
const syncQueryToRouter = () => {
  router.replace({
    query: {
      ...filters.value,
      page: page.value,
      per_page: perPage.value,
      // 不存在的值不要带上
      user_id: filters.value.user_id || undefined,
      problem_id: filters.value.problem_id || undefined,
      problem_set_id: filters.value.problem_set_id || undefined
    }
  })
}

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

// 搜索按钮
const doSearch = () => {
  page.value = 1
  syncQueryToRouter()
  fetchSubmissions()
}

// 改变页码
const changePage = (p) => {
  if (p >= 1 && p <= pages.value) {
    page.value = p
  }
}

// 点击跳转
const goDetail = (submission) => {
  if (userStore.usertype === 'student' && submission.user.id !== userStore.id) {
    alert("学生只能查看自己的提交详情")
    return
  }
  router.push(`/submissions/${submission.submission_id}`)
}
const goUser = (submission) => router.push(`/users/${submission.user.id}`)
const goProblem = (submission) => {
  router.push(`/problems/${submission.problem_id}?${submission.problem_set_id ? `psid=${submission.problem_set_id}` : ''}`)
}
const goProblemSet = (submission) => {
  if (submission.problem_set_id) router.push(`/problemsets/${submission.problem_set_id}`)
}

onMounted(fetchSubmissions)

// 监听分页、筛选变化，自动更新 URL 并拉数据
watch([page, perPage, () => filters.value.user_id, () => filters.value.problem_id, () => filters.value.problem_set_id], () => {
  syncQueryToRouter()
  fetchSubmissions()
})
</script>


<template>
  <div class="submissions-list-wrapper">
    <div class="submissions-container">
    <h2 class="submissions-title">提交记录</h2>

    <!-- 筛选 -->
    <div class="submissions-filter-container">
      <div class="submissions-user-filter">
        <input v-model="filters.user_id" placeholder="用户ID" class="submissions-filter-input" />
      <button @click="showUserSelectModal = true" class="submissions-select-user-button">选择用户</button>
    </div>
    <div class="submissions-course-filter">
      <input v-model="filters.problem_id" placeholder="题目ID" class="submissions-filter-input" />
      <button @click="showCourseSelectModal = true" class="submissions-select-course-button">选择课程</button>
    </div>
    <div class="submissions-problem-set-filter">
      <input v-model="filters.problem_set_id" placeholder="题单ID" class="submissions-filter-input" />
      <button @click="showProblemSetSelectModal = true" class="submissions-select-problem-set-button">选择题单</button>
    </div>
    <div class="submissions-action-buttons">
      <button @click="doSearch" class="submissions-search-button">搜索</button>
    </div>
    
    <!-- 课程选择弹窗 -->
    <CourseSelectModal 
      v-model="showCourseSelectModal" 
      :selected-course-id="filters.problem_id"
      @course-selected="(courseId) => { filters.problem_id = courseId; showCourseSelectModal = false }"
    />
    
    <!-- 题单选择弹窗 -->
    <ProblemSetSelectModal 
      v-model="showProblemSetSelectModal" 
      :selected-problem-set-id="filters.problem_set_id"
      @problem-set-selected="(problemSetId) => { filters.problem_set_id = problemSetId; showProblemSetSelectModal = false }"
    />
      
      <!-- 用户选择弹窗 -->
      <UserSelectModal 
        v-model="showUserSelectModal" 
        :selected-user-id="filters.user_id"
        @user-selected="(userId) => { filters.user_id = userId; showUserSelectModal = false }"
      />
    </div>

    <!-- 表格 -->
    <div class="submissions-table-container">
      <table class="submissions-table">
        <thead class="submissions-table-header">
          <tr>
            <th class="submissions-table-header-cell">提交编号</th>
            <th class="submissions-table-header-cell">用户</th>
            <th class="submissions-table-header-cell">题目编号</th>
            <th class="submissions-table-header-cell">题单编号</th>
            <th class="submissions-table-header-cell">结果</th>
            <th class="submissions-table-header-cell">语言</th>
            <th class="submissions-table-header-cell">内存</th>
            <th class="submissions-table-header-cell">时间</th>
            <th class="submissions-table-header-cell">提交时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in submissions" :key="s.submission_id" class="submissions-table-row">
            <td class="submissions-table-cell">{{ s.submission_id }}</td>
            <td class="submissions-table-cell submissions-link" @click="goUser(s)">{{ s.user.username }}</td>
            <td class="submissions-table-cell submissions-link" @click="goProblem(s)">{{ s.problem_id }}</td>
            <td v-if="s.problem_set_id" class="submissions-table-cell submissions-link" @click="goProblemSet(s)">{{ s.problem_set_id }}</td>
            <td v-else class="submissions-table-cell">--</td>
            <td class="submissions-table-cell">
              <StatusBadge :status="s.status" :score="s.score" />
            </td>
            <td class="submissions-table-cell submissions-link" @click="goDetail(s)"
              :class="{ 'submissions-disabled-link': userStore.usertype === 'student' && s.user.id !== userStore.id }">
              {{ s.language ? s.language : '无' }}
            </td>
            <td class="submissions-table-cell">{{ s.max_memory ? `${s.max_memory} KB` : "--" }}</td>
            <td class="submissions-table-cell">{{ s.max_time ? `${s.max_time} ms` : "--" }}</td>
            <td class="submissions-table-cell">{{ s.time_stamp }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="submissions-pagination">
      <button @click="changePage(page - 1)" :disabled="page <= 1" class="submissions-pagination-button">上一页</button>
      <span class="submissions-pagination-info">第 {{ page }} / {{ pages }} 页 (共 {{ total }} 条)</span>
      <button @click="changePage(page + 1)" :disabled="page >= pages" class="submissions-pagination-button">下一页</button>
    </div>
  </div>
</div>
</template>
