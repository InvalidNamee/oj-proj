<script setup>
import { ref } from 'vue'

const content = ref("# jfdsalk")
// import MarkdownArea from '@/components/MarkdownArea.vue';
</script>
<template>
  <div class="prose">
    {{ content }}
  </div>
</template>
