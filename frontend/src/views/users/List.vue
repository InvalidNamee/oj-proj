<script setup>
import { ref, watch, onMounted } from "vue";
import axios from "axios";
import { useRouter, useRoute } from "vue-router";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const router = useRouter();
const route = useRoute();

const users = ref([]);
const selected = ref([]); // 选中的 uid
const selectMode = ref(false); // 是否进入选择模式

// 搜索 & 分页
const keyword = ref("");
const page = ref(parseInt(route.query.page) || 1);
const perPage = ref(15);
const total = ref(0);
const pages = ref(1);

// 筛选条件
const filters = ref({
  username: route.query.username || "",
  usertype: route.query.usertype || "",
  school: route.query.school || "",
  profession: route.query.profession || "",
});

// 用户类型映射
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

// 改变路由参数并刷新
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

// 点击行选择
const toggleSelect = (id) => {
  if (!selectMode.value) return;
  const idx = selected.value.indexOf(id);
  if (idx >= 0) selected.value.splice(idx, 1);
  else selected.value.push(id);
};

// 分页切换
const changePage = (p) => {
  if (p >= 1 && p <= pages.value) {
    page.value = p;
    updateRoute();
  }
};

onMounted(fetchUsers);
</script>

<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">用户列表</h2>

    <!-- 筛选栏 -->
    <div class="mb-4 flex flex-wrap items-center gap-2">
      <input v-model="filters.username" placeholder="用户名" class="border rounded px-2 py-1 w-36" />
      <select v-model="filters.usertype" class="border rounded px-2 py-1 w-32">
        <option value="">全部类型</option>
        <option value="student">学生</option>
        <option value="teacher">教师</option>
        <option value="admin">管理员</option>
      </select>
      <input v-model="filters.school" placeholder="学校" class="border rounded px-2 py-1 w-40" />
      <input v-model="filters.profession" placeholder="专业" class="border rounded px-2 py-1 w-40" />
      <button @click="page=1; updateRoute()" class="px-3 py-1 bg-blue-500 text-white rounded">搜索</button>
    </div>

    <!-- 顶部操作栏 -->
    <div class="flex justify-between items-center mb-2">
      <div class="flex space-x-2">
        <button @click="$router.push('/users/add')" class="px-4 py-2 bg-blue-500 text-white rounded shadow">新建用户</button>
        <button v-if="!selectMode" @click="selectMode=true" class="px-4 py-2 bg-gray-500 text-white rounded shadow">选择</button>
        <div v-else class="flex space-x-2">
          <button @click="deleteBatch" class="px-4 py-2 bg-red-500 text-white rounded shadow">批量删除</button>
          <button @click="selectMode=false; selected=[]" class="px-4 py-2 bg-gray-400 text-white rounded shadow">取消</button>
        </div>
      </div>
    </div>

    <!-- 表格 -->
    <div class="bg-white shadow rounded-lg overflow-hidden">
      <table class="w-full text-left text-sm">
        <thead class="bg-gray-50 text-gray-700">
          <tr>
            <th class="p-3" v-if="selectMode"></th>
            <th class="p-3">UID</th>
            <th class="p-3">用户名</th>
            <th class="p-3">类型</th>
            <th class="p-3">学校</th>
            <th class="p-3">专业</th>
            <th class="p-3">注册时间</th>
            <th class="p-3">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="u in users"
            :key="u.id"
            @click="toggleSelect(u.id)"
            :class="['hover:bg-gray-50 transition', selectMode && selected.includes(u.id) ? 'bg-blue-100' : '']"
          >
            <td class="p-3" v-if="selectMode">
              <input type="checkbox" :value="u.id" v-model="selected" @click.stop/>
            </td>
            <td class="p-3">{{ u.uid }}</td>
            <td class="p-3 cursor-pointer text-blue-600 hover:underline" @click.stop="goDetail(u.id)">{{ u.username }}</td>
            <td class="p-3">{{ userTypeMap[u.usertype] || u.usertype }}</td>
            <td class="p-3">{{ u.school || "-" }}</td>
            <td class="p-3">{{ u.profession || "-" }}</td>
            <td class="p-3">{{ new Date(u.timestamp).toLocaleString() }}</td>
            <td class="p-3 space-x-2">
              <button class="text-blue-500 hover:underline" @click.stop="goEdit(u.id)">编辑</button>
              <button class="text-red-500 hover:underline" @click.stop="deleteOne(u.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页器 -->
    <div class="flex justify-center items-center mt-4 space-x-2">
      <button @click="changePage(page-1)" :disabled="page===1" class="px-3 py-1 border rounded disabled:opacity-50">上一页</button>
      <span>第 {{ page }} / {{ pages }} 页 (共 {{ total }} 条)</span>
      <button @click="changePage(page+1)" :disabled="page===pages" class="px-3 py-1 border rounded disabled:opacity-50">下一页</button>
    </div>
  </div>
</template>
