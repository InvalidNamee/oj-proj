<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useUserStore } from '@/stores/user';
import { RouterLink, useRouter, useRoute } from 'vue-router';

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
  <nav class="bg-white shadow-sm p-4 flex justify-between items-center">
    <div class="flex items-center space-x-4">
      <div class="text-lg font-bold text-gray-800">DawOj v2</div>

      <!-- 课程选择 -->
      <template v-if="userStore.uid && userStore.courses.length">
        <select
          v-model="currentCourseId"
          class="border border-gray-300 rounded px-2 py-1 text-gray-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 outline-none transition-all"
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
    <div class="flex space-x-4">
      <RouterLink
        v-for="view in filteredViews"
        :key="view.name"
        :to="view.path"
        class="px-3 py-1 rounded text-gray-800 hover:text-blue-600 hover:bg-blue-50 transition-colors"
        :class="activePath === view.path ? 'bg-blue-50 text-blue-600 font-semibold' : ''"
      >
        {{ view.name }}
      </RouterLink>
    </div>

    <!-- 用户区域 -->
    <div class="relative flex items-center space-x-4" id="user-dropdown">
      <template v-if="userStore.uid">
        <button @click.stop="toggleDropdown"
          class="flex items-center space-x-2 text-gray-800 hover:text-blue-600 focus:outline-none relative z-10">
          <span>{{ userStore.username }}</span>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </button>

        <div
          v-show="dropdownOpen"
          class="absolute right-0 top-full mt-2 w-48 bg-white rounded-lg shadow-sm z-50 border border-gray-100"
          style="min-width: 160px;"
        >
          <div class="px-4 py-2 text-gray-700 border-b border-gray-100">
            {{ userStore.username }} ({{ userStore.usertype }})
          </div>
          <RouterLink :to="`/users/${userStore.id}`" class="block px-4 py-2 text-gray-700 hover:bg-gray-50"
            @click="closeDropdown">
            Profile
          </RouterLink>
          <button @click="logout" class="w-full text-left px-4 py-2 text-red-500 hover:bg-gray-50">
            Logout
          </button>
        </div>
      </template>

      <template v-else>
        <RouterLink to="/login" class="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600">
          Login
        </RouterLink>
      </template>
    </div>
  </nav>
</template>
