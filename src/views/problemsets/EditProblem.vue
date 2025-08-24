<template>
  <div class="max-w-2xl mx-auto mt-12 p-6 rounded-xl bg-white shadow">
    <h2 class="text-2xl font-bold mb-6">编辑题目</h2>

    <div class="space-y-4">
      <!-- 标题 -->
      <input v-model="title" placeholder="标题"
        class="w-full border border-gray-300 rounded px-3 py-2 text-gray-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none" />

      <!-- 描述 -->
      <textarea v-model="description" rows="6" placeholder="题目描述"
        class="w-full border border-gray-300 rounded px-3 py-2 text-gray-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none"></textarea>

      <!-- 限制条件 -->
      <div class="grid grid-cols-2 gap-4">
        <input v-model="maxTime" type="number" placeholder="时间限制 (s)"
          class="w-full border border-gray-300 rounded px-3 py-2 text-gray-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none" />
        <input v-model="maxMemory" type="number" placeholder="内存限制 (MB)"
          class="w-full border border-gray-300 rounded px-3 py-2 text-gray-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none" />
      </div>

      <!-- 所属课程 -->
      <select v-model="courseId"
        class="w-full border border-gray-300 rounded px-3 py-2 text-gray-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none">
        <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>

      <!-- 提交按钮 -->
      <button @click="submitProblem" class="w-full bg-blue-500 text-white px-3 py-2 rounded hover:bg-blue-600">
        提交修改
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";

const route = useRoute();
const router = useRouter();
const problemId = route.params.id;

const title = ref("");
const description = ref("");
const maxTime = ref("");
const maxMemory = ref("");
const courseId = ref("");
const courses = ref([]);

const fetchCourses = async () => {
  const res = await axios.get("/api/courses");
  courses.value = res.data.items;
};

const fetchProblem = async () => {
  const res = await axios.get(`/api/coding_problems/${problemId}`);
  const data = res.data;
  title.value = data.title;
  description.value = data.description;
  maxTime.value = data.limitations.maxTime;
  maxMemory.value = data.limitations.maxMemory;
  courseId.value = data.course_id;
};

const submitProblem = async () => {
  try {
    const form = new FormData();
    form.append(
      "meta",
      JSON.stringify({
        title: title.value,
        description: description.value,
        limitations: { maxTime: maxTime.value, maxMemory: maxMemory.value },
        course_id: courseId.value,
      })
    );

    await axios.put(`/api/coding_problems/${problemId}`, form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    alert("题目修改成功");
    router.push("/problems");
  } catch (err) {
    alert(err.response?.data?.error || "提交失败");
  }
};

onMounted(() => {
  fetchCourses();
  fetchProblem();
});
</script>
