<script setup>
import { ref, computed, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import axios from "axios";
import TestCases from "@/components/TestCases.vue";
import GeminiPrompt from "@/components/GeminiPrompt.vue";
import SolutionPanel from "@/components/SolutionPanel.vue";

const router = useRouter();
const userStore = useUserStore();

const props = defineProps({
  courseId: {
    type: Number,
    required: true
  }
});

// 基本信息
const title = ref("");
const description = ref("");
const inputFormat = ref("");
const outputFormat = ref("");
const notes = ref("");

// 限制条件
const maxTime = ref(1);
const maxMemory = ref(256);

// 样例和测试用例
const samples = ref([{ id: 1, input: "", output: "" }]);
const testCases = ref([{ id: 1, input: "", output: "" }]);

// 标程
const referenceSolution = ref({ language: "python", code: "" });

// 提交 loading
const submitting = ref(false);

const allTestCases = computed(() => {
  const prefixedSamples = samples.value.map(tc => ({
    ...tc,
    id: `Sample ${tc.id}`
  }))
  const normalTests = testCases.value.map(tc => ({ ...tc }))
  return [...prefixedSamples, ...normalTests]
})

// 提交题目
const submit = async () => {
  if (submitting.value) return;
  submitting.value = true;

  try {
    const payload = {
      title: title.value,
      limitations: { maxTime: maxTime.value, maxMemory: maxMemory.value },
      description: {
        description: description.value,
        input_format: inputFormat.value,
        output_format: outputFormat.value,
        samples: samples.value,
        notes: notes.value
      },
      test_cases: testCases.value,
      reference_solution: referenceSolution.value,
      course_id: userStore.currentCourseId
    };

    const res = await axios.post("/api/problems/", payload);
    const problemId = res.data.id;

    if (confirm("题目创建成功！是否继续上传测试数据？")) {
      router.push(`/problems/${problemId}/edit/testcases`);
    } else {
      router.push("/problems");
    }
  } catch (err) {
    console.error(err);
    alert(err.response?.data?.error || "创建失败");
  } finally {
    submitting.value = false;
  }
};

// 接收 GeminiPrompt 的更新
const updateProblem = (p) => {
  title.value = p.title || "";
  description.value = p.description || "";
  inputFormat.value = p.input_format || "";
  outputFormat.value = p.output_format || "";
  samples.value = (p.samples || []).map((tc, i) => ({ id: i + 1, ...tc }));
  notes.value = p.notes || "";

  if (p.limitations) {
    if (p.limitations.maxTime !== undefined) {
      maxTime.value = p.limitations.maxTime;
    }
    if (p.limitations.maxMemory !== undefined) {
      maxMemory.value = p.limitations.maxMemory;
    }
  }
};
const updateTestCases = (tc) => {
  testCases.value = (tc || []).map((t, i) => ({ id: i + 1, ...t }));
};
const updateReferenceSolution = (rs) => {
  // 只有内容变化时才更新，避免死循环
  if (
    referenceSolution.value.language !== rs.language ||
    referenceSolution.value.code !== rs.code
  ) {
    referenceSolution.value = { ...rs };
  }
};
</script>

<template>
  <div class="add-coding-problem-container">
    <!-- 标题 -->
    <input v-model="title" placeholder="标题"
      class="add-coding-problem-input" />

  <!-- 题目描述 -->
  <textarea v-model="description" rows="6" placeholder="题目描述"
    class="w-full border border-gray-300 rounded px-2 py-2 focus:ring-2 focus:ring-blue-400" />

  <!-- 输入输出格式 -->
  <input v-model="inputFormat" placeholder="输入格式" class="w-full border border-gray-300 rounded px-2 py-2" />
  <input v-model="outputFormat" placeholder="输出格式" class="w-full border border-gray-300 rounded px-2 py-2" />

  <!-- Notes -->
  <textarea v-model="notes" rows="3" placeholder="说明 / Notes" class="w-full border border-gray-300 rounded px-2 py-2" />

  <!-- 样例和测试用例 -->
  <TestCases v-model="samples" title="样例" />
  <TestCases v-model="testCases" title="测试用例" />
  <!-- 标程 + 自测 -->
  <SolutionPanel v-model="referenceSolution" :test-cases="allTestCases" />

    <!-- 限制条件 -->
    <div class="add-coding-problem-grid">
      <input v-model.number="maxTime" type="number" placeholder="时间限制 (s)"
        class="add-coding-problem-input" />
      <input v-model.number="maxMemory" type="number" placeholder="内存限制 (MB)"
        class="add-coding-problem-input" />
    </div>
     <!-- 所属课程（固定） -->
    <input type="text" :value="courseName" disabled
      class="add-coding-problem-input add-coding-problem-disabled-input" />

    <!-- 提交按钮 -->
    <button @click="submit" :disabled="submitting"
      class="add-coding-problem-submit-button">
      {{ submitting ? '提交中…' : '提交' }}
    </button>
  </div>
</template>
