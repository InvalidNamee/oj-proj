<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import axios from "axios";
import TestCases from "@/components/TestCases.vue";
import EditableTestCases from "@/components/EditableTestCases.vue";
import MonacoEditor from "@/components/MonacoEditor.vue";
import GeminiPrompt from "@/components/GeminiPrompt.vue";
import "@/assets/pr7.css";

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
    id: `Sample ${tc.id}`
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
  <div style="display: flex; gap: 1.5rem; align-items: flex-start;">
    <div class="add-coding-problem-container">
      <div class="add-coding-problem-main-content">
        <!-- 左侧表单区域 -->
        <div class="add-coding-problem-form-section">
        <!-- 标题 & 描述 -->
        <div class="add-coding-problem-form-group">
          <label class="add-coding-problem-form-group-label">标题</label>
          <input v-model="title" placeholder="请输入题目标题" class="add-coding-problem-input" />
        </div>
        
        <div class="add-coding-problem-form-group">
          <label class="add-coding-problem-form-group-label">题目描述</label>
          <textarea v-model="description" rows="6" placeholder="请输入题目描述"
            class="add-coding-problem-textarea" />
        </div>
        
        <div class="add-coding-problem-grid">
          <div class="add-coding-problem-form-group">
            <label class="add-coding-problem-form-group-label">输入格式</label>
            <input v-model="inputFormat" placeholder="请输入输入格式" class="add-coding-problem-input" />
          </div>
          
          <div class="add-coding-problem-form-group">
            <label class="add-coding-problem-form-group-label">输出格式</label>
            <input v-model="outputFormat" placeholder="请输入输出格式" class="add-coding-problem-input" />
          </div>
        </div>
        
        <div class="add-coding-problem-form-group">
          <label class="add-coding-problem-form-group-label">说明 / Notes</label>
          <textarea v-model="notes" rows="3" placeholder="请输入说明或备注"
            class="add-coding-problem-textarea" />
        </div>

        <!-- 样例和测试用例 -->
        <EditableTestCases v-model="samples" title="样例" />
        <EditableTestCases v-model="testCases" title="测试用例" />
        
        <!-- 标程 -->
        <div class="monaco-editor-container">
          <MonacoEditor v-model="referenceSolution" />
        </div>
        
        <!-- 提交按钮 -->
        <div class="add-coding-problem-button-group">
          <button class="add-coding-problem-submit-button" @click="submit" :disabled="submitting">
            {{ submitting ? '提交中…' : '提交题目' }}
          </button>
        </div>
        
        <!-- 运行自测按钮 -->
        <div class="add-coding-problem-button-group">
          <button class="add-coding-problem-submit-button" @click="runSelfCheck" :disabled="submitting">
            {{ submitting ? '自测中…' : '运行自测' }}
          </button>
        </div>
      </div>
      </div>
      
      <!-- 自测结果 -->
      <div v-if="selfCheckResult" class="self-check-result">
        <h4>自测结果: {{ selfCheckResult.status }}</h4>
        <p v-if="selfCheckResult.score !== undefined">得分: {{ selfCheckResult.score }}</p>
        <div v-for="r in selfCheckResult.result || []" :key="r.name" class="self-check-result-item">
          <p>用例 {{ r.name }} - {{ r.status }}</p>
          <p v-if="r.diff" class="text-red-500 whitespace-pre-line">{{ r.diff }}</p>
          <p v-if="r.time">时间: {{ r.time }} ms</p>
          <p v-if="r.memory">内存: {{ r.memory }} KB</p>
        </div>
      </div>
    </div>
    
    <!-- 右侧Gemini生成题目部分 -->
    <div class="add-coding-problem-right-section">
      <!-- GeminiPrompt -->
      <div class="gemini-container">
        <GeminiPrompt
          @update:problem="updateProblem"
          @update:test_cases="updateTestCases"
          @update:reference_solution="updateReferenceSolution"
        />
      </div>
    </div>
  </div>
</template>