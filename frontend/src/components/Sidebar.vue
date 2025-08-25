<script setup>
import { ref, computed } from 'vue';
import { useRoute, RouterLink } from 'vue-router';

const props = defineProps({
  views: {
    type: Array,
    default: () => []
  }
});

const route = useRoute();
const activePath = computed(() => route.path);
</script>

<template>
  <aside
    class="fixed left-0 top-16 w-60 h-[calc(100vh-4rem)] bg-white shadow p-4 z-10"
  >
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