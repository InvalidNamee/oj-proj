<script setup>
import { RouterLink } from 'vue-router';
import { reactive } from 'vue';
import LoginButton from './LoginButton.vue';
const views = reactive([
  { name: 'Home', path: '/' },
  { name: 'Auth', path: '/auth-test'},
  { name: 'User', path: '/user-test'},
  { name: 'Course', path: '/course-test'},
  { name: 'Problemset', path: '/problemset-test'},
  { name: 'Test', path: '/test' },
  { name: 'Coding', path: '/coding-test'},
  { name: 'Legacy', path: '/legacy-test'}
]);
</script>

<template>
  <div>
    <LoginButton />
    <nav>
      <ul>
        <li
          v-for="view in views" :key="view.path">
          <RouterLink :to="view.path">
            <p>{{ view.name }}</p>
          </RouterLink>
        </li>
      </ul>
    </nav>
  </div>
</template>


<style scoped>
  ul {
    display: flex;
  }

  li {
    padding: 2rem;
  }
</style>