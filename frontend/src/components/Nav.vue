<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';
import { RouterLink, useRouter, useRoute } from 'vue-router';
import '@/assets/components.css';

const userStore = useUserStore();
const route = useRoute();
const router = useRouter();

const activePath = computed(() => route.path);

// 定义视图 + 权限要求
const views = ref([
  { name: '主页', path: '/', permission: 2 },
  { name: '课程', path: '/courses', permission: 2 },
  { name: '用户', path: '/users', permission: 1 },
  { name: '题单', path: '/problemsets', permission: 2 },
  { name: '分组', path: '/groups', permission: 1 },
  { name: '提交记录', path: '/submissions', permission: 2 },
]);

// 权限映射
const rolePermission = {
  student: 2, // 学生能看 permission <= 2
  teacher: 1, // 教师能看 permission <= 1
  admin: 0,   // 管理员能看所有
};

// 根据用户角色过滤视图
const filteredViews = computed(() => {
  const role = userStore.usertype || 'student'; // 默认当学生
  const level = rolePermission[role] ?? 2;
  return views.value.filter(view => view.permission >= level);
});

const dropdownOpen = ref(false);
const toggleDropdown = () => (dropdownOpen.value = !dropdownOpen.value);
const closeDropdown = () => (dropdownOpen.value = false);

// 当前选中的课程
const currentCourseId = ref(userStore.currentCourseId || null);

onMounted(() => {
  if (!currentCourseId.value && userStore.courses.length) {
    currentCourseId.value = userStore.courses[0].id;
    userStore.setCurrentCourse(currentCourseId.value);
  }
});

watch(currentCourseId, (val) => {
  userStore.setCurrentCourse(val);
});

const handleClickOutside = (event) => {
  const dropdown = document.getElementById('user-dropdown');
  if (dropdown && !dropdown.contains(event.target)) closeDropdown();
};
document.addEventListener('click', handleClickOutside);

const logout = async () => {
  await userStore.logout();
  closeDropdown();
  router.push('/login');
};
</script>

<template>
  <nav class="nav-container">
    <div class="nav-left">
      <div class="nav-logo">DawOj v2</div>

      <!-- 课程选择 -->
      <template v-if="userStore.uid && userStore.courses.length">
        <select
          v-model="currentCourseId"
          class="nav-course-select"
          style="margin-left: 8px; min-width: 120px;"
        >
          <option v-if="userStore.usertype === 'admin'" :value="null">
            全部课程
          </option>
          <option v-for="course in userStore.courses" :key="course.id" :value="course.id">
            {{ course.name }}
          </option>
        </select>
      </template>
    </div>

    <!-- 导航栏菜单 -->
    <div class="nav-menu">
      <RouterLink
        v-for="view in filteredViews"
        :key="view.name"
        :to="view.path"
        class="nav-link"
        :class="activePath === view.path ? 'active' : ''"
      >
        {{ view.name }}
      </RouterLink>
    </div>

    <!-- 用户区域 -->
    <div class="nav-user" id="user-dropdown">
      <template v-if="userStore.uid">
        <button @click.stop="toggleDropdown" class="nav-user-button">
          <span>{{ userStore.username }}</span>
          <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </button>

        <div
          v-show="dropdownOpen"
          class="nav-dropdown"
          style="min-width: 160px;"
        >
          <div class="nav-dropdown-header">
            {{ userStore.username }} ({{ userStore.usertype }})
          </div>
          <RouterLink :to="`/users/${userStore.id}`" class="nav-dropdown-link"
            @click="closeDropdown">
            Profile
          </RouterLink>
          <button @click="logout" class="nav-dropdown-button">
            Logout
          </button>
        </div>
      </template>

      <template v-else>
        <RouterLink to="/login" class="nav-login-link">
          Login
        </RouterLink>
      </template>
    </div>
  </nav>
</template>
