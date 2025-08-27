<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import axios from "axios";
import ProblemSelector from "@/components/ProblemSelector.vue";

const router = useRouter();
const userStore = useUserStore();

const title = ref("");
const description = ref("");
const Selected = ref([]);

// 当前课程
const courseId = computed(() => userStore.currentCourseId);
const courseName = computed(() => {
  const course = userStore.courses.find(c => c.id === userStore.currentCourseId);
  return course ? course.name : '';
});

const submit = async () => {
  if (!courseId.value) {
    alert("请先选择课程");
    return;
  }
  await axios.post("/api/problemsets/", {
    title: title.value,
    description: description.value,
    course_id: courseId.value,
    problem_ids: Selected.value,
  });
  router.push("/problemsets");
};
</script>

<template>
  <div class="add-problemset-container">
    <h2 class="add-problemset-title">新建题单</h2>
    <div class="add-problemset-space-y-4">
      <input
        v-model="title"
        placeholder="题单标题"
        class="add-problemset-input"
      />
      <textarea
        v-model="description"
        rows="4"
        placeholder="描述"
        class="add-problemset-textarea"
      ></textarea>

      <!-- 课程显示 -->
      <div>
        <label class="add-problemset-label">所属课程</label>
        <input
          type="text"
          :value="courseName"
          disabled
          class="add-problemset-course-input"
        />
        <p class="text-xs text-gray-500 mt-1">
          题单必须绑定课程，如需更改，请先切换当前课程。
        </p>
      </div>

      <!-- 题目选择器 -->
      <div>
        <label class="add-problemset-label">选择代码题</label>
        <ProblemSelector v-model="Selected" />
      </div>

      <button
        @click="submit"
        class="add-problemset-button"
      >
        创建题单
      </button>
    </div>
  </div>
</template>
