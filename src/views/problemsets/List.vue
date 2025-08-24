<script setup>
import { ref, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user.js";
import axios from "axios";

const userStore = useUserStore();
const router = useRouter();
const problemsets = ref([]);
const page = ref(1);
const perPage = ref(20);

const fetchProblemSets = async () => {
  const res = await axios.get("/api/problemsets/", {
    params: { page: page.value, per_page: perPage.value, course_id: userStore.currentCourseId },
  });
  problemsets.value = res.data.problemsets;
};

onMounted(fetchProblemSets);

watch(() => userStore.currentCourseId, fetchProblemSets);

const goDetail = (id) => router.push(`/problemsets/${id}`);
const goEdit = (id) => router.push(`/problemsets/${id}/edit`);
</script>

<template>
  <div class="max-w-4xl mx-auto mt-8 p-6 rounded-xl bg-white shadow">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold">题单列表</h2>
      <button @click="router.push('/problemsets/add')" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">新建题单</button>
    </div>

    <div class="space-y-2">
      <div v-for="ps in problemsets" :key="ps.id" class="p-4 border border-gray-300 rounded flex justify-between items-center hover:shadow">
        <div @click="goDetail(ps.id)" class="cursor-pointer">
          <h3 class="font-semibold text-lg">{{ ps.title }}</h3>
          <p class="text-sm text-gray-500">{{ ps.description }}</p>
          <p class="text-xs text-gray-400">课程: {{ ps.course?.title || '无' }} | 题目数: {{ ps.num_legacy_problems }} + {{ ps.num_coding_problems }}</p>
        </div>
        <div class="space-x-2">
          <button @click="goEdit(ps.id)" class="text-blue-500 hover:underline">编辑</button>
        </div>
      </div>
    </div>
  </div>
</template>
