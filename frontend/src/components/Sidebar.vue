<script setup>
import { ref, computed } from 'vue';
import { useRoute, RouterLink } from 'vue-router';
import '@/assets/components.css';

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
    class="sidebar-container"
  >
    <nav class="sidebar-nav">
      <RouterLink
        v-for="view in views"
        :key="view.path"
        :to="view.path"
        class="sidebar-link"
        :class="activePath === view.path ? 'active' : 'inactive'"
      >
        {{ view.name }}
      </RouterLink>
    </nav>
  </aside>
</template>