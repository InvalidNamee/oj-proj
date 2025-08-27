
<script setup>
import { ref } from "vue";
import AddLegacyProblem from "@/views/problemsets/AddLegacyProblem.vue";
import AddCodingProblem from "@/views/problemsets/AddCodingProblem.vue";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const courseId = userStore.currentCourseId;
const problemType = ref("coding");
</script>

<template>
  <div class="add-problem-container">
    <h2>新建题目</h2>
    <!-- 题目类型选择器（只在外层） -->
    <div>
      <label>题目类型:</label>
      <select v-model="problemType">
        <option value="coding">编程题</option>
        <option value="single">单选题</option>
        <option value="multiple">多选题</option>
        <option value="fill">填空题</option>
        <option value="subjective">主观题</option>
      </select>
    </div>
    
    <!-- 统一渲染表单 -->
    <AddLegacyProblem
      v-if="['single','multiple','fill','subjective'].includes(problemType)"
      :problem-type="problemType"
      :course-id="courseId"
    />
    <AddCodingProblem
      v-else
      :course-id="courseId"
    />
  </div>
</template>