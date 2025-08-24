<script setup>
import { ref, computed, watch } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";

const groupName = ref("");
const description = ref("");
const router = useRouter();
const userStore = useUserStore();

const courseName = computed(() => {
  const course = userStore.courses.find(c => c.id === userStore.currentCourseId);
  return course ? course.name : '';
});

const createGroup = async () => {
  if (!groupName.value) {
    alert("请填写分组名称");
    return;
  }

  await axios.post("/api/groups", {
    course_id: userStore.currentCourseId,
    name: groupName.value,
    description: description.value
  });
  router.push("/groups");
};
</script>

<template>
  <div class="p-6 max-w-lg mx-auto">
    <h2 class="text-xl font-bold mb-4">创建分组</h2>

    <!-- 当前课程显示 -->
    <div class="mb-3">
      <label class="block mb-1">课程</label>
      <input type="text" :value="courseName" disabled class="border border-gray-300 px-2 py-1 w-full bg-gray-100 cursor-not-allowed" />
    </div>

    <div class="mb-3">
      <label class="block mb-1">分组名称</label>
      <input v-model="groupName" type="text" class="border border-gray-300 px-2 py-1 w-full" placeholder="请输入分组名称" />
    </div>

    <div class="mb-3">
      <label class="block mb-1">描述</label>
      <textarea v-model="description" class="border border-gray-300 px-2 py-1 w-full" placeholder="请输入分组描述"></textarea>
    </div>

    <button @click="createGroup" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition">
      创建
    </button>
  </div>
</template>
