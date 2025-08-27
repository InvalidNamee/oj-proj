<script setup>
import { RouterView } from 'vue-router';
import Nav from '@/components/Nav.vue';
</script>

<template>
  <Nav />
  <div class="page-content">
    <RouterView />
  </div>
</template>