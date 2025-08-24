<script setup>
import { ref, onMounted, watch } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";

const groups = ref([]);
const router = useRouter();
const userStore = useUserStore();

const fetchGroups = async () => {
  const res = await axios.get("/api/groups", {
    params: { course_id: userStore.currentCourseId }
  });
  groups.value = res.data.groups || [];
};

const goDetail = (id) => {
  router.push(`/groups/${id}`);
};

const goEdit = (id) => {
  router.push(`/groups/${id}/edit`);
};

watch(
  () => userStore.currentCourseId,
  () => {
    fetchGroups();
  }
);

onMounted(fetchGroups);
</script>

<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-bold">分组列表</h2>
    </div>

    <div class="bg-white shadow rounded-lg overflow-hidden">
      <table class="w-full text-left text-sm">
        <thead class="bg-gray-50 text-gray-700">
          <tr>
            <th class="p-3">ID</th>
            <th class="p-3">组名</th>
            <th class="p-3">所属课程</th>
            <th class="p-3">学生数</th>
            <th class="p-3">题单数</th>
            <th class="p-3">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="g in groups"
            :key="g.id"
            class="hover:bg-gray-50 transition cursor-pointer"
          >
            <td class="p-3">{{ g.id }}</td>
            <td class="p-3 text-blue-600 hover:underline" @click="goDetail(g.id)">
              {{ g.name }}
            </td>
            <td class="p-3">{{ g.course.name }}</td>
            <td class="p-3">{{ g.student_cnt }}</td>
            <td class="p-3">{{ g.problemset_cnt }}</td>
            <td class="p-3 space-x-3">
              <button
                class="text-blue-500 hover:underline"
                @click.stop="goEdit(g.id)"
              >
                编辑
              </button>
            </td>
          </tr>
          <tr v-if="groups.length === 0">
            <td colspan="5" class="p-3 text-center text-gray-400">
              暂无分组
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
