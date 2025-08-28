<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import axios from "axios";
import TestCases from "@/components/TestCases.vue";
import MonacoEditor from "@/components/MonacoEditor.vue";
import GeminiPrompt from "@/components/GeminiPrompt.vue";

const router = useRouter();
const userStore = useUserStore();

const props = defineProps({ courseId: { type: Number, required: true } });

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
const samples = ref([]);
const testCases = ref([]);

// 标程
const referenceSolution = ref({ language: "python", code: "" });

// 提交 & 自测 loading
const submitting = ref(false);
const selfCheckResult = ref(null);
let pollTimer = null;

// 合并所有测试用例
const allTestCases = computed(() => {
  const prefixedSamples = samples.value.map(tc => ({
    ...tc,
    id: `Sample_${tc.id}`
  }))
  return [...prefixedSamples, ...testCases.value]
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

// 自测逻辑（参考题目详情页）
const runSelfCheck = async () => {
  if (!referenceSolution.value.code) return;
  submitting.value = true;
  selfCheckResult.value = null;
  if (pollTimer) clearInterval(pollTimer);

  try {
    const res = await axios.post("/api/submissions/self_check", {
      language: referenceSolution.value.language,
      source_code: referenceSolution.value.code,
      test_cases: allTestCases.value
    });
    const submissionId = res.data.submission_id;
    pollSelfCheck(submissionId);
  } catch (err) {
    console.error(err);
    alert(err.response?.data?.error || "自测失败");
    submitting.value = false;
  }
};

const pollSelfCheck = (id) => {
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(async () => {
    try {
      const res = await axios.get(`/api/submissions/self_check/${id}`);
      if (res.data.status && !['Pending', 'Judging'].includes(res.data.status)) {
        selfCheckResult.value = res.data;
        submitting.value = false;
        clearInterval(pollTimer);
      }
    } catch (err) {
      console.error(err);
      submitting.value = false;
      clearInterval(pollTimer);
    }
  }, 2000);
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
    if (p.limitations.maxTime !== undefined) maxTime.value = p.limitations.maxTime;
    if (p.limitations.maxMemory !== undefined) maxMemory.value = p.limitations.maxMemory;
  }
};
const updateTestCases = (tc) => testCases.value = (tc || []).map((t, i) => ({ id: i + 1, ...t }));
const updateReferenceSolution = (rs) => {
  if (referenceSolution.value.language !== rs.language || referenceSolution.value.code !== rs.code) {
    referenceSolution.value = { ...rs };
  }
};
</script>

<template>
  <div class="add-coding-problem-container">
    <!-- 标题 & 描述 -->
    <input v-model="title" placeholder="标题" class="add-coding-problem-input" />
    <textarea v-model="description" rows="6" placeholder="题目描述"
      class="w-full border border-gray-300 rounded px-2 py-2 focus:ring-2 focus:ring-blue-400" />
    <input v-model="inputFormat" placeholder="输入格式" class="w-full border border-gray-300 rounded px-2 py-2" />
    <input v-model="outputFormat" placeholder="输出格式" class="w-full border border-gray-300 rounded px-2 py-2" />
    <textarea v-model="notes" rows="3" placeholder="说明 / Notes"
      class="w-full border border-gray-300 rounded px-2 py-2" />

    <!-- 样例和测试用例 -->
    <TestCases v-model="samples" title="样例" />
    <TestCases v-model="testCases" title="测试用例" />

    <!-- 标程 + 自测 -->
    <MonacoEditor v-model="referenceSolution" />
     
    <div class="flex gap-2 mt-2">
      <button class="btn" @click="runSelfCheck" :disabled="submitting">
        {{ submitting ? '自测中…' : '自测' }}
      </button>
      <button class="btn" @click="submit" :disabled="submitting">
        {{ submitting ? '提交中…' : '提交' }}
      </button>
    </div>

    <!-- 自测结果 -->
    <div v-if="selfCheckResult" class="self-check-result mt-4">
      <h4>自测结果: {{ selfCheckResult.status }}</h4>
      <p v-if="selfCheckResult.score !== undefined">得分: {{ selfCheckResult.score }}</p>
      <div v-for="r in selfCheckResult.result || []" :key="r.name" class="mt-2 p-2 border rounded">
        <p>用例 {{ r.name }} - {{ r.status }}</p>
        <p v-if="r.diff" class="text-red-500 whitespace-pre-line">{{ r.diff }}</p>
        <p v-if="r.time">时间: {{ r.time }} ms</p>
        <p v-if="r.memory">内存: {{ r.memory }} KB</p>
      </div>
    </div>

    <GeminiPrompt
      @update:problem="updateProblem"
      @update:test_cases="updateTestCases"
      @update:reference_solution="updateReferenceSolution"
    />
  </div>
</template>