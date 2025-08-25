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
  <div class="p-6">
    <div class="bg-white shadow-lg rounded-xl p-6">
      <h1 class="text-3xl font-bold mb-4">{{ course.course_name }}</h1>
      <p class="text-gray-700 mb-6">{{ course.description || "暂无课程描述" }}</p>

      <div class="mb-6">
        <h2 class="text-2xl font-semibold mb-2">教师</h2>
        <ul class="list-disc pl-6">
          <li v-for="t in course.teachers" :key="t.id">
            {{ t.username }} <span class="text-gray-500">({{ t.school || "-" }} {{ t.profession || "-" }})</span>
          </li>
          <li v-if="course.teachers.length === 0" class="text-gray-400">暂无教师</li>
        </ul>
      </div>

      <div>
        <h2 class="text-2xl font-semibold mb-2">学生</h2>
        <ul class="list-disc pl-6">
          <li v-for="s in course.students" :key="s.id">
            {{ s.username }} <span class="text-gray-500">({{ s.school || "-" }} {{ s.profession || "-" }})</span>
          </li>
          <li v-if="course.students.length === 0" class="text-gray-400">暂无学生</li>
        </ul>
      </div>
    </div>
  </div>
</template>
