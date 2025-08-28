<script setup>
import { ref, onMounted, watch } from "vue"
import axios from "axios"
import { useUserStore } from "@/stores/user.js"

const props = defineProps({
  modelValue: Boolean,
  selectedProblemSetId: String
})

const emit = defineEmits(['update:modelValue', 'problemSetSelected'])

const problemSets = ref([])
const selectedId = ref(props.selectedProblemSetId || '')
const userStore = useUserStore()

// 获取题单列表
const fetchProblemSets = async () => {
  try {
    const res = await axios.get("/api/problemsets/", {
      params: {
        per_page: 100,  // 获取较多题单以供选择
        course_id: userStore.currentCourseId
      }
    })
    problemSets.value = res.data.problemsets
  } catch (err) {
    console.error(err)
  }
}

// 选择题单
const selectProblemSet = (problemSetId) => {
  selectedId.value = problemSetId
}

// 确认选择
const confirmSelection = () => {
  emit('problemSetSelected', selectedId.value)
  closeModal()
}

// 关闭弹窗
const closeModal = () => {
  emit('update:modelValue', false)
}

// 监听弹窗打开事件
onMounted(() => {
  fetchProblemSets()
})

// 监听modelValue变化
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    fetchProblemSets()
  }
})
</script>

<template>
  <div v-if="modelValue" class="problem-set-select-modal-overlay" @click="closeModal">
    <div class="problem-set-select-modal" @click.stop>
      <div class="problem-set-select-modal-header">
        <h3>选择题单</h3>
        <button class="problem-set-select-modal-close" @click="closeModal">×</button>
      </div>
      
      <div class="problem-set-select-modal-body">
        <div class="problem-set-select-list">
          <div 
            v-for="problemSet in problemSets" 
            :key="problemSet.id" 
            class="problem-set-select-item"
            :class="{ 'problem-set-select-item-selected': selectedId === problemSet.id }"
            @click="selectProblemSet(problemSet.id)"
          >
            <div class="problem-set-select-item-info">
              <div class="problem-set-select-item-name">{{ problemSet.title }}</div>
              <div class="problem-set-select-item-id">ID: {{ problemSet.id }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="problem-set-select-modal-footer">
        <button @click="closeModal" class="problem-set-select-cancel-button">取消</button>
        <button @click="confirmSelection" class="problem-set-select-confirm-button" :disabled="!selectedId">确定</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.problem-set-select-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.problem-set-select-modal {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.problem-set-select-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #eee;
}

.problem-set-select-modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.problem-set-select-modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.problem-set-select-modal-body {
  padding: 16px 24px;
  flex: 1;
  overflow-y: auto;
}

.problem-set-select-list {
  border: 1px solid #eee;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.problem-set-select-item {
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.problem-set-select-item:last-child {
  border-bottom: none;
}

.problem-set-select-item:hover {
  background-color: #f5f5f5;
}

.problem-set-select-item-selected {
  background-color: #e8f4ff;
}

.problem-set-select-item-info {
  flex: 1;
}

.problem-set-select-item-name {
  font-weight: 500;
}

.problem-set-select-item-id {
  font-size: 12px;
  color: #666;
}

.problem-set-select-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #eee;
}

.problem-set-select-cancel-button,
.problem-set-select-confirm-button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.problem-set-select-cancel-button {
  background-color: #f5f5f5;
  color: #333;
}

.problem-set-select-confirm-button {
  background-color: #42b983;
  color: white;
}

.problem-set-select-confirm-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>