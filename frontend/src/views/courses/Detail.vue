<script setup>
import { ref, watch, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import axios from "axios";

const course = ref({
  id: null,
  course_name: "",
  description: "",
  teachers: [],
  students: [],
});

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

// 设置 axios token
axios.defaults.headers.common['Authorization'] = `Bearer ${userStore.accessToken}`;

// 拉取课程详情
const fetchCourse = async (courseId) => {
  if (!courseId) return;
  try {
    const res = await axios.get(`/api/courses/${courseId}`);
    console.log("fetchCourse 请求成功", res.data);
    course.value = res.data;
  } catch (err) {
    console.error("加载课程失败", err);
    course.value = {
      id: null,
      course_name: "课程不存在或无权限",
      description: "",
      teachers: [],
      students: [],
    };
  }
};

// 页面初始化
onMounted(() => {
  const cid = route.params.id || userStore.currentCourseId;
  if (!cid) return;

  if (!route.params.id) {
    // 如果 URL 没有 id，先替换成当前课程
    router.replace(`/courses/${cid}`);
  } else {
    fetchCourse(cid);
  }
});

// 当 route.params.id 改变时，重新拉取课程
watch(
  () => route.params.id,
  (newId) => {
    if (newId) fetchCourse(newId);
  },
  { immediate: true }
);

// 当 userStore.currentCourseId 改变时，跳转到新课程
watch(
  () => userStore.currentCourseId,
  (newId) => {
    if (newId && newId !== Number(route.params.id)) {
      router.push(`/courses/${newId}`);
    }
  }
);
</script>

<template>
  <div class="course-main">
    <div class="course-detail-container">
      <h1 class="course-detail-title">{{ course.course_name }}</h1>
      <p class="course-detail-description">{{ course.description || "暂无课程描述" }}</p>

      <div class="mb-6">
        <h2 class="course-detail-section-title">教师</h2>
        <ul class="course-detail-list">
          <li v-for="t in course.teachers" :key="t.id">
            {{ t.username }} <span class="course-detail-list-item-info">({{ t.school || "-" }} {{ t.profession || "-" }})</span>
          </li>
          <li v-if="course.teachers.length === 0" class="course-detail-empty-list">暂无教师</li>
        </ul>
      </div>

      <div>
        <h2 class="course-detail-section-title">学生</h2>
        <ul class="course-detail-list">
          <li v-for="s in course.students" :key="s.id">
            {{ s.username }} <span class="course-detail-list-item-info">({{ s.school || "-" }} {{ s.profession || "-" }})</span>
          </li>
          <li v-if="course.students.length === 0" class="course-detail-empty-list">暂无学生</li>
        </ul>
      </div>
    </div>
  </div>
</template>
