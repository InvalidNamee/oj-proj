<script setup>
import "@/assets/groups.css";
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'

const route = useRoute()
const group = ref(null)

onMounted(async () => {
  const res = await axios.get(`/api/groups/${route.params.id}`)
  group.value = res.data
})
</script>

<template>
  <div class="groups-detail-container">
    <h2 class="groups-detail-title">分组详情</h2>
    <div v-if="group">
      <div class="groups-detail-grid">
        <div class="groups-detail-grid-item"><b>ID：</b>{{ group.id }}</div>
        <div class="groups-detail-grid-item"><b>名称：</b>{{ group.name }}</div>
        <div class="groups-detail-grid-item groups-detail-grid-item-full"><b>描述：</b>{{ group.description }}</div>
        <div class="groups-detail-grid-item"><b>课程：</b>{{ group.course.name }} (ID: {{ group.course.id }})</div>
        <div class="groups-detail-grid-item"><b>学生数：</b>{{ group.students.length }}</div>
      </div>
      <div>
        <h3 class="groups-detail-section-title">学生列表</h3>
        <ul class="groups-detail-list">
          <li class="groups-detail-list-item" v-for="s in group.students" :key="s.id">{{ s.username }} (ID: {{ s.id }})</li>
        </ul>
        <h3 class="groups-detail-section-title">题单列表</h3>
        <ul class="groups-detail-list">
          <li class="groups-detail-list-item" v-for="ps in group.problemsets" :key="ps.id">{{ ps.title }} (ID: {{ ps.id }})</li>
        </ul>
      </div>
    </div>
  </div>
</template>
