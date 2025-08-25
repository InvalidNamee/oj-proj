<script setup>
import { RouterView } from 'vue-router';
import Sidebar from '@/components/Sidebar.vue';
import { ref } from 'vue';
import { useUserStore } from '@/stores/user.js';

const userStore = useUserStore();
const views = ref([
  { name: '用户列表', path: '/users' },
  { name: '注册', path: '/users/register' },
  { name: '导入', path: '/users/import' }
])
</script>

<template>
  <div class="flex">
    <Sidebar v-if="userStore.usertype !== 'student'" :views="views" />
    <main class="flex-1 p-6">
      <RouterView />
    </main>
  </div>
  <!-- <RouterView /> -->
</template>