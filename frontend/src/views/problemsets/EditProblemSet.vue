<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import axios from "axios";
import ProblemSelector from "@/components/ProblemSelector.vue";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const psid = route.params.id;

const title = ref("");
const description = ref("");
const Selected = ref([]);

// 当前课程
const courseId = computed(() => userStore.currentCourseId);
const courseName = computed(() => {
  const course = userStore.courses.find(c => c.id === userStore.currentCourseId);
  return course ? course.name : '';
});

const fetchProblemSet = async () => {
  const res = await axios.get(`/api/problemsets/${psid}`);
  const data = res.data;
  title.value = data.title;
  description.value = data.description;
  Selected.value = data.problems.map(p => p.id);
};

const submit = async () => {
  if (!courseId.value) {
    alert("请先选择课程");
    return;
  }
  await axios.put(`/api/problemsets/${psid}`, {
    title: title.value,
    description: description.value,
    course_id: courseId.value,
    problem_ids: Selected.value,
  });
  router.push("/problemsets");
};

onMounted(fetchProblemSet);
</script>

<template>
  <div class="max-w-2xl mx-auto mt-12 p-6 rounded-xl bg-white shadow">
    <h2 class="text-2xl font-bold mb-6">编辑题单</h2>
    <div class="space-y-4">
      <input
        v-model="title"
        placeholder="题单标题"
        class="w-full border border-gray-300 rounded px-3 py-2"
      />
      <textarea
        v-model="description"
        rows="4"
        placeholder="描述"
        class="w-full border border-gray-300 rounded px-3 py-2"
      ></textarea>

      <!-- 课程显示 -->
      <div>
        <label class="block mb-1 text-gray-700">所属课程（不可更改）</label>
        <input
          type="text"
          :value="courseName"
          disabled
          class="border border-gray-300 px-2 py-1 w-full bg-gray-100 cursor-not-allowed"
        />
      </div>

      <!-- Coding 题目选择器 -->
      <div>
        <label class="block mb-1 text-gray-700">选择代码题</label>
        <ProblemSelector v-model="Selected" />
      </div>

      <button
        @click="submit"
        class="w-full bg-blue-500 text-white px-3 py-2 rounded hover:bg-blue-600"
      >
        提交修改
      </button>
    </div>
  </div>
</template>
