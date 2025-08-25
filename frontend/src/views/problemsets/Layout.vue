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
  <div class="flex">
    <Sidebar v-if="userStore.usertype !== 'student'" :views="views"/>
    <main class="flex-1 p-6">
      <RouterView />
    </main>
  </div>
  <!-- <RouterView /> -->
</template>