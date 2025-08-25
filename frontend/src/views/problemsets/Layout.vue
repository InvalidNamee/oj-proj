<script setup>
import { RouterView } from 'vue-router';
import Sidebar from '@/components/Sidebar.vue';
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();
const views = ref([
    { name: '题单列表', path: '/problemsets'},
    { name: '题目列表', path: '/problems' },
    { name: '创建题单', path: '/problemsets/add'},
    { name: '新建题目', path: '/problems/add' },
])
</script>

<template>
  <div class="flex flex-1 relative">
    <!-- 固定 Sidebar -->
    <Sidebar
      v-if="userStore.usertype !== 'student'"
      :views="views"
      class="fixed left-0 top-0 h-full w-60"
    />

    <main
      class="flex-1 p-6 overflow-auto"
      :class="userStore.usertype !== 'student' ? 'ml-60' : ''"
    >
      <RouterView />
    </main>
  </div>
</template>
