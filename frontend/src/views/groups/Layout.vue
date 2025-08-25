<script setup>
import { RouterView } from 'vue-router';
import Sidebar from '@/components/Sidebar.vue';
import { ref } from 'vue';
import { useUserStore } from '@/stores/user.js';

const userStore = useUserStore();
const views = ref([
  { name: '分组列表', path: '/groups'},
  { name: '创建分组', path: '/groups/add' }
])
</script>

<template>
  <div class="flex">
    <Sidebar v-if="userStore.usertype !== 'student'" :views="views" />
    <main class="flex-1 p-6">
      <RouterView />
    </main>
  </div>
</template>