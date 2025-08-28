<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

const stats = ref({
  registeredUsers: 0,
  courses: 0,
  announcements: [
    {
      id: 1,
      title: '系统维护通知',
      content: '系统将于本周六晚上10点进行维护，预计持续2小时。',
      date: '2025-08-26'
    },
    {
      id: 2,
      title: '新功能上线',
      content: '我们新增了AI题目生成功能，欢迎体验！',
      date: '2025-08-23'
    },
    {
      id: 3,
      title: '*****',
      content: '***，*******。',
      date: '2025-08-20'
    }
  ]
});

// 获取真实数据
const fetchStats = async () => {
  try {
    // 获取用户总数
    const userRes = await axios.get('/api/users', { params: { per_page: 1 } });
    stats.value.registeredUsers = userRes.data.total;
    
    // 获取课程总数
    const courseRes = await axios.get('/api/courses', { params: { per_page: 1 } });
    stats.value.courses = courseRes.data.total;
  } catch (err) {
    console.error('获取统计数据失败', err);
  }
};

const quickLinks = ref([
  { name: '我的课程', path: '/courses' },
  { name: '题库练习', path: '/problemsets' },
  { name: '提交记录', path: '/submissions' },
  { name: '个人中心', path: `/users/${userStore.id}` }
]);

onMounted(() => {
  fetchStats();
  console.log('主页组件已加载');
});
</script>

<template>
  <div class="home-container">
    <!-- 欢迎语 -->
    <div class="welcome-section">
      <h1 class="welcome-title">欢迎来到在线判题系统</h1>
      <p class="welcome-subtitle">在这里你可以练习编程、参加竞赛、提升技能</p>
    </div>
    
    <!-- 统计数据卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">{{ stats.registeredUsers }}</div>
        <div class="stat-label">注册用户</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.courses }}</div>
        <div class="stat-label">课程数量</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.announcements.length }}</div>
        <div class="stat-label">最新公告</div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 公告栏 -->
      <div class="announcements-section">
        <h2 class="section-title">公告栏</h2>
        <div class="announcement-list">
          <div 
            v-for="announcement in stats.announcements" 
            :key="announcement.id" 
            class="announcement-item"
          >
            <h3 class="announcement-title">{{ announcement.title }}</h3>
            <p class="announcement-content">{{ announcement.content }}</p>
            <div class="announcement-date">{{ announcement.date }}</div>
          </div>
        </div>
      </div>

      <!-- 快速链接 -->
      <div class="quick-links-section">
        <h2 class="section-title">快速开始</h2>
        <div class="links-grid">
          <router-link 
            v-for="link in quickLinks" 
            :key="link.name" 
            :to="link.path"
            class="link-card"
          >
            {{ link.name }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 欢迎语区域 */
.welcome-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 30px;
  text-align: center;
  margin-bottom: 30px;
}

.welcome-title {
  font-size: 2rem;
  font-weight: bold;
  color: #1f2937; /* gray-800 */
  margin-bottom: 10px;
}

.welcome-subtitle {
  font-size: 1.1rem;
  color: #6b7280; /* gray-500 */
}

/* 统计数据卡片布局 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #3b82f6; /* blue-500 */
  margin-bottom: 5px;
}

.stat-label {
  font-size: 1rem;
  color: #6b7280; /* gray-500 */
}

/* 主要内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
}

/* 公告栏样式 */
.announcements-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.section-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 20px;
  color: #1f2937; /* gray-800 */
  border-bottom: 2px solid #3b82f6; /* blue-500 */
  padding-bottom: 10px;
}

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.announcement-item {
  padding: 15px;
  border-radius: 6px;
  background-color: #f9fafb; /* gray-50 */
  border: 1px solid #e5e7eb; /* gray-200 */
  transition: background-color 0.3s ease;
}

.announcement-item:hover {
  background-color: #f3f4f6; /* gray-100 */
}

.announcement-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: #1f2937; /* gray-800 */
}

.announcement-content {
  color: #4b5563; /* gray-600 */
  margin-bottom: 10px;
  line-height: 1.5;
}

.announcement-date {
  font-size: 0.875rem;
  color: #9ca3af; /* gray-400 */
  text-align: right;
}

/* 快速链接样式 */
.quick-links-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.links-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 15px;
}

.link-card {
  display: block;
  padding: 15px;
  border-radius: 6px;
  background-color: #eff6ff; /* blue-50 */
  color: #3b82f6; /* blue-500 */
  text-decoration: none;
  font-weight: 500;
  text-align: center;
  transition: background-color 0.3s ease, transform 0.3s ease;
  border: 1px solid #dbeafe; /* blue-100 */
}

.link-card:hover {
  background-color: #dbeafe; /* blue-100 */
  transform: translateY(-2px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
