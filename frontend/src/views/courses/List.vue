<script setup>
import { ref, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import axios from "axios";

const router = useRouter();
const route = useRoute();

// 数据
const courses = ref([]);
const page = ref(parseInt(route.query.page) || 1);
const perPage = ref(10);
const total = ref(0);

// 拉课程列表
const fetchCourses = async () => {
  try {
    const res = await axios.get("/api/courses", {
      params: { page: page.value, per_page: perPage.value }
    });
    courses.value = res.data.items;
    total.value = res.data.total;
  } catch (err) {
    console.error("获取课程失败", err);
  }
};

// 改变路由刷新
const updateRoute = () => {
  router.push({ path: "/courses", query: { page: page.value } });
};

// 删除课程
const deleteCourse = async (id) => {
  if (!confirm("确定要删除该课程吗？")) return;
  try {
    await axios.delete(`/api/courses/${id}`);
    fetchCourses();
  } catch (err) {
    alert(err.response?.data?.error || "删除失败");
  }
};

const goDetail = (id) => {
  router.push(`/courses/${id}`);
};

watch(() => route.query, () => fetchCourses(), { immediate: true });
</script>

<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">课程列表</h2>

    <div class="mb-4 flex justify-end">
      <button @click="router.push('/courses/add')" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
        添加课程
      </button>
    </div>

    <div class="space-y-4">
      <div v-for="course in courses" :key="course.id" class="bg-white shadow-md rounded-xl p-4 border border-gray-200 flex justify-between items-center">
        <div>
          <div class="font-medium" @click.prevent="goDetail(course.id)">{{ course.name }}</div>
          <div class="text-gray-500 text-sm">{{ course.description || '-' }}</div>
          <div class="text-gray-400 text-xs mt-1">更新时间: {{ course.timestamp }}</div>
        </div>
        <div class="flex gap-2">
          <button @click="router.push(`/courses/edit/${course.id}`)" class="text-blue-500 hover:underline text-sm">编辑</button>
          <button @click="deleteCourse(course.id)" class="text-red-500 hover:underline text-sm">删除</button>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="mt-6 flex justify-center items-center gap-4">
      <button :disabled="page <= 1" @click="page--; updateRoute()" class="px-3 py-1 border rounded disabled:opacity-50">上一页</button>
      <span>第 {{ page }} 页 / 共 {{ Math.ceil(total / perPage) }} 页</span>
      <button :disabled="page >= Math.ceil(total / perPage)" @click="page++; updateRoute()" class="px-3 py-1 border rounded disabled:opacity-50">下一页</button>
    </div>
  </div>
</template>
