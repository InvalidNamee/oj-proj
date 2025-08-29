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
  pages.value = res.data.total_pages;
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

// 格式化时间显示
const formatTime = (time) => {
  if (!time) return '无';
  return new Date(time).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};
</script>

<template>
  <div class="problemset-list-container">
    <h2 class="problemset-list-title">题单列表</h2>

    <!-- 顶部操作栏 + 搜索框 -->
    <div class="problemset-list-toolbar">
      <!-- 左侧搜索框 -->
      <div class="problemset-list-search-container">
        <input v-model="keyword" @keyup.enter="page = 1; fetchProblemSets()" placeholder="按题单标题筛选"
          class="problemset-list-search-input" />
        <button @click="page = 1; fetchProblemSets()"
          class="problemset-list-button problemset-list-primary-button">
          筛选
        </button>
      </div>

      <!-- 右侧操作按钮 -->
      <div class="flex items-center space-x-2">
        <button @click="router.push('/problemsets/add')"
          class="problemset-list-button problemset-list-primary-button-green">
          新建题单
        </button>
        <button @click="showSelect = !showSelect; selected = []"
          class="problemset-list-button problemset-list-secondary-button">
          {{ showSelect ? "取消选择" : "选择" }}
        </button>
        <button v-if="showSelect && selected.length > 0" @click="deleteBatch"
          class="problemset-list-button problemset-list-danger-button">
          删除选中
        </button>
      </div>
    </div>


    <!-- 题单列表 -->
    <div class="problemset-list-items-container">
      <div v-for="ps in problemsets" :key="ps.id"
        class="problemset-list-item"
        :class="showSelect && selected.includes(ps.id) ? 'selected' : ''"
        @click="handleSelect(ps.id)">
        <div class="problemset-list-item-content">
          <h3 @click.stop="goDetail(ps.id)" class="problemset-list-item-title">{{ ps.title }}</h3>
          <p class="problemset-list-item-description">{{ ps.description }}</p>
          <p class="problemset-list-item-meta">
            课程: {{ ps.course?.title || '无' }} | 题目数: {{ ps.num_problems }}
          </p>
          <p class="problemset-list-item-meta">
            开始时间: {{ formatTime(ps.start_time) }} | 结束时间: {{ formatTime(ps.end_time) }}
          </p>
        </div>
        <div class="problemset-list-item-actions">
          <input v-if="showSelect" type="checkbox" v-model="selected" :value="ps.id" @click.stop class="problemset-list-item-checkbox" />
          <button @click.stop="goEdit(ps.id)" class="problemset-list-edit-button">编辑</button>
          <button @click.stop="deleteOne(ps.id)" class="problemset-list-delete-button">删除</button>
        </div>
      </div>
    </div>


    <!-- 分页器 -->
    <div class="problemset-list-pagination">
      <button @click="changePage(page - 1)" :disabled="page === 1" class="problemset-list-pagination-button">
        上一页
      </button>
      <span class="problemset-list-pagination-info">第 {{ page }} / {{ pages }} 页 (共 {{ total }} 条)</span>
      <button @click="changePage(page + 1)" :disabled="page === pages"
        class="problemset-list-pagination-button">
        下一页
      </button>
    </div>
  </div>
</template>