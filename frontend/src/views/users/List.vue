<script setup>
import { ref, watch, onMounted } from "vue";
import axios from "axios";
import { useRouter, useRoute } from "vue-router";
import { useUserStore } from "@/stores/user";
import '@/assets/users.css';

const userStore = useUserStore();
const router = useRouter();
const route = useRoute();

const users = ref([]);
const selected = ref([]);
const selectMode = ref(false);

const keyword = ref("");
const page = ref(parseInt(route.query.page) || 1);
const perPage = ref(15);
const total = ref(0);
const pages = ref(1);

const filters = ref({
  username: route.query.username || "",
  usertype: route.query.usertype || "",
  school: route.query.school || "",
  profession: route.query.profession || "",
});

const userTypeMap = {
  student: "学生",
  teacher: "教师",
  admin: "管理员"
};

// 拉取用户列表
const fetchUsers = async () => {
  try {
    const res = await axios.get("/api/users", {
      params: {
        page: page.value,
        per_page: perPage.value,
        course_id: userStore.currentCourseId,
        keyword: keyword.value || undefined,
        ...filters.value,
      },
    });
    users.value = res.data.users;
    total.value = res.data.total;
    pages.value = Math.ceil(total.value / perPage.value);
  } catch (err) {
    console.error(err);
  }
};

const updateRoute = () => {
  router.push({
    path: "/users",
    query: { page: page.value, ...filters.value },
  });
};

watch(
  () => route.query,
  (q) => {
    page.value = parseInt(q.page) || 1;
    filters.value = {
      username: q.username || "",
      usertype: q.usertype || "",
      school: q.school || "",
      profession: q.profession || "",
    };
    fetchUsers();
  },
  { immediate: true }
);

watch(() => userStore.currentCourseId, () => {
  page.value = 1;
  fetchUsers();
});

const goDetail = (id) => {
  if (!selectMode.value) router.push(`/users/${id}`);
};
const goEdit = (id) => router.push(`/users/edit/${id}`);

// 单个删除
const deleteOne = async (id) => {
  if (!confirm("确认删除该用户吗？")) return;
  try {
    await axios.delete("/api/users", { data: { user_ids: [id] } });
    fetchUsers();
  } catch (err) {
    console.error(err);
    alert(err.response?.data?.error || "删除失败");
  }
};

// 批量删除
const deleteBatch = async () => {
  if (selected.value.length === 0) {
    alert("请先选择要删除的用户");
    return;
  }
  if (!confirm(`确认删除选中的 ${selected.value.length} 个用户吗？`)) return;
  try {
    await axios.delete("/api/users", { data: { user_ids: selected.value } });
    selected.value = [];
    fetchUsers();
  } catch (err) {
    console.error(err);
    alert(err.response?.data?.error || "批量删除失败");
  }
};

// 从当前课程移除
const removeFromCourse = async (id) => {
  if (!confirm("确认将该用户从当前课程移除吗？")) return;
  try {
    await axios.patch(`/api/users/${id}/courses`, {
      courses: userStore.courses
        .filter(c => c.id !== userStore.currentCourseId)
        .map(c => c.id),
    });
    fetchUsers();
  } catch (err) {
    console.error(err);
    alert(err.response?.data?.error || "移除失败");
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
    updateRoute();
  }
};

onMounted(fetchUsers);
</script>

<template>
  <div class="user-list-container">
    <h2 class="user-list-title">用户列表</h2>

    <!-- 筛选栏 + 操作按钮 -->
    <div class="user-list-filter-bar">
      <div class="user-list-filter-group">
        <input v-model="filters.username" placeholder="用户名" class="user-list-input user-list-input-username" />
        <select v-model="filters.usertype" class="user-list-select">
          <option value="">全部类型</option>
          <option value="student">学生</option>
          <option value="teacher">教师</option>
          <option value="admin">管理员</option>
        </select>
      </div>
      <div class="user-list-filter-group">
        <input v-model="filters.school" placeholder="学校" class="user-list-input user-list-input-school" />
        <input v-model="filters.profession" placeholder="专业" class="user-list-input user-list-input-profession" />
      </div>
      <button @click="page = 1; updateRoute()" class="user-list-search-button">搜索</button>
      <!-- 操作按钮区，放最右 -->
      <div class="user-list-action-buttons">
        <button @click="$router.push('/users/register')"
          class="user-list-new-user-button">新建用户</button>
        <button v-if="!selectMode" @click="selectMode = true"
          class="user-list-select-button">选择</button>
        <div v-else class="user-list-batch-buttons">
          <button @click="deleteBatch" class="user-list-batch-delete-button">批量删除</button>
          <button @click="selectMode = false; selected = []"
            class="user-list-cancel-button">取消</button>
        </div>
      </div>
    </div>

    <!-- 表格 -->
    <div class="user-list-table-container">
      <table class="user-list-table">
        <thead class="user-list-table-header">
          <tr>
            <th class="user-list-table-header-cell"></th>
            <th class="user-list-table-header-cell" v-if="selectMode"></th>
            <th class="user-list-table-header-cell">UID</th>
            <th class="user-list-table-header-cell">用户名</th>
            <th class="user-list-table-header-cell">类型</th>
            <th class="user-list-table-header-cell">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;学校</th>
            <th class="user-list-table-header-cell">专业</th>
            <th class="user-list-table-header-cell">注册时间</th>
            <th class="user-list-table-header-cell">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id" @click="toggleSelect(u.id)"
            :class="[selectMode && selected.includes(u.id) ? 'user-list-table-row-selected' : 'user-list-table-row']">
            <td class="user-list-table-cell"></td>
            <td class="user-list-table-cell" v-if="selectMode">
              <input type="checkbox" :value="u.id" v-model="selected" @click.stop />
            </td>
            <td class="user-list-table-cell">{{ u.uid }}</td>
            <td class="user-list-table-cell user-list-username-link" @click.stop="goDetail(u.id)">{{ u.username }}
            </td>
            <td class="user-list-table-cell">{{ userTypeMap[u.usertype] || u.usertype }}</td>
            <td class="user-list-table-cell">{{ u.school || "-" }}</td>
            <td class="user-list-table-cell">{{ u.profession || "-" }}</td>
            <td class="user-list-table-cell">{{ new Date(u.timestamp).toLocaleString() }}</td>
            <td class="user-list-table-cell">
              <button class="user-list-action-button" @click.stop="goEdit(u.id)">编辑</button>
              <button v-if="userStore.usertype === 'admin'" class="user-list-delete-button"
                @click.stop="deleteOne(u.id)">删除</button>
              <button v-if="userStore.currentCourseId" class="user-list-remove-button" @click.stop="removeFromCourse(u.id)">
                移除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页器 -->
    <div class="user-list-pagination">
      <button @click="changePage(page - 1)" :disabled="page === 1"
        class="user-list-pagination-button">上一页</button>
      <span class="user-list-pagination-info">第 {{ page }} / {{ pages }} 页 (共 {{ total }} 条)</span>
      <button @click="changePage(page + 1)" :disabled="page === pages"
        class="user-list-pagination-button">下一页</button>
    </div>
  </div>
</template>
