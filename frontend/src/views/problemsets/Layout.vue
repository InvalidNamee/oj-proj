<script setup>
import { RouterView } from 'vue-router';
import Sidebar from '@/components/Sidebar.vue';
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
import '@/assets/problemsets.css';

const userStore = useUserStore();
const views = ref([
    { name: '题单列表', path: '/problemsets'},
    { name: '题目列表', path: '/problems' },
    { name: '新建题单', path: '/problemsets/add'},
    { name: '新建题目', path: '/problems/add' },
])
</script>

<template>
  <div class="problemset-layout">
    <!-- 固定 Sidebar -->
    <Sidebar
      v-if="userStore.usertype !== 'student'"
      :views="views"
      class="sidebar-container"
    />

    <main
      class="problemset-main"
      :class="userStore.usertype !== 'student' ? 'problemset-main-with-sidebar' : ''"
    >
      <RouterView />
    </main>
  </div>
</template>
