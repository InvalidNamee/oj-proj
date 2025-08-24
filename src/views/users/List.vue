<script setup>
import { ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import { useUserStore } from "@/stores/user";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

// 数据
const users = ref([]);
const page = ref(parseInt(route.query.page) || 1);
const perPage = ref(10);
const total = ref(0);

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

// 拉数据
const fetchUsers = async () => {
  try {
    const res = await axios.get("/api/users", {
      params: {
        page: page.value,
        per_page: perPage.value,
        course_id: userStore.currentCourseId,
        ...filters.value,
      },
    });
    users.value = res.data.users;
    total.value = res.data.total;
  } catch (err) {
    console.error("获取用户失败", err);
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

watch(
  () => userStore.currentCourseId,
  () => {
    page.value = 1;
    fetchUsers();
  }
);

const deleteUser = async (id) => {
  if (!confirm("确定要删除该用户吗？")) return;
  try {
    const res = await axios.delete("/api/users", { data: { user_ids: [id] } });
    if (res.data.success) {
      fetchUsers();
    }
  } catch (err) {
    alert(err.response?.data?.error || "删除失败");
  }
};

const removeCourse = async (userId, courseId) => {
  if (!confirm('确定要从该用户移除这门课程吗？')) return;

  try {
    const user = users.value.find(u => u.id === userId);
    if (!user) return;

    const newCourseIds = user.courses
      .filter(c => c.id !== courseId)
      .map(c => c.id);

    const res = await axios.patch(`/api/users/${userId}/courses`, {
      course_ids: newCourseIds
    });

    if (res.data.success) {
      fetchUsers(); // 移除课程成功后刷新列表
    }
  } catch (err) {
    alert(err.response?.data?.error || '移除课程失败');
  }
};
</script>

<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">用户列表</h2>
    <!-- 筛选 -->
    <div class="mb-6 flex flex-wrap items-center gap-3">
      <input v-model="filters.uid" placeholder="UID" class="border border-gray-300 p-2 rounded w-28" />
      <input v-model="filters.username" placeholder="用户名" class="border border-gray-300 p-2 rounded w-36" />
      <select v-model="filters.usertype" class="border border-gray-300 p-2 rounded w-32">
        <option value="">全部类型</option>
        <option value="student">学生</option>
        <option value="teacher">教师</option>
        <option value="admin">管理员</option>
      </select>
      <input v-model="filters.school" placeholder="学校" class="border border-gray-300 p-2 rounded w-40" />
      <input v-model="filters.profession" placeholder="专业" class="border border-gray-300 p-2 rounded w-40" />
      <button @click="updateRoute" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
        搜索
      </button>
    </div>

    <!-- 用户列表 -->
    <div class="space-y-4">
      <div v-for="user in users" :key="user.id"
        class="bg-white shadow-md rounded-xl px-6 py-4 grid grid-cols-6 gap-4 items-center hover:shadow-lg transition border border-gray-200">
        <div class="font-medium text-gray-800" @click="router.push(`/users/${user.id}`)" style="cursor: pointer;">
          {{ user.username }}
          <span class="text-gray-400 text-xs ml-1">#{{ user?.uid }}</span>
        </div>
        <div class="text-gray-600">{{ userTypeMap[user?.usertype] || user?.usertype }}</div>
        <div class="text-gray-600">{{ user?.school || "-" }}</div>
        <div class="text-gray-600">{{ user?.profession || "-" }}</div>
        <div class="text-gray-500 text-sm">{{ new Date(user.timestamp).toLocaleString() }}</div>
        <div class="text-right flex flex-wrap justify-end gap-2">
          <!-- 管理员按钮 -->
          <template v-if="userStore.usertype === 'admin'">
            <button class="text-sm text-blue-500 hover:underline" @click="router.push(`/users/edit/${user.id}`)">
              编辑
            </button>
            <button v-if="userStore.currentCourseId !== 'null'" class="text-sm text-red-500 hover:underline" @click="removeCourse(user.id, userStore.currentCourseId)">
              移除
            </button>
            <button class="text-sm text-red-500 hover:underline" @click="deleteUser(user.id)">
              删除
            </button>
          </template>

          <!-- 教师操作学生 -->
          <template v-else-if="userStore.usertype === 'teacher' && user.usertype === 'student'">
            <button class="text-sm text-blue-500 hover:underline" @click="router.push(`/users/edit/${user.id}`)">
              编辑
            </button>
            <button class="text-sm text-red-500 hover:underline" @click="removeCourse(user.id, userStore.currentCourseId)">
              移除
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="mt-8 flex justify-center items-center gap-4">
      <button :disabled="page <= 1" @click="page--; updateRoute()" class="px-3 py-1 border rounded disabled:opacity-50">
        上一页
      </button>
      <span>第 {{ page }} 页 / 共 {{ Math.ceil(total / perPage) }} 页</span>
      <button :disabled="page >= Math.ceil(total / perPage)" @click="page++; updateRoute()"
        class="px-3 py-1 border rounded disabled:opacity-50">
        下一页
      </button>
    </div>
  </div>
</template>
