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
  <div class="space-y-4">
    <!-- 标题 -->
    <input v-model="title" placeholder="标题"
      class="w-full border border-gray-300 rounded px-2 py-2 text-gray-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none" />

    <!-- 描述 -->
    <textarea v-model="description" rows="6" placeholder="题目描述"
      class="w-full border border-gray-300 rounded px-2 py-2 text-gray-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none"></textarea>

    <!-- 限制条件 -->
    <div class="grid grid-cols-2 gap-4">
      <input v-model.number="maxTime" type="number" placeholder="时间限制 (s)"
        class="w-full border border-gray-300 rounded px-2 py-2 text-gray-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none" />
      <input v-model.number="maxMemory" type="number" placeholder="内存限制 (MB)"
        class="w-full border border-gray-300 rounded px-2 py-2 text-gray-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none" />
    </div>
     <!-- 所属课程（固定） -->
    <input type="text" :value="courseName" disabled
      class="w-full border border-gray-300 rounded px-2 py-2 text-gray-700 bg-gray-100 cursor-not-allowed" />

    <!-- 提交按钮 -->
    <button @click="submit" :disabled="submitting" class="w-full px-3 py-2 rounded text-white"
      :class="submitting ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600'">
      {{ submitting ? '提交中…' : '提交' }}
    </button>
  </div>
</template>
