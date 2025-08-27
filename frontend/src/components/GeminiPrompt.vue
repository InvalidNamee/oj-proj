<script setup>
import { ref } from "vue";
import axios from "axios";

const emits = defineEmits([
  "update:problem",
  "update:test_cases",
  "update:reference_solution"
]);

const prompt = ref("");
const model = ref("gemini-2.5-flash");
const generating = ref(false);

const models = [
  { label: "Gemini 2.5 Flash", value: "gemini-2.5-flash" },
  { label: "Gemini 2.5 Flash Lite", value: "gemini-2.5-flash-lite" }
];

const generateProblem = async () => {
  if (generating.value) return;
  if (!prompt.value.trim()) {
    alert("请输入提示词");
    return;
  }

  generating.value = true;
  try {
    const res = await axios.post("/api/gemini/generate_problem", {
      prompt: prompt.value.trim(),
      model: model.value
    });

    const data = res.data;
    if (!data) throw new Error("返回内容为空或不是 JSON");

    if (data.problem) emits("update:problem", data.problem);
    if (data.test_cases) emits("update:test_cases", data.test_cases);
    if (data.reference_solution) emits("update:reference_solution", data.reference_solution);
    
  } catch (err) {
    console.error(err);
    alert(err.response?.data?.error || err.message || "生成失败");
  } finally {
    generating.value = false;
  }
};
</script>

<template>
  <div class="fixed top-24 right-4 w-80 p-4 bg-white border rounded shadow-lg z-50">
    <h2 class="text-lg font-bold mb-2">使用 Gemini 生成题目</h2>

    <textarea v-model="prompt" placeholder="输入提示词" rows="4"
      class="w-full border rounded px-2 py-1 mb-2 focus:ring-2 focus:ring-blue-400 outline-none"></textarea>

    <select v-model="model" class="w-full mb-2 border rounded px-2 py-1">
      <option v-for="m in models" :key="m.value" :value="m.value">{{ m.label }}</option>
    </select>

    <button @click="generateProblem" :disabled="generating" class="w-full py-2 rounded text-white"
      :class="generating ? 'bg-gray-400 cursor-not-allowed' : 'bg-purple-500 hover:bg-purple-600'">
      {{ generating ? "生成中…" : "生成题目" }}
    </button>
  </div>
</template>
