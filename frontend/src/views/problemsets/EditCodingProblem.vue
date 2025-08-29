<script setup>
import { ref, watch, computed } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import { useUserStore } from "@/stores/user";
import EditableTestCases from "@/components/EditableTestCases.vue";
import "@/assets/problemsets.css";
import "@/assets/pr5.css";

const props = defineProps({
  problemId: { type: [String, Number], required: true },
  problemData: { type: Object, required: true }
});

const userStore = useUserStore();
const router = useRouter();
const cases = ref(props.problemData.description.samples || [])
const title = ref(props.problemData.title || "");
const description = ref({
  notes: "",
  description: "",
  input_format: "",
  output_format: "",
  samples: []
});

// 如果后端已经是 JSON，初始化
if (props.problemData.description) {
  description.value = { ...props.problemData.description };
}

const maxTime = ref(props.problemData.limitations?.maxTime || 1);
const maxMemory = ref(props.problemData.limitations?.maxMemory || 256);
const courseId = ref(props.problemData.course_id || "");

// 课程列表
const courses = computed(() => userStore.courses);

// 监听 problemData 更新
watch(() => props.problemData, (data) => {
  title.value = data.title || "";
  description.value = data.description
    ? { ...data.description }
    : { notes: "", description: "", input_format: "", output_format: "", samples: [] };
  maxTime.value = data.limitations?.maxTime || 1;
  maxMemory.value = data.limitations?.maxMemory || 256;
  courseId.value = data.course_id || "";
});

const submitting = ref(false);

const submit = async () => {
  if (submitting.value) return;
  submitting.value = true;
  try {
    await axios.put(`/api/problems/${props.problemId}`, {
      title: title.value,
      description: description.value,
      limitations: { maxTime: maxTime.value, maxMemory: maxMemory.value },
      course_id: courseId.value,
    });
    alert("题目修改成功");
    router.push("/problems");
  } catch (err) {
    alert(err.response?.data?.error || "提交失败");
  } finally {
    submitting.value = false;
  }
};
</script>

<template>
  <div class="edit-coding-problem-container">
    <!-- 标题 -->
    <div class="add-coding-problem-form-group">
      <label class="add-coding-problem-form-group-label">标题</label>
      <input v-model="title" placeholder="请输入题目标题" class="add-coding-problem-input" />
    </div>

    <div class="add-coding-problem-form-group">
      <label class="add-coding-problem-form-group-label">题目描述</label>
      <textarea v-model="description.description" rows="6" placeholder="请输入题目描述" class="add-coding-problem-textarea" />
    </div>

    <div class="add-coding-problem-grid">
      <div class="add-coding-problem-form-group">
        <label class="add-coding-problem-form-group-label">输入格式</label>
        <textarea v-model="description.input_format" placeholder="请输入输入格式" class="add-coding-problem-textarea format-input"
          rows="4" />
      </div>

      <div class="add-coding-problem-form-group">
        <label class="add-coding-problem-form-group-label">输出格式</label>
        <textarea v-model="description.output_format" placeholder="请输入输出格式" class="add-coding-problem-textarea format-input"
          rows="4" />
      </div>
    </div>

    <div class="add-coding-problem-form-group">
      <label class="add-coding-problem-form-group-label">数据范围与提示</label>
      <textarea v-model="description.notes" rows="3" placeholder="请输入数据范围与提示" class="add-coding-problem-textarea" />
    </div>

    <!-- 样例 -->
    <EditableTestCases v-model="description.samples" title="样例" />

    <!-- 限制 -->
    <div class="add-coding-problem-grid">
      <div class="add-coding-problem-form-group">
        <label class="add-coding-problem-form-group-label">时间限制 (s)</label>
        <input v-model="maxTime" type="number" placeholder="请输入时间限制" class="add-coding-problem-input" />
      </div>

      <div class="add-coding-problem-form-group">
        <label class="add-coding-problem-form-group-label">空间限制 (MB)</label>
        <input v-model="maxMemory" type="number" placeholder="请输入空间限制" class="add-coding-problem-input" />
      </div>
    </div>

    <!-- 课程选择 -->
    <select v-model="courseId" class="edit-coding-problem-select">
      <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.name }}</option>
    </select>

    <!-- 提交按钮 -->
    <button @click="submit" :disabled="submitting" class="edit-coding-problem-button">
      {{ submitting ? "提交中…" : "提交修改" }}
    </button>
  </div>
</template>
