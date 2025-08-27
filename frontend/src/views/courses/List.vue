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
  <div class="course-main">
    <h2 class="course-list-title">课程列表</h2>

    <div class="course-list-actions">
      <button @click="router.push('/courses/add')" class="course-list-add-button">
        添加课程
      </button>
    </div>

    <div class="course-list-items">
      <div v-for="course in courses" :key="course.id" class="course-list-item">
        <div>
          <div class="course-list-item-content" @click.prevent="goDetail(course.id)">{{ course.name }}</div>
          <div class="course-list-item-description">{{ course.description || '-' }}</div>
          <div class="course-list-item-timestamp">更新时间: {{ course.timestamp }}</div>
        </div>
        <div class="course-list-item-actions">
          <button @click="router.push(`/courses/edit/${course.id}`)" class="course-list-edit-button">编辑</button>
          <button @click="deleteCourse(course.id)" class="course-list-delete-button">删除</button>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="course-list-pagination">
      <button :disabled="page <= 1" @click="page--; updateRoute()" class="course-list-pagination-button">上一页</button>
      <span class="course-list-pagination-info">第 {{ page }} 页 / 共 {{ Math.ceil(total / perPage) }} 页</span>
      <button :disabled="page >= Math.ceil(total / perPage)" @click="page++; updateRoute()" class="course-list-pagination-button">下一页</button>
    </div>
  </div>
</template>
