<script setup>
import { RouterView } from 'vue-router';
import Sidebar from '@/components/Sidebar.vue';
import { ref } from 'vue';

const views = ref([
  { name: '课程列表', path: '/courses' },
  { name: '新增课程', path: '/courses/add' }
])
</script>

<template>
  <div class="flex">
    <Sidebar :views="views" />
    <main class="flex-1 p-6">
      <RouterView />
    </main>
  </div>
  <!-- <RouterView /> -->
</template>