<script setup>
import { ref } from "vue";
import axios from "axios";

// ---------- 日志 ----------
const log = ref("");

// ---------- 列表 ----------
const courses = ref([]);
const page = ref(1);
const per_page = ref(10);
const total = ref(0);

const listCourses = async () => {
  try {
    const res = await axios.get("/courses", { params: { page: page.value, per_page: per_page.value } });
    courses.value = res.data.items;
    total.value = res.data.total;
    log.value += `\n[List Courses] 成功获取 ${res.data.items.length} 条数据\n`;
  } catch (e) {
    log.value += `\n[List Courses] 错误: ${e.response?.data?.error || e.message}\n`;
  }
};

// ---------- 创建 ----------
const newCourse = ref({ course_name: "", course_description: "", teacher_ids: [] });
const createCourse = async () => {
  const payload = {
    ...newCourse.value,
    teacher_ids: typeof newCourse.value.teacher_ids === "string"
      ? newCourse.value.teacher_ids.split(",").map(i => parseInt(i.trim())).filter(Boolean)
      : newCourse.value.teacher_ids
  };
  try {
    const res = await axios.post("/courses", payload);
    log.value += `\n[Create Course] 成功, ID=${res.data.id}\n`;
    await listCourses();
  } catch (e) {
    log.value += `\n[Create Course] 错误: ${e.response?.data?.error || e.message}\n`;
  }
};

// ---------- 详情 ----------
const queryCourseId = ref("");
const courseDetail = ref(null);
const getCourse = async () => {
  if (!queryCourseId.value) return;
  try {
    const res = await axios.get(`/courses/${queryCourseId.value}`);
    courseDetail.value = res.data;
    log.value += `\n[Get Course] 成功获取课程详情\n`;
  } catch (e) {
    log.value += `\n[Get Course] 错误: ${e.response?.data?.error || e.message}\n`;
  }
};

// ---------- 修改 ----------
const updateCourseData = ref({ course_name: "", course_description: "", teacher_ids: [], student_ids: [] });
const updateCourse = async () => {
  if (!queryCourseId.value) return;
  const payload = {
    ...updateCourseData.value,
    teacher_ids: typeof updateCourseData.value.teacher_ids === "string"
      ? updateCourseData.value.teacher_ids.split(",").map(i => parseInt(i.trim())).filter(Boolean)
      : updateCourseData.value.teacher_ids,
    student_ids: typeof updateCourseData.value.student_ids === "string"
      ? updateCourseData.value.student_ids.split(",").map(i => parseInt(i.trim())).filter(Boolean)
      : updateCourseData.value.student_ids,
  };
  try {
    await axios.put(`/courses/${queryCourseId.value}`, payload);
    log.value += `\n[Update Course] 成功修改课程\n`;
    await listCourses();
  } catch (e) {
    log.value += `\n[Update Course] 错误: ${e.response?.data?.error || e.message}\n`;
  }
};

// ---------- 删除单个 ----------
const deleteSingleCourse = async () => {
  if (!queryCourseId.value) return;
  try {
    await axios.delete(`/courses/${queryCourseId.value}`);
    log.value += `\n[Delete Course] 成功删除课程\n`;
    await listCourses();
  } catch (e) {
    log.value += `\n[Delete Course] 错误: ${e.response?.data?.error || e.message}\n`;
  }
};

// ---------- 批量删除 ----------
const batchDeleteIds = ref("");
const deleteCourses = async () => {
  const ids = batchDeleteIds.value.split(",").map(i => parseInt(i.trim())).filter(Boolean);
  if (!ids.length) return;
  try {
    const res = await axios.delete("/courses", { data: { courses: ids } });
    log.value += `\n[Batch Delete] 成功: ${res.data.success}, 失败: ${res.data.fail}\n`;
    await listCourses();
  } catch (e) {
    log.value += `\n[Batch Delete] 错误: ${e.response?.data?.error || e.message}\n`;
  }
};
</script>

<template>
  <div class="p-4 space-y-6">
    <!-- 列表 -->
    <section class="p-2 border rounded">
      <h3>课程列表</h3>
      <button @click="listCourses">刷新列表</button>
      <div>总数: {{ total }}</div>
      <ul>
        <li v-for="c in courses" :key="c.id">{{ c.id }} - {{ c.name }} - {{ c.description }}</li>
      </ul>
    </section>

    <!-- 创建 -->
    <section class="p-2 border rounded">
      <h3>创建课程</h3>
      <input v-model="newCourse.course_name" placeholder="课程名" />
      <input v-model="newCourse.course_description" placeholder="课程描述" />
      <input v-model="newCourse.teacher_ids" placeholder="教师ID逗号分隔" />
      <button @click="createCourse">创建</button>
    </section>

    <!-- 详情 -->
    <section class="p-2 border rounded">
      <h3>课程详情</h3>
      <input v-model="queryCourseId" placeholder="课程ID" />
      <button @click="getCourse">查询</button>
      <pre v-if="courseDetail">{{ courseDetail }}</pre>
    </section>

    <!-- 修改 -->
    <section class="p-2 border rounded">
      <h3>修改课程</h3>
      <input v-model="updateCourseData.course_name" placeholder="新课程名" />
      <input v-model="updateCourseData.course_description" placeholder="新描述" />
      <input v-model="updateCourseData.teacher_ids" placeholder="教师ID逗号分隔" />
      <input v-model="updateCourseData.student_ids" placeholder="学生ID逗号分隔" />
      <button @click="updateCourse">修改</button>
    </section>

    <!-- 删除单个 -->
    <section class="p-2 border rounded">
      <h3>删除课程</h3>
      <input v-model="queryCourseId" placeholder="课程ID" />
      <button @click="deleteSingleCourse">删除单个课程</button>
    </section>

    <!-- 批量删除 -->
    <section class="p-2 border rounded">
      <h3>批量删除课程</h3>
      <input v-model="batchDeleteIds" placeholder="课程ID逗号分隔" />
      <button @click="deleteCourses">批量删除</button>
    </section>

    <!-- 日志 -->
    <section class="p-2 border rounded">
      <h3>日志</h3>
      <pre class="whitespace-pre-wrap">{{ log }}</pre>
    </section>
  </div>
</template>

<style scoped>
input { display: block; margin-bottom: 6px; padding: 4px; width: 100%; }
button { padding: 4px 8px; margin-top: 4px; }
section { background: #f9f9f9; }
</style>
