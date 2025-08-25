<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user.js";
import axios from "axios";

const userStore = useUserStore();
const router = useRouter();
const problemsets = ref([]);
const selected = ref([]);
const page = ref(1);
const perPage = ref(10);
const total = ref(0);
const pages = ref(1);
const showSelect = ref(false);
const keyword = ref(""); // 题单标题筛选

const fetchProblemSets = async () => {
  const res = await axios.get("/api/problemsets/", {
    params: {
      page: page.value,
      per_page: perPage.value,
      course_id: userStore.currentCourseId,
      keyword: keyword.value || undefined,
    },
  });
  problemsets.value = res.data.problemsets;
  total.value = res.data.total;
  pages.value = res.data.pages;
};

onMounted(fetchProblemSets);
watch(() => userStore.currentCourseId, fetchProblemSets);

const goDetail = (id) => router.push(`/problemsets/${id}`);
const goEdit = (id) => router.push(`/problemsets/${id}/edit`);

const deleteOne = async (id) => {
  if (!confirm("确认删除该题单吗？")) return;
  try {
    await axios.delete("/api/problemsets/", { data: { ids: [id] } });
    fetchProblemSets();
  } catch (err) {
    console.error(err);
    alert(err.response?.data?.error || "删除失败");
  }
};

const deleteBatch = async () => {
  if (selected.value.length === 0) {
    alert("请先选择题单");
    return;
  }
  if (!confirm(`确认删除选中的 ${selected.value.length} 个题单吗？`)) return;
  try {
    await axios.delete("/api/problemsets/", { data: { ids: selected.value } });
    selected.value = [];
    fetchProblemSets();
  } catch (err) {
    console.error(err);
    alert(err.response?.data?.error || "批量删除失败");
  }
};

const toggleAll = (e) => {
  selected.value = e.target.checked ? problemsets.value.map(p => p.id) : [];
};

const handleSelect = (id) => {
  if (!showSelect.value) return;
  if (selected.value.includes(id)) {
    selected.value = selected.value.filter(sid => sid !== id);
  } else {
    selected.value.push(id);
  }
};

const changePage = (p) => {
  if (p >= 1 && p <= pages.value) {
    page.value = p;
    fetchProblemSets();
  }
};
</script>

<template>
  <div class="max-w-4xl mx-auto mt-8 p-6 rounded-xl bg-white shadow">
    <h2 class="text-2xl font-bold mb-4">题单列表</h2>

    <!-- 顶部操作栏 + 搜索框 -->
    <div class="flex justify-between items-center mb-4">
      <!-- 左侧搜索框 -->
      <div class="flex items-center space-x-2">
        <input v-model="keyword" @keyup.enter="page = 1; fetchProblemSets()" placeholder="按题单标题筛选"
          class="border border-gray-500 rounded px-3 py-1" />
        <button @click="page = 1; fetchProblemSets()"
          class="px-4 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 cursor-pointer">
          筛选
        </button>
      </div>

      <!-- 右侧操作按钮 -->
      <div class="flex items-center space-x-2">
        <button @click="router.push('/problemsets/add')"
          class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 cursor-pointer">
          新建题单
        </button>
        <button @click="showSelect = !showSelect; selected = []"
          class="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 cursor-pointer">
          {{ showSelect ? "取消选择" : "选择" }}
        </button>
        <button v-if="showSelect && selected.length > 0" @click="deleteBatch"
          class="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 cursor-pointer">
          删除选中
        </button>
      </div>
    </div>


    <!-- 题单列表 -->
    <div class="space-y-2">
      <div v-for="ps in problemsets" :key="ps.id"
        class="p-4 border border-gray-300 rounded flex justify-between items-center hover:shadow-md cursor-pointer transition-shadow duration-200"
        :class="showSelect && selected.includes(ps.id) ? 'bg-blue-50 border-blue-400' : ''"
        @click="handleSelect(ps.id)">
        <div class="flex-1">
          <h3 @click.stop="goDetail(ps.id)" class="font-semibold text-lg">{{ ps.title }}</h3>
          <p class="text-sm text-gray-500">{{ ps.description }}</p>
          <p class="text-xs text-gray-400">
            课程: {{ ps.course?.title || '无' }} | 题目数: {{ ps.num_legacy_problems }} + {{ ps.num_coding_problems }}
          </p>
        </div>
        <div class="space-x-2 flex items-center">
          <input v-if="showSelect" type="checkbox" v-model="selected" :value="ps.id" @click.stop />
          <button @click.stop="goEdit(ps.id)" class="text-blue-500 hover:underline">编辑</button>
          <button @click.stop="deleteOne(ps.id)" class="text-red-500 hover:underline">删除</button>
        </div>
      </div>
    </div>


    <!-- 分页器 -->
    <div class="flex justify-center items-center mt-6 space-x-2">
      <button @click="changePage(page - 1)" :disabled="page === 1" class="px-3 py-1 border rounded disabled:opacity-50">
        上一页
      </button>
      <span>第 {{ page }} / {{ pages }} 页 (共 {{ total }} 条)</span>
      <button @click="changePage(page + 1)" :disabled="page === pages"
        class="px-3 py-1 border rounded disabled:opacity-50">
        下一页
      </button>
    </div>
  </div>
</template>