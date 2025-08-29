<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

const stats = ref({
  registeredUsers: 0,
  courses: 0,
  problemTypeDistribution: [], // 题目类型分布数据
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

// 用户增长数据
const userGrowthData = ref([]);

// 获取真实数据
const fetchStats = async () => {
  try {
    // 获取用户总数
    const userRes = await axios.get('/api/users', { params: { per_page: 1 } });
    stats.value.registeredUsers = userRes.data.total;
    
    // 获取课程总数
    const courseRes = await axios.get('/api/courses', { params: { per_page: 1 } });
    stats.value.courses = courseRes.data.total;
    
    // 获取用户增长趋势数据
    await fetchUserGrowthData();
    
    // 获取题目类型分布数据
    await fetchProblemTypeDistribution();
  } catch (err) {
    console.error('获取统计数据失败', err);
  }
};

// 获取用户增长趋势数据
const fetchUserGrowthData = async () => {
  try {
    // 获取所有用户数据
    const userRes = await axios.get('/api/users', { params: { per_page: 1000 } });
    const users = userRes.data.users;
    
    // 按天统计用户注册数量
    const growthData = {};
    
    // 获取最近30天的日期
    const dates = [];
    for (let i = 29; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      dates.push(dateStr);
      growthData[dateStr] = 0;
    }
    
    // 统计每天的注册用户数
    users.forEach(user => {
      const registerDate = new Date(user.timestamp);
      const dateStr = registerDate.toISOString().split('T')[0];
      if (growthData[dateStr] !== undefined) {
        growthData[dateStr]++;
      }
    });
    
    // 计算累计用户数
    let cumulativeCount = 0;
    const cumulativeData = {};
    dates.forEach(date => {
      cumulativeCount += growthData[date];
      cumulativeData[date] = cumulativeCount;
    });
    
    // 转换为图表需要的格式
    userGrowthData.value = dates.map(date => ({
      date,
      count: cumulativeData[date]
    }));
  } catch (err) {
    console.error('获取用户增长数据失败', err);
  }
};

// 获取题目类型分布数据
const fetchProblemTypeDistribution = async () => {
  try {
    // 获取所有题目数据
    const res = await axios.get('/api/problems/', { params: { per_page: 1000 } });
    const problems = res.data.problems;
    
    // 统计各类型题目的数量
    const typeCount = {};
    problems.forEach(problem => {
      const type = problem.type;
      if (typeCount[type]) {
        typeCount[type]++;
      } else {
        typeCount[type] = 1;
      }
    });
    
    // 转换为图表需要的格式
    const typeDistribution = [];
    for (const type in typeCount) {
      typeDistribution.push({
        type,
        count: typeCount[type]
      });
    }
    
    stats.value.problemTypeDistribution = typeDistribution;
  } catch (err) {
    console.error('获取题目类型分布数据失败', err);
  }
};

// 计算折线图的点坐标
const getLinePoints = () => {
  if (userGrowthData.value.length === 0) return '';
  
  const maxCount = getMaxCount();
  const points = [];
  
  userGrowthData.value.forEach((item, index) => {
    const x = getCircleX(index);
    const y = getCircleY(item.count, maxCount);
    points.push(`${x},${y}`);
  });
  
  return points.join(' ');
};

// 计算数据点的X坐标
const getCircleX = (index) => {
  const totalPoints = userGrowthData.value.length;
  if (totalPoints <= 1) return 200;
  return 20 + (index * (360 / (totalPoints - 1)));
};

// 计算数据点的Y坐标
const getCircleY = (count, maxCount = getMaxCount()) => {
  if (maxCount === 0) return 200;
  return 200 - (count / maxCount) * 200;
};

// 获取最大用户数
const getMaxCount = () => {
  if (userGrowthData.value.length === 0) return 0;
  return Math.max(...userGrowthData.value.map(item => item.count));
};

// 获取X轴标签
const getXAxisLabels = () => {
  if (userGrowthData.value.length === 0) return [];
  
  const labels = [];
  const totalPoints = userGrowthData.value.length;
  
  // 只显示部分标签以避免重叠
  const step = Math.ceil(totalPoints / 6);
  
  for (let i = 0; i < totalPoints; i += step) {
    const date = userGrowthData.value[i].date;
    const dateObj = new Date(date);
    const month = dateObj.getMonth() + 1;
    const day = dateObj.getDate();
    labels.push(`${month}/${day}`);
  }
  
  return labels;
};

// 计算标签的X坐标
const getLabelX = (index) => {
  const labels = getXAxisLabels();
  const totalPoints = userGrowthData.value.length;
  if (totalPoints <= 1) return 200;
  
  const step = Math.ceil(totalPoints / 6);
  const actualIndex = index * step;
  return 20 + (actualIndex * (360 / (totalPoints - 1)));
};

const quickLinks = ref([
  { name: '我的课程', path: '/courses' },
  { name: '题库练习', path: '/problemsets' },
  { name: '提交记录', path: '/submissions' },
  { name: '个人中心', path: `/users/${userStore.id}` }
]);

// 类型映射函数
const getTypeDisplayName = (type) => {
  const typeMap = {
    'single': '单选题',
    'multiple': '多选题',
    'fill': '填空题',
    'subjective': '主观题',
    'coding': '编程题'
  };
  return typeMap[type] || type;
};

// 获取饼图数据
const getPieChartData = () => {
  if (stats.value.problemTypeDistribution.length === 0) return [];
  
  // 计算总数
  const total = stats.value.problemTypeDistribution.reduce((sum, item) => sum + item.count, 0);
  
  // 类型颜色映射
  const colorMap = {
    'coding': '#3b82f6',
    'single': '#10b981',
    'multiple': '#8b5cf6',
    'fill': '#f59e0b',
    'subjective': '#ef4444'
  };
  
  // 计算每个扇形的角度
  let startAngle = 0;
  const pieData = [];
  
  stats.value.problemTypeDistribution.forEach(item => {
    const percentage = total > 0 ? Math.round((item.count / total) * 100) : 0;
    const angle = (percentage / 100) * 360;
    
    // 计算扇形路径
    const path = describeArc(100, 100, 80, startAngle, startAngle + angle);
    
    pieData.push({
      type: item.type,
      count: item.count,
      percentage,
      angle,
      path,
      color: colorMap[item.type] || '#cccccc'
    });
    
    startAngle += angle;
  });
  
  return pieData;
};

// 计算扇形路径的辅助函数
function polarToCartesian(centerX, centerY, radius, angleInDegrees) {
  const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
  return {
    x: centerX + (radius * Math.cos(angleInRadians)),
    y: centerY + (radius * Math.sin(angleInRadians))
  };
}

function describeArc(x, y, radius, startAngle, endAngle) {
  const start = polarToCartesian(x, y, radius, endAngle);
  const end = polarToCartesian(x, y, radius, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
  
  const d = [
    "M", start.x, start.y,
    "A", radius, radius, 0, largeArcFlag, 0, end.x, end.y,
    "L", x, y,
    "Z"
  ].join(" ");
  
  return d;
}

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

    <!-- 图表区域 -->
    <div class="charts-section">
      <h2 class="section-title">数据统计</h2>
      <div class="charts-grid">
        <!-- 用户增长折线图 -->
        <div class="chart-card">
          <h3 class="chart-title">用户增长趋势</h3>
          <div class="line-chart">
            <div class="chart-container">
              <div class="y-axis">
                <span>{{ getMaxCount() }}</span>
                <span>{{ Math.floor(getMaxCount() * 0.75) }}</span>
                <span>{{ Math.floor(getMaxCount() * 0.5) }}</span>
                <span>{{ Math.floor(getMaxCount() * 0.25) }}</span>
                <span>0</span>
              </div>
              <div class="chart-content">
                <div class="line-graph">
                  <svg width="100%" height="200" viewBox="0 0 400 200">
                    <polyline
                      v-if="userGrowthData.length > 0"
                      fill="none"
                      stroke="#3b82f6"
                      stroke-width="2"
                      :points="getLinePoints()"
                    />
                    <!-- 数据点 -->
                    <circle 
                      v-for="(item, index) in userGrowthData" 
                      :key="index" 
                      :cx="getCircleX(index)" 
                      :cy="getCircleY(item.count)" 
                      r="4" 
                      fill="#3b82f6" 
                    />
                  </svg>
                </div>
                <div class="x-axis">
                  <span v-for="(label, index) in getXAxisLabels()" :key="index">{{ label }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 题目类型分布饼图 -->
        <div class="chart-card">
          <h3 class="chart-title">题目类型分布</h3>
          <div class="pie-chart">
            <div class="chart-container">
              <svg width="200" height="200" viewBox="0 0 200 200">
                <!-- 动态生成饼图扇形 -->
                <template v-for="(item, index) in getPieChartData()" :key="index">
                  <path :d="item.path" :fill="item.color" />
                </template>
                <!-- 中心圆 -->
                <circle cx="100" cy="100" r="30" fill="white" />
              </svg>
              <div class="legend">
                <div class="legend-item" v-for="(item, index) in getPieChartData()" :key="index">
                  <div class="legend-color" :style="{ backgroundColor: item.color }"></div>
                  <span>{{ getTypeDisplayName(item.type) }} ({{ item.percentage }}%)</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 提交状态柱状图 -->
        <div class="chart-card">
          <h3 class="chart-title">提交状态统计</h3>
          <div class="bar-chart">
            <div class="chart-container">
              <div class="y-axis">
                <span>80</span>
                <span>60</span>
                <span>40</span>
                <span>20</span>
                <span>0</span>
              </div>
              <div class="chart-content">
                <div class="bars">
                  <div class="bar-group">
                    <div class="bar" style="height: 162px; background-color: #10b981;"></div>
                    <span class="bar-label">通过</span>
                  </div>
                  <div class="bar-group">
                    <div class="bar" style="height: 50px; background-color: #ef4444;"></div>
                    <span class="bar-label">错误</span>
                  </div>
                  <div class="bar-group">
                    <div class="bar" style="height: 25px; background-color: #f59e0b;"></div>
                    <span class="bar-label">编译错误</span>
                  </div>
                  <div class="bar-group">
                    <div class="bar" style="height: 12px; background-color: #8b5cf6;"></div>
                    <span class="bar-label">超时</span>
                  </div>
                </div>
                <div class="x-axis">
                  <span></span>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        </div>
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
  background-color: white; /* 设置主页背景色为白色，覆盖全局背景色 */
}

/* 欢迎语区域 */
.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  padding: 40px;
  text-align: center;
  margin-bottom: 30px;
  color: white;
  animation: fadeInDown 1s ease-out;
}

.welcome-title {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 15px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  animation: slideInLeft 1s ease-out;
}

.welcome-subtitle {
  font-size: 1.3rem;
  animation: slideInRight 1s ease-out;
}

/* 统计数据卡片布局 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  padding: 25px;
  text-align: center;
  transition: transform 0.5s ease, box-shadow 0.5s ease;
  color: white;
  animation: zoomIn 0.8s ease-out;
}

.stat-card:nth-child(2) {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  animation-delay: 0.2s;
}

.stat-card:nth-child(3) {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  animation-delay: 0.4s;
}

.stat-card:hover {
  transform: translateY(-10px) scale(1.05);
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.3);
}

.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.stat-label {
  font-size: 1.1rem;
  font-weight: 500;
}

/* 图表区域 */
.charts-section {
  margin-bottom: 30px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.chart-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.chart-title {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 15px;
  color: #1f2937;
  text-align: center;
}

.chart-container {
  display: flex;
  align-items: flex-end;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  height: 200px;
  margin-right: 10px;
  color: #6b7280;
  font-size: 0.8rem;
  position: relative;
  top: -30px; /* 向上移动10像素 */
}

.y-axis span {
  position: absolute;
  left: 0;
  transform: translateY(-50%);
}

.y-axis span:nth-child(1) {
  top: 0%;
}

.y-axis span:nth-child(2) {
  top: 25%;
}

.y-axis span:nth-child(3) {
  top: 50%;
}

.y-axis span:nth-child(4) {
  top: 75%;
}

.y-axis span:nth-child(5) {
  top: 100%;
}

.chart-content {
  flex: 1;
}

.x-axis {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  color: #6b7280;
  font-size: 0.9rem;
}

/* 折线图 */
.line-graph {
  height: 200px;
  margin-bottom: 20px;
}

/* 饼图 */
.pie-chart .chart-container {
  flex-direction: column;
  align-items: center;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 15px;
}

.legend-item {
  display: flex;
  align-items: center;
  font-size: 0.85rem;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 5px;
}

/* 柱状图 */
.bars {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 200px;
  padding: 0 10px;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.bar {
  width: 40px;
  border-radius: 4px 4px 0 0;
  transition: height 0.5s ease;
}

.bar-label {
  font-size: 0.8rem;
  color: #6b7280;
}

/* 主要内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
}

/* 公告栏样式 */
.announcements-section {
  background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  padding: 25px;
  animation: fadeInUp 1s ease-out;
}

.section-title {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 20px;
  color: #1f2937;
  text-align: center;
  position: relative;
  padding-bottom: 15px;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border-radius: 2px;
}

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.announcement-item {
  padding: 20px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.announcement-item:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.announcement-title {
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: 10px;
  color: #1f2937;
}

.announcement-content {
  color: #4b5563;
  margin-bottom: 15px;
  line-height: 1.6;
}

.announcement-date {
  font-size: 0.9rem;
  color: #9ca3af;
  text-align: right;
  font-style: italic;
}

/* 快速链接样式 */
.quick-links-section {
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  padding: 25px;
  animation: fadeInUp 1s ease-out;
}

.links-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

.link-card {
  display: block;
  padding: 20px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.9);
  color: #1f2937;
  text-decoration: none;
  font-weight: 600;
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.link-card:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  color: #3b82f6;
}

/* 动画关键帧 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes zoomIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
