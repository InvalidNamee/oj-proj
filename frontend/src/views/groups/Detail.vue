<script setup>
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
  <div class="p-6 max-w-4xl mx-auto">
    <h2 class="text-xl font-bold mb-4">分组详情</h2>
    <div v-if="group">
      <div class="grid grid-cols-2 gap-x-6 gap-y-2 text-sm mb-4">
        <div><b>ID：</b>{{ group.id }}</div>
        <div><b>名称：</b>{{ group.name }}</div>
        <div class="col-span-2"><b>描述：</b>{{ group.description }}</div>
        <div><b>课程：</b>{{ group.course.name }} (ID: {{ group.course.id }})</div>
        <div><b>学生数：</b>{{ group.students.length }}</div>
      </div>
      <div>
        <h3 class="font-semibold mb-2">学生列表</h3>
        <ul class="list-disc pl-5 mb-4">
          <li v-for="s in group.students" :key="s.id">{{ s.username }} (ID: {{ s.id }})</li>
        </ul>
        <h3 class="font-semibold mb-2">题单列表</h3>
        <ul class="list-disc pl-5">
          <li v-for="ps in group.problemsets" :key="ps.id">{{ ps.title }} (ID: {{ ps.id }})</li>
        </ul>
      </div>
    </div>
  </div>
</template>
