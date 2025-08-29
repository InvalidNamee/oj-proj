<script setup>
import { ref } from "vue";
import axios from "axios";

const emits = defineEmits([
  "update:problem",
  "update:test_cases",
  "update:reference_solution"
]);

const prompt = ref("");
const model = ref("gemini-2.5-flash-lite");
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
  <div class="gemini-container">
    <h2 class="gemini-title">使用 Gemini 生成题目</h2>

    <textarea
      v-model="prompt"
      placeholder="输入提示词"
      rows="4"
      class="gemini-textarea"
    ></textarea>

    <select v-model="model" class="gemini-select">
      <option v-for="m in models" :key="m.value" :value="m.value">{{ m.label }}</option>
    </select>

    <button
      @click="generateProblem"
      :disabled="generating"
      :class="['gemini-button', generating ? 'disabled' : '']"
    >
      {{ generating ? "生成中…" : "生成题目" }}
    </button>
  </div>
</template>

<style scoped>
.gemini-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 16px;
  border-radius: 8px;
  background-color: #fafafa;
}

.gemini-title {
  font-size: 1.5em;
  margin-bottom: 12px;
  text-align: center;
}

.gemini-textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  resize: vertical;
  font-size: 14px;
  margin-bottom: 12px;
  box-sizing: border-box;
}

.gemini-select {
  width: 100%;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ccc;
  margin-bottom: 12px;
  font-size: 14px;
  box-sizing: border-box;
}

.gemini-button {
  width: 100%;
  padding: 10px 0;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  color: white;
  background-color: #7b5cf6; /* 紫色 */
  cursor: pointer;
  transition: background-color 0.2s;
}

.gemini-button:hover {
  background-color: #6d4ce2;
}

.gemini-button.disabled {
  background-color: #999;
  cursor: not-allowed;
}
</style>
