<script setup>
import { ref, watch, computed } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import LegacyEditor from "@/components/LegacyEditor.vue";
import { useUserStore } from "@/stores/user";
import "@/assets/pr5.css";

const props = defineProps({
  problemId: { type: [String, Number], required: true },
  problemData: { type: Object, required: true }
});

const userStore = useUserStore();
const router = useRouter();

const title = ref(props.problemData.title || "");
const description = ref(props.problemData.description || "");
const courseId = ref(props.problemData.course_id || "");
const problemType = ref(props.problemData.type || "single");
const testCases = ref(props.problemData.test_cases || {});

// 从 userStore 获取课程列表
const courses = computed(() => userStore.courses);

// 监听 problemData 更新
watch(() => props.problemData, (data) => {
  title.value = data.title || "";
  description.value = data.description || "";
  courseId.value = data.course_id || "";
  problemType.value = data.type || "single";
  testCases.value = data.test_cases || {};
});

const submitting = ref(false);

const submit = async () => {
  if (submitting.value) return;
  submitting.value = true;
  try {
    await axios.put(`/api/problems/${props.problemId}/legacy`, {
      title: title.value,
      description: description.value,
      test_cases: testCases.value,
      course_id: courseId.value
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
  <div class="edit-problem-container">
    <div class="edit-legacy-problem-space-y-4">
      <input v-model="title" placeholder="标题" class="edit-legacy-problem-input" />
      <textarea v-model="description" rows="6" placeholder="题目描述" class="edit-legacy-problem-textarea"></textarea>
      
      <LegacyEditor
        :problemType="problemType"
        :initialTestCases="testCases"
        @update:testCases="val => testCases.value = val"
      />

      <!-- 课程选择 -->
      <select v-model="courseId" class="edit-legacy-problem-select">
        <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>

      <button
        @click="submit"
        :disabled="submitting"
        class="edit-legacy-problem-button"
      >
        {{ submitting ? "提交中…" : "提交修改" }}
      </button>
    </div>
  </div>
</template>
