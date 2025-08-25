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