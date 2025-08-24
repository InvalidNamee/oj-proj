<script setup>
import { ref, computed } from 'vue';
import { useRoute, RouterLink } from 'vue-router';
// import PropTypes from 'vue-types';

const props = defineProps({
  views: {
    type: Array,
    default: () => []
  }
});

const route = useRoute();

// 当前激活的路由路径
const activePath = computed(() => route.path);
</script>

<template>
  <aside class="w-60 h-screen bg-white shadow p-4">
    <nav class="flex flex-col space-y-2">
      <RouterLink
        v-for="view in views"
        :key="view.path"
        :to="view.path"
        class="px-4 py-2 rounded hover:bg-blue-100 transition-colors"
        :class="activePath === view.path ? 'bg-blue-200 font-semibold text-blue-700' : 'text-gray-800'"
      >
        {{ view.name }}
      </RouterLink>
    </nav>
  </aside>
</template>

<style scoped>
/* 简单过渡效果，保持极简风格 */
</style>
