<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import Nav from '@/components/Nav.vue';
import axios from 'axios';

const userStore = useUserStore();
const router = useRouter();
const problemsets = ref([]);

const fetchProblemSets = async () => {
  try {
    const res = await axios.get("/api/problemsets/", {
      params: {
        course_id: userStore.currentCourseId,
      },
    });
    problemsets.value = res.data.problemsets;
  } catch (err) {
    console.error(err);
  }
};

// 格式化时间显示
const formatTime = (time) => {
  if (!time) return '无';
  return new Date(time).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

const goToProblemSet = (id) => {
  // 检查用户是否是学生
  if (userStore.usertype === 'student') {
    // 找到对应的题单
    const problemset = problemsets.value.find(ps => ps.id === id);
    if (problemset) {
      const now = new Date();
      const startTime = new Date(problemset.start_time);
      const endTime = new Date(problemset.end_time);
      
      // 如果题单未开始或已结束，则禁止学生点击
      if ((problemset.start_time && now < startTime) || (problemset.end_time && now > endTime)) {
        alert('该题单当前不可访问');
        return;
      }
    }
  }
  router.push(`/problemsets/${id}`);
};

onMounted(fetchProblemSets);
watch(() => userStore.currentCourseId, fetchProblemSets);
</script>

<template>
  <div class="home-container">
    <Nav />
    <div class="content-wrapper">
      <div class="welcome-section">
        <h1 class="welcome-title">欢迎, {{ userStore.username }}!</h1>
        <p class="welcome-subtitle">您已成功登录系统。</p>
      </div>
      
      <!-- 作业列表 -->
      <div class="problemset-section">
        <h2 class="problemset-title">当前课程作业列表</h2>
        <div v-if="problemsets.length === 0" class="no-problemsets">
          暂无作业
        </div>
        <div v-else class="problemset-list">
          <div v-for="ps in problemsets" :key="ps.id" class="problemset-item">
            <h3 class="problemset-item-title clickable" @click="goToProblemSet(ps.id)" :class="{ 'disabled': userStore.usertype === 'student' && ((ps.start_time && new Date() < new Date(ps.start_time)) || (ps.end_time && new Date() > new Date(ps.end_time))) }">{{ ps.title }}</h3>
            <p class="problemset-item-description">{{ ps.description }}</p>
            <div class="problemset-item-meta">
              <span>题目数: {{ ps.num_problems }}</span>
              <span>开始时间: {{ formatTime(ps.start_time) }}</span>
              <span>结束时间: {{ formatTime(ps.end_time) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7f1 100%);
  padding-bottom: 40px;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.welcome-section {
  max-width: 100%;
  margin: 20px auto 30px;
  padding: 30px;
  text-align: center;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  color: #333;
  position: relative;
  overflow: hidden;
}

.welcome-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.welcome-title {
  font-size: 2.2rem;
  color: #333;
  margin-bottom: 15px;
  font-weight: 600;
}

.welcome-subtitle {
  font-size: 1.1rem;
  color: #666;
  font-weight: 400;
}

.problemset-section {
  max-width: 100%;
  margin: 30px auto;
  padding: 35px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  min-height:60rem;
}

.problemset-title {
  font-size: 1.8rem;
  color: #333;
  margin-bottom: 25px;
  text-align: center;
  position: relative;
  padding-bottom: 15px;
  font-weight: 600;
}

.problemset-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 3px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
}

.no-problemsets {
  text-align: center;
  font-size: 1.2rem;
  color: #666;
  padding: 40px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.problemset-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  grid-auto-rows: 1fr;
  gap: 25px;
}

.problemset-item {
  padding: 25px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background-color: #fff;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  z-index: 1;
  box-sizing: border-box;
}

.problemset-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.problemset-item-title {
  font-size: 1.4rem;
  color: #333;
  margin-bottom: 15px;
  transition: color 0.2s ease;
  flex-grow: 1;
}

.problemset-item-description {
  font-size: 1rem;
  color: #666;
  margin-bottom: 20px;
  line-height: 1.6;
  flex-grow: 1;
}

.problemset-item-meta {
  font-size: 0.9rem;
  color: #999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: auto;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.problemset-item-meta span {
  display: flex;
  justify-content: space-between;
}

.problemset-item-meta span::before {
  content: '•';
  margin-right: 8px;
  color: #667eea;
}

.clickable {
  cursor: pointer;
  color: #007bff;
  text-decoration: underline;
}

.clickable:hover {
  color: #0056b3;
}

.disabled {
  color: #999;
  cursor: not-allowed;
  opacity: 0.7;
}

.disabled:hover {
  color: #999;
  cursor: not-allowed;
  text-decoration: none;
}

.disabled::after {
  display: none;
}
</style>