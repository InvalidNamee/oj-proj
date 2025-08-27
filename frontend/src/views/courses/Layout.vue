<script setup>
import { RouterView } from 'vue-router';
import Sidebar from '@/components/Sidebar.vue';
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
import { useRouter } from 'vue-router';
import '@/assets/courses.css';

const userStore = useUserStore();
const views = ref([
  { name: '课程列表', path: '/courses' },
  { name: '新增课程', path: '/courses/add' }
])
</script>

<template>
  <div class="course-layout">
    <!-- 固定 Sidebar -->
    <Sidebar
      v-if="userStore.usertype === 'admin'"
      :views="views"
      class="sidebar-container"
    />

    <main
      class="course-main"
      :class="userStore.usertype === 'admin' ? 'course-main-with-sidebar' : ''"
    >
      <RouterView />
    </main>
  </div>
</template>