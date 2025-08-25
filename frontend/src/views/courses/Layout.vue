<script setup>
import { RouterView } from 'vue-router';
import Sidebar from '@/components/Sidebar.vue';
import { ref } from 'vue';
import { useUserStore } from '@/stores/user';
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const views = ref([
  { name: '课程列表', path: '/courses' },
  { name: '新增课程', path: '/courses/add' }
])
</script>

<template>
  <div class="flex">
    <Sidebar v-if="userStore.usertype === 'admin'" :views="views" />
    <main class="flex-1 p-6">
      <RouterView />
    </main>
  </div>
</template>