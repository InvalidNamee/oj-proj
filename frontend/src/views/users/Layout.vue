<script setup>
import { RouterView } from 'vue-router';
import Sidebar from '@/components/Sidebar.vue';
import { ref } from 'vue';
import { useUserStore } from '@/stores/user.js';
import '@/assets/users.css';

const userStore = useUserStore();
const views = ref([
  { name: '用户列表', path: '/users' },
  { name: '注册', path: '/users/register' },
  { name: '导入', path: '/users/import' }
])
</script>

<template>
  <div class="user-layout">
    <!-- 固定 Sidebar -->
    <Sidebar
      v-if="userStore.usertype !== 'student'"
      :views="views"
      class="sidebar-container"
    />

    <main
      class="user-main"
      :class="userStore.usertype !== 'student' ? 'user-main-with-sidebar' : ''"
    >
      <RouterView />
    </main>
  </div>
</template>