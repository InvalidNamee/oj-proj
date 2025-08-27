<script setup>
import '@/assets/components.css'
import { ref, watch } from "vue";

const props = defineProps({
  problemType: { type: String, required: true },
  initialTestCases: { type: Object, default: () => ({}) } // 支持传入初始值
});
const emit = defineEmits(["update:testCases"]);

const options = ref([]);
const answers = ref("");

// 初始化
function initFromProps() {
  if (props.problemType === "single" || props.problemType === "multiple") {
    options.value = props.initialTestCases.options || [];
    answers.value = props.initialTestCases.answers || (props.problemType === "single" ? "" : []);
  } else if (props.problemType === "fill") {
    answers.value = props.initialTestCases.answers || [];
    options.value = [];
  } else {
    options.value = [];
    answers.value = null;
  }
}

initFromProps();

// 类型变化时重置
watch(() => props.problemType, initFromProps);

// 添加/删除操作
let nextOptId = options.value.length ? Math.max(...options.value.map(o => o.id)) + 1 : 1;
function addOption() {
  options.value.push({ id: nextOptId++, content: "" });
}
function removeOption(id) {
  options.value = options.value.filter(opt => opt.id !== id);
}
function addAnswer() {
  answers.value.push("");
}
function removeAnswer(idx) {
  answers.value.splice(idx, 1);
}

// 每次变化 emit
watch([options, answers], () => {
  if (props.problemType === "single" || props.problemType === "multiple") {
    emit("update:testCases", { options: options.value, answers: answers.value });
  } else if (props.problemType === "fill") {
    emit("update:testCases", { answers: answers.value });
  } else {
    emit("update:testCases", {});
  }
}, { deep: true });
</script>

<template>
  <div>
    <!-- 单选/多选 -->
    <div v-if="problemType==='single' || problemType==='multiple'" class="legacy-editor-container">
      <div class="legacy-editor-header">
        <span class="legacy-editor-title">选项</span>
        <button @click="addOption" class="legacy-editor-button">添加选项</button>
      </div>

      <div v-for="opt in options" :key="opt.id" class="legacy-editor-option-item">
        <input v-if="problemType==='single'" type="radio" :value="opt.id" v-model="answers" />
        <input v-if="problemType==='multiple'" type="checkbox" :value="opt.id" v-model="answers" />
        <input v-model="opt.content" placeholder="选项内容" class="legacy-editor-option-input" />
        <button @click="removeOption(opt.id)" class="legacy-editor-delete-button">删除</button>
      </div>
    </div>

    <!-- 填空 -->
    <div v-if="problemType==='fill'" class="legacy-editor-container">
      <div class="legacy-editor-header">
        <span class="legacy-editor-title">填空答案</span>
        <button @click="addAnswer" class="legacy-editor-button">添加答案</button>
      </div>

      <div v-for="(ans, idx) in answers" :key="idx" class="legacy-editor-answer-item">
        <input v-model="answers[idx]" placeholder="答案" class="legacy-editor-answer-input" />
        <button @click="removeAnswer(idx)" class="legacy-editor-delete-button">删除</button>
      </div>
    </div>
  </div>
</template>
