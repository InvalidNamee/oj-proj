<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'
import StudentSelector from '@/components/StudentSelector.vue'
import ProblemSetSelector from '@/components/ProblemSetSelector.vue'
import { useUserStore } from '@/stores/user'
import '@/assets/groups.css'

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
  <div class="groups-edit-container">
    <h2 class="groups-edit-title">编辑分组</h2>
    <div v-if="group">
      <div class="groups-edit-form-group">
        <label class="groups-edit-label">分组名称</label>
        <input v-model="groupName" type="text" class="groups-edit-input" />
      </div>
      <div class="groups-edit-form-group">
        <label class="groups-edit-label">描述</label>
        <textarea v-model="description" class="groups-edit-textarea"></textarea>
      </div>
      <div class="groups-edit-form-group">
        <StudentSelector
          :currentCourseId="currentCourseId"
          v-model="studentIds"
        />
      </div>
      <div class="groups-edit-form-group">
        <ProblemSetSelector
          :currentCourseId="currentCourseId"
          v-model="problemsetIds"
        />
      </div>
      <button @click="updateGroup" class="groups-edit-save-button">保存</button>
    </div>
  </div>
</template>