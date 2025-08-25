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
  <div class="flex flex-1 relative">
    <!-- 固定 Sidebar -->
    <Sidebar
      v-if="userStore.usertype === 'admin'"
      :views="views"
      class="fixed left-0 top-0 h-full w-60"
    />

    <main
      class="flex-1 p-6 overflow-auto"
      :class="userStore.usertype === 'admin' ? 'ml-60' : ''"
    >
      <RouterView />
    </main>
  </div>
</template>