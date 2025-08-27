<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import axios from "axios";

const router = useRouter();
const title = ref("");
const description = ref("");
const maxTime = ref(1); // 默认 1 秒
const maxMemory = ref(256); // 默认 256 MB
const submitting = ref(false); // 提交状态

// 固定课程为当前课程
const userStore = useUserStore();
const courseName = computed(() => {
  const course = userStore.courses.find(c => c.id === userStore.currentCourseId);
  return course ? course.name : '';
});

const submit = async () => {
  if (submitting.value) return;
  submitting.value = true;
  try {
    // 只传 JSON，不用 FormData
    const res = await axios.post("/api/problems/", {
      title: title.value,
      description: description.value,
      limitations: { maxTime: maxTime.value, maxMemory: maxMemory.value },
      course_id: userStore.currentCourseId,
      test_cases: [], // 初始空，之后去 edit 页面再上传
    });

    const problemId = res.data.id;
    const goEdit = confirm("题目创建成功！是否继续上传测试数据？");
    if (goEdit) {
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
</script>

<template>
  <div class="add-coding-problem-container">
    <!-- 标题 -->
    <input v-model="title" placeholder="标题"
      class="add-coding-problem-input" />

    <!-- 描述 -->
    <textarea v-model="description" rows="6" placeholder="题目描述"
      class="add-coding-problem-textarea"></textarea>

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
