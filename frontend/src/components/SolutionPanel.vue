<script setup>
import { ref, watch } from "vue";
import CodeMirrorEditor from "./CodeMirrorEditor.vue";
import DetailResults from "./DetailResults.vue";
import axios from "axios";

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ language: "python", code: "" })
  },
  testCases: {
    type: Array,
    default: () => []
  },
  samples: {
    type: Array,
    default: () => []
  }
});
const emit = defineEmits(["update:modelValue"]);

// 本地状态
const localSolution = ref({ ...props.modelValue });
watch(
  () => props.modelValue,
  (v) => {
    // 只有内容变化时才赋值
    if (
      localSolution.value.language !== v.language ||
      localSolution.value.code !== v.code
    ) {
      localSolution.value = { ...v };
    }
  },
  { deep: true }
);
watch(
  localSolution,
  (v) => {
    // 只有内容变化时才 emit
    if (
      props.modelValue.language !== v.language ||
      props.modelValue.code !== v.code
    ) {
      emit("update:modelValue", v);
    }
  },
  { deep: true }
);

// 自测
const loadingSelfCheck = ref(false);
const selfCheckResult = ref(null);
let pollTimer = null;

const runSelfCheck = async () => {
  if (loadingSelfCheck.value) return;
  loadingSelfCheck.value = true;
  selfCheckResult.value = null;

  try {
    // 直接用 props.testCases，不修改任何字段
    const res = await axios.post("/api/submissions/self_check", {
      language: localSolution.value.language,
      source_code: localSolution.value.code,
      test_cases: [...props.samples, ...props.testCases] // 样例和测试用例直接用原数组
    });

    const { submission_id } = res.data;

    pollTimer = setInterval(async () => {
      try {
        const resp = await axios.get(`/api/submissions/self_check/${submission_id}`);
        selfCheckResult.value = resp.data;
        if (resp.data.status !== "Pending") {
          clearInterval(pollTimer);
          loadingSelfCheck.value = false;
        }
      } catch (e) {
        clearInterval(pollTimer);
        loadingSelfCheck.value = false;
      }
    }, 1500);
  } catch (err) {
    console.error(err);
    selfCheckResult.value = { error: "自测失败" };
    loadingSelfCheck.value = false;
  }
};
</script>

<template>
  <div class="space-y-2">
    <div>
      <label class="font-semibold">语言</label>
      <select v-model="localSolution.language" class="border border-gray-300 rounded px-2 py-1 ml-2">
        <option value="python">Python</option>
        <option value="cpp">C++</option>
      </select>
    </div>
    <CodeMirrorEditor
      v-model="localSolution.code"
      :lang="localSolution.language === 'cpp' ? 'cpp' : (localSolution.language === 'python' ? 'python' : 'md')"
      :height="'300px'"
      :editable="true"
      />


    <button @click="runSelfCheck" :disabled="loadingSelfCheck"
      class="mt-2 px-4 py-2 rounded bg-green-500 text-white hover:bg-green-600 disabled:opacity-50">
      {{ loadingSelfCheck ? "测试中…" : "测试代码" }}
    </button>

    <!-- 测试结果展示 -->
    <DetailResults v-if="selfCheckResult" :results="selfCheckResult" />
  </div>
</template>