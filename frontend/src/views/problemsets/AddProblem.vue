
<script setup>
import { ref, watch } from "vue";
import AddLegacyProblem from "@/views/problemsets/AddLegacyProblem.vue";
import AddCodingProblem from "@/views/problemsets/AddCodingProblem.vue";
import AddSingleProblem from "@/views/problemsets/AddSingleProblem.vue";
import AddMultipleProblem from "@/views/problemsets/AddMultipleProblem.vue";
import AddFillProblem from "@/views/problemsets/AddFillProblem.vue";
import AddSubjectiveProblem from "@/views/problemsets/AddSubjectiveProblem.vue";
import { useUserStore } from "@/stores/user";
import { useRoute } from "vue-router";
import "@/assets/pr7.css";

const userStore = useUserStore();
const courseId = userStore.currentCourseId;
const route = useRoute();

// 从路由参数获取题目类型，如果没有则默认为coding
const problemType = ref(route.params.type || "coding");

// 监听路由参数变化
watch(() => route.params.type, (newType) => {
  problemType.value = newType || "coding";
});
</script>

<template>
  <div >
    
    <!-- 统一渲染表单 -->
    <AddSingleProblem
      v-if="problemType === 'single'"
      :problem-type="problemType"
      :course-id="courseId"
    />
    <AddMultipleProblem
      v-else-if="problemType === 'multiple'"
      :problem-type="problemType"
      :course-id="courseId"
    />
    <AddFillProblem
      v-else-if="problemType === 'fill'"
      :problem-type="problemType"
      :course-id="courseId"
    />
    <AddSubjectiveProblem
      v-else-if="problemType === 'subjective'"
      :problem-type="problemType"
      :course-id="courseId"
    />
    <AddLegacyProblem
      v-else-if="['single','multiple','fill','subjective'].includes(problemType)"
      :problem-type="problemType"
      :course-id="courseId"
    />
    <AddCodingProblem
      v-else
      :course-id="courseId"
      :problem-type="problemType"
    />
  </div>
</template>