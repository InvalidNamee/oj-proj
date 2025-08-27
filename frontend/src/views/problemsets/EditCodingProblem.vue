<script setup>
import { ref, watch, computed } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import { useUserStore } from "@/stores/user";
import "@/assets/problemsets.css";

const props = defineProps({
  problemId: { type: [String, Number], required: true },
  problemData: { type: Object, required: true }
});

const userStore = useUserStore();
const router = useRouter();

const title = ref(props.problemData.title || "");
const description = ref(props.problemData.description || "");
const maxTime = ref(props.problemData.limitations?.maxTime || 1);
const maxMemory = ref(props.problemData.limitations?.maxMemory || 256);
const courseId = ref(props.problemData.course_id || "");

// 课程列表
const courses = computed(() => userStore.courses);

// 监听 problemData 更新
watch(() => props.problemData, (data) => {
  title.value = data.title || "";
  description.value = data.description || "";
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
    <input v-model="title" placeholder="标题"
      class="edit-coding-problem-input" />
    <textarea v-model="description" rows="6" placeholder="题目描述"
      class="edit-coding-problem-textarea"></textarea>

    <div class="edit-coding-problem-grid">
      <input v-model="maxTime" type="number" placeholder="时间限制 (s)"
        class="edit-coding-problem-input" />
      <input v-model="maxMemory" type="number" placeholder="内存限制 (MB)"
        class="edit-coding-problem-input" />
    </div>

    <!-- 课程选择 -->
    <select v-model="courseId" class="edit-coding-problem-select">
      <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.name }}</option>
    </select>

    <button @click="submit" :disabled="submitting"
      class="edit-coding-problem-button">
      {{ submitting ? "提交中…" : "提交修改" }}
    </button>
  </div>
</template>
