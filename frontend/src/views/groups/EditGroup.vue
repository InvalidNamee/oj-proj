<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'
import StudentSelector from '@/components/StudentSelector.vue'
import ProblemSetSelector from '@/components/ProblemSetSelector.vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const group = ref(null)
const groupName = ref('')
const description = ref('')
const studentIds = ref([])
const problemsetIds = ref([])

onMounted(async () => {
  const res = await axios.get(`/api/groups/${route.params.id}`)
  group.value = res.data
  groupName.value = group.value.name
  description.value = group.value.description
  studentIds.value = group.value.students.map(s => s.id)
  problemsetIds.value = group.value.problemsets.map(ps => ps.id)
})

const updateGroup = async () => {
  await axios.put(`/api/groups/${group.value.id}`, {
    name: groupName.value,
    description: description.value,
    student_ids: studentIds.value,
    problemset_ids: problemsetIds.value
  })
  router.push('/groups')
}

const currentCourseId = computed(() => group.value?.course_id || userStore.currentCourseId)
</script>

<template>
  <div class="p-6 max-w-lg mx-auto">
    <h2 class="text-xl font-bold mb-4">编辑分组</h2>
    <div v-if="group">
      <div class="mb-3">
        <label class="block mb-1">分组名称</label>
        <input v-model="groupName" type="text" class="border border-gray-300 px-2 py-1 w-full" />
      </div>
      <div class="mb-3">
        <label class="block mb-1">描述</label>
        <textarea v-model="description" class="border border-gray-300 px-2 py-1 w-full"></textarea>
      </div>
      <div class="mb-3">
        <StudentSelector
          :currentCourseId="currentCourseId"
          v-model="studentIds"
        />
      </div>
      <div class="mb-3">
        <ProblemSetSelector
          :currentCourseId="currentCourseId"
          v-model="problemsetIds"
        />
      </div>
      <button @click="updateGroup" class="bg-blue-500 text-white px-4 py-2 rounded">保存</button>
    </div>
  </div>
</template>