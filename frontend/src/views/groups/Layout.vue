<script setup>
import { RouterView } from 'vue-router';
import Sidebar from '@/components/Sidebar.vue';
import { ref } from 'vue';
import { useUserStore } from '@/stores/user.js';
import '@/assets/groups.css';

const userStore = useUserStore();
const views = ref([
  { name: '分组列表', path: '/groups'},
  { name: '创建分组', path: '/groups/add' }
])
</script>

<template>
  
  <div class="group-layout">
    <!-- 固定 Sidebar -->
    <Sidebar
      v-if="userStore.usertype !== 'student'"
      :views="views"
      class="sidebar-container"
    />

    <main
      class="group-main"
      :class="userStore.usertype !== 'student' ? 'group-main-with-sidebar' : ''"
    >
      <RouterView />
    </main>
  </div>
</template>