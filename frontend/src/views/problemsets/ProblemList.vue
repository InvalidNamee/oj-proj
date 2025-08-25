<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const router = useRouter();
const problems = ref([]);
const selected = ref([]); // 选中的 pid
const selectMode = ref(false); // 是否进入选择模式

// 搜索 & 分页
const keyword = ref("");
const page = ref(1);
const perPage = ref(10);
const total = ref(0);
const pages = ref(1);

const fetchProblems = async () => {
  try {
    const res = await axios.get("/api/problems/", {
      params: {
        course_id: userStore.currentCourseId,
        page: page.value,
        per_page: perPage.value,
        keyword: keyword.value || undefined,
      }
    });
    problems.value = res.data.problems;
    total.value = res.data.total;
    pages.value = res.data.pages;
  } catch (err) {
    console.error(err);
  }
};

const goDetail = (id) => {
  if (!selectMode.value) router.push(`/problems/${id}`);
};
const goEdit = (id) => router.push(`/problems/${id}/edit`);
const goEditTestCases = (id) => router.push(`/problems/${id}/edit/testcases`);

// 单个删除
const deleteOne = async (id) => {
  if (!confirm("确认删除该题目吗？")) return;
  try {
    await axios.delete("/api/problems/", {
      data: { pids: [id] },
    });
    fetchProblems();
  } catch (err) {
    console.error(err);
    alert(err.response?.data?.error || "删除失败");
  }
};

// 批量删除
const deleteBatch = async () => {
  if (selected.value.length === 0) {
    alert("请先选择要删除的题目");
    return;
  }
  if (!confirm(`确认删除选中的 ${selected.value.length} 个题目吗？`)) return;
  try {
    await axios.delete("/api/problems/", {
      data: { pids: selected.value },
    });
    selected.value = [];
    fetchProblems();
  } catch (err) {
    console.error(err);
    alert(err.response?.data?.error || "批量删除失败");
  }
};

// 点击行选择
const toggleSelect = (id) => {
  if (!selectMode.value) return;
  const idx = selected.value.indexOf(id);
  if (idx >= 0) selected.value.splice(idx, 1);
  else selected.value.push(id);
};

const changePage = (p) => {
  if (p >= 1 && p <= pages.value) {
    page.value = p;
    fetchProblems();
  }
};

onMounted(fetchProblems);
</script>

<template>
  <div class="p-6">
    <h2 class="text-xl font-bold mb-4">题目列表</h2>
    <!-- 顶部工具栏 -->
    <div class="flex justify-between items-center mb-4">
      <!-- 左侧搜索框 -->
      <div class="flex items-center space-x-2">
        <input v-model="keyword" @keyup.enter="page = 1; fetchProblems()" placeholder="搜索题目标题"
          class="border border-gray-500 rounded px-3 py-1" />
        <button @click="page = 1; fetchProblems()" class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 cursor-pointer">
          搜索
        </button>
      </div>

      <!-- 右侧操作按钮 -->
      <div class="flex items-center space-x-2">
        <button @click="$router.push('/problems/add')"
          class="px-4 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 cursor-pointer">
          新建题目
        </button>
        <button v-if="!selectMode" @click="selectMode = true"
          class="px-4 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 cursor-pointer">
          选择
        </button>
        <div v-else class="flex items-center space-x-2">
          <button @click="deleteBatch" class="px-4 py-1 bg-red-500 text-white rounded hover:bg-red-600 cursor-pointer">
            批量删除
          </button>
          <button @click="selectMode = false; selected = []"
            class="px-4 py-1 bg-gray-400 text-white rounded hover:bg-gray-500 cursor-pointer">
            取消
          </button>
        </div>
      </div>
    </div>


    <!-- 表格 -->
    <div class="bg-white shadow rounded-lg overflow-hidden">
      <table class="w-full text-left text-sm">
        <thead class="bg-gray-50 text-gray-700">
          <tr>
            <th class="p-3" v-if="selectMode"></th>
            <th class="p-3">ID</th>
            <th class="p-3">标题</th>
            <th class="p-3">所属课程</th>
            <th class="p-3">测试用例数</th>
            <th class="p-3">时间</th>
            <th class="p-3">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in problems" :key="p.id" @click="toggleSelect(p.id)"
            :class="['hover:bg-gray-50 transition', selectMode && selected.includes(p.id) ? 'bg-blue-100' : '']">
            <td class="p-3" v-if="selectMode">
              <input type="checkbox" :value="p.id" v-model="selected" @click.stop />
            </td>
            <td class="p-3">{{ p.id }}</td>
            <td class="p-3 cursor-pointer text-blue-600 hover:underline" @click.stop="goDetail(p.id)">{{ p.title }}</td>
            <td class="p-3">{{ p.course.name }}</td>
            <td v-if="p.type === 'coding'" class="p-3 cursor-pointer text-blue-600 hover:underline"
              @click.stop="goEditTestCases(p.id)">{{ p.num_test_cases }}</td>
            <td v-else class="p-3">-</td>
            <td class="p-3">{{ p.timestamp }}</td>
            <td class="p-3 space-x-3">
              <button class="text-blue-500 hover:underline" @click.stop="goEdit(p.id)">编辑</button>
              <button class="text-red-500 hover:underline" @click.stop="deleteOne(p.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页器 -->
    <div class="flex justify-center items-center mt-4 space-x-2">
      <button @click="changePage(page - 1)" :disabled="page === 1"
        class="px-3 py-1 border rounded disabled:opacity-50">上一页</button>
      <span>第 {{ page }} / {{ pages }} 页 (共 {{ total }} 条)</span>
      <button @click="changePage(page + 1)" :disabled="page === pages"
        class="px-3 py-1 border rounded disabled:opacity-50">下一页</button>
    </div>
  </div>
</template>
