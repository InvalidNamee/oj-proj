<script setup>
import "@/assets/groups.css";
import { ref, onMounted, watch } from "vue";
import axios from "axios";
import { useRouter, useRoute } from "vue-router";
import { useUserStore } from "@/stores/user";

const groups = ref([]);
const total = ref(0);
const page = ref(1);
const perPage = ref(10);
const keyword = ref("");
const selected = ref([]);
const batchMode = ref(false);

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const fetchGroups = async () => {
  const res = await axios.get("/api/groups", {
    params: {
      course_id: userStore.currentCourseId,
      page: page.value,
      per_page: perPage.value,
      keyword: keyword.value || undefined,
    },
  });
  groups.value = res.data.groups || [];
  total.value = res.data.total || 0;
};

// 改变路由参数
const updateRoute = () => {
  router.push({
    path: "/groups",
    query: {
      page: page.value,
      per_page: perPage.value,
      keyword: keyword.value || "",
    },
  });
};

// 监听路由变化，恢复状态
watch(
  () => route.query,
  (q) => {
    page.value = Number(q.page) || 1;
    perPage.value = Number(q.per_page) || 10;
    keyword.value = q.keyword || "";
    fetchGroups();
  },
  { immediate: true }
);

watch(() => userStore.currentCourseId, () => {
  page.value = 1;
  fetchGroups();
});

// 翻页
const changePage = (p) => {
  if (p >= 1 && p <= Math.ceil(total.value / perPage.value)) {
    page.value = p;
    updateRoute();
  }
};

// 搜索
const search = () => {
  page.value = 1;
  updateRoute();
};

const goDetail = (id) => router.push(`/groups/${id}`);
const goEdit = (id) => router.push(`/groups/${id}/edit`);

const deleteOne = async (id) => {
  if (!confirm("确认删除该组？")) return;
  await axios.delete("/api/groups", { data: { group_ids: [id] } });
  fetchGroups();
};

const deleteBatch = async () => {
  if (!confirm(`确认删除选中的 ${selected.value.length} 个组？`)) return;
  await axios.delete("/api/groups", { data: { group_ids: selected.value } });
  selected.value = [];
  batchMode.value = false;
  fetchGroups();
};
</script>

<template>
  <div class="groups-container">
    <h2 class="groups-title">分组列表</h2>

    <!-- 搜索栏 -->
    <div class="groups-search-bar">
      <div class="groups-search-input-container">
        <input v-model="keyword" placeholder="按组名搜索"
          class="groups-search-input" />
        <button class="groups-search-button"
          @click="search">
          搜索
        </button>
      </div>

      <!-- 批量操作 -->
      <div class="groups-batch-actions">
        <button class="groups-batch-toggle-button"
          @click="batchMode = !batchMode; selected = []">
          {{ batchMode ? "取消" : "选择" }}
        </button>
        <button v-if="batchMode" class="groups-batch-delete-button"
          @click="deleteBatch">
          批量删除
        </button>
      </div>
    </div>

    <!-- 表格 -->
    <div class="groups-table-container">
      <table class="groups-table">
        <thead class="groups-table-header">
          <tr class="groups-table-header-row">
            <th class="groups-table-header-cell"></th>
            <th class="groups-table-header-cell" v-if="batchMode">
              <input type="checkbox" :checked="selected.length === groups.length"
                @change="selected = $event.target.checked ? groups.map(g => g.id) : []" />
            </th>
            <th class="groups-table-header-cell">ID</th>
            <th class="groups-table-header-cell">组名</th>
            <th class="groups-table-header-cell">所属课程</th>
            <th class="groups-table-header-cell">学生数</th>
            <th class="groups-table-header-cell">题单数</th>
            <th class="groups-table-header-cell">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="g in groups" :key="g.id" class="groups-table-row">
            <td class="groups-table-cell"></td>
            <td class="groups-table-cell" v-if="batchMode">
              <input type="checkbox" v-model="selected" :value="g.id" />
            </td>
            <td class="groups-table-cell">{{ g.id }}</td>
            <td class="groups-table-cell groups-name-link" @click="goDetail(g.id)">
              {{ g.name }}
            </td>
            <td class="groups-table-cell">{{ g.course.name }}</td>
            <td class="groups-table-cell">{{ g.student_cnt }}</td>
            <td class="groups-table-cell">{{ g.problemset_cnt }}</td>
            <td class="groups-table-cell">
              <template v-if="userStore.usertype !== 'student'">
                <button class="groups-action-button groups-edit-button" @click.stop="goEdit(g.id)">编辑</button>
                <button class="groups-action-button groups-delete-button" @click.stop="deleteOne(g.id)">删除</button>
              </template>
            </td>
          </tr>
          <tr v-if="groups.length === 0" class="groups-empty-row">
            <td :colspan="batchMode ? 8 : 7" class="groups-table-cell">
              暂无分组
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="groups-pagination">
      <button class="groups-pagination-button"
        :disabled="page === 1"
        @click="changePage(page - 1)">
        上一页
      </button>
      <span>第 {{ page }} / {{ Math.ceil(total / perPage) }} 页</span>
      <button class="groups-pagination-button"
        :disabled="page >= Math.ceil(total / perPage)"
        @click="changePage(page + 1)">
        下一页
      </button>
    </div>
  </div>
</template>
