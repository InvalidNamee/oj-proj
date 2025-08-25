<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import EditCodingProblem from "@/views/problemsets/EditCodingProblem.vue";
import EditLegacyProblem from "@/views/problemsets/EditLegacyProblem.vue";
import axios from "axios";

const route = useRoute();
const problemId = route.params.id;
const problemType = ref("coding"); // 默认

const problemData = ref(null);
const loading = ref(true);

onMounted(async () => {
  // 拉取题目详情，判断类型
  const res = await axios.get(`/api/problems/${problemId}`);
  problemData.value = res.data;
  problemType.value = res.data.type || "coding";
  loading.value = false;
});
</script>

<template>
  <div class="max-w-2xl mx-auto mt-12 p-6 rounded-xl bg-white shadow">
    <h2 class="text-2xl font-bold mb-6">编辑题目</h2>
    <div v-if="loading">加载中...</div>
    <template v-else>
      <div class="mb-6">
        <label class="mr-2">题目类型:</label>
        <select v-model="problemType" class="border p-2 rounded border-gray-300" disabled>
          <option value="coding">编程题</option>
          <option value="single">单选题</option>
          <option value="multiple">多选题</option>
          <option value="fill">填空题</option>
          <option value="subjective">主观题</option>
        </select>
      </div>
      <EditLegacyProblem
        v-if="['single','multiple','fill','subjective'].includes(problemType)"
        :problem-id="problemId"
        :problem-data="problemData"
      />
      <EditCodingProblem
        v-else
        :problem-id="problemId"
        :problem-data="problemData"
      />
    </template>
  </div>
</template>