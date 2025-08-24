<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const problems = ref([]);
const router = useRouter();
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
    const res = await axios.get("/api/coding_problems/", {
      params: {
        course_id: userStore.currentCourseId,
        page: page.value,
        per_page: perPage.value,
        keyword: keyword.value || undefined,
      }
    });
    problems.value = res.data.coding_problems;
    total.value = res.data.total;
    pages.value = res.data.pages;
  } catch (err) {
    console.error(err);
  }
};

const goDetail = (id) => {
  router.push(`/problems/${id}`);
};
const goEdit = (id) => {
  router.push(`/problems/${id}/edit`);
};

// 单个删除
const deleteOne = async (id) => {
  if (!confirm("确认删除该题目吗？")) return;
  try {
    await axios.delete("/api/coding_problems/", {
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
    await axios.delete("/api/coding_problems/", {
      data: { pids: selected.value },
    });
    selected.value = [];
    fetchProblems();
  } catch (err) {
    console.error(err);
    alert(err.response?.data?.error || "批量删除失败");
  }
};

// 全选/全不选
const toggleAll = (e) => {
  if (e.target.checked) {
    selected.value = problems.value.map(p => p.id);
  } else {
    selected.value = [];
  }
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
    <!-- 顶部工具栏 -->
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-bold">题目列表</h2>
      <div class="flex space-x-2">
        <!-- 搜索 -->
        <input
          v-model="keyword"
          @keyup.enter="page = 1; fetchProblems()"
          placeholder="搜索题目标题"
          class="border rounded px-2 py-1"
        />
        <button
          @click="page = 1; fetchProblems()"
          class="px-3 py-1 bg-gray-200 rounded"
        >
          搜索
        </button>

        <!-- 新建 -->
        <button
          @click="$router.push('/problems/add')"
          class="px-4 py-2 bg-blue-500 text-white rounded shadow"
        >
          新建题目
        </button>

        <!-- 切换选择模式 -->
        <button
          v-if="!selectMode"
          @click="selectMode = true"
          class="px-4 py-2 bg-gray-500 text-white rounded shadow"
        >
          选择
        </button>
        <div v-else class="flex space-x-2">
          <button
            @click="deleteBatch"
            class="px-4 py-2 bg-red-500 text-white rounded shadow"
          >
            批量删除
          </button>
          <button
            @click="selectMode = false; selected = []"
            class="px-4 py-2 bg-gray-400 text-white rounded shadow"
          >
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
            <th class="p-3" v-if="selectMode">
              <input type="checkbox" @change="toggleAll" />
            </th>
            <th class="p-3">ID</th>
            <th class="p-3">标题</th>
            <th class="p-3">所属课程</th>
            <th class="p-3">测试用例数</th>
            <th class="p-3">时间</th>
            <th class="p-3">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="p in problems"
            :key="p.id"
            class="hover:bg-gray-50 transition"
          >
            <td class="p-3" v-if="selectMode">
              <input
                type="checkbox"
                :value="p.id"
                v-model="selected"
              />
            </td>
            <td class="p-3">{{ p.id }}</td>
            <td class="p-3 cursor-pointer text-blue-600 hover:underline" @click="goDetail(p.id)">
              {{ p.title }}
            </td>
            <td class="p-3">{{ p.course.name }}</td>
            <td class="p-3">{{ p.num_test_cases }}</td>
            <td class="p-3">{{ p.timestamp }}</td>
            <td class="p-3 space-x-3">
              <button class="text-blue-500 hover:underline" @click="goEdit(p.id)">编辑</button>
              <button class="text-red-500 hover:underline" @click="deleteOne(p.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页器 -->
    <div class="flex justify-center items-center mt-4 space-x-2">
      <button
        @click="changePage(page - 1)"
        :disabled="page === 1"
        class="px-3 py-1 border rounded disabled:opacity-50"
      >
        上一页
      </button>
      <span>第 {{ page }} / {{ pages }} 页 (共 {{ total }} 条)</span>
      <button
        @click="changePage(page + 1)"
        :disabled="page === pages"
        class="px-3 py-1 border rounded disabled:opacity-50"
      >
        下一页
      </button>
    </div>
  </div>
</template>
