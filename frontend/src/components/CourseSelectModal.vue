<script setup>
import { ref, onMounted, watch } from "vue"
import axios from "axios"

const props = defineProps({
  modelValue: Boolean,
  selectedCourseId: String
})

const emit = defineEmits(['update:modelValue', 'courseSelected'])

const courses = ref([])
const selectedId = ref(props.selectedCourseId || '')

// 获取课程列表
const fetchCourses = async () => {
  try {
    const res = await axios.get("/api/courses", {
      params: {
        per_page: 100  // 获取较多课程以供选择
      }
    })
    courses.value = res.data.items
  } catch (err) {
    console.error(err)
  }
}

// 选择课程
const selectCourse = (courseId) => {
  selectedId.value = courseId
}

// 确认选择
const confirmSelection = () => {
  emit('courseSelected', selectedId.value)
  closeModal()
}

// 关闭弹窗
const closeModal = () => {
  emit('update:modelValue', false)
}

// 监听弹窗打开事件
onMounted(() => {
  fetchCourses()
})

// 监听modelValue变化
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    fetchCourses()
  }
})
</script>

<template>
  <div v-if="modelValue" class="course-select-modal-overlay" @click="closeModal">
    <div class="course-select-modal" @click.stop>
      <div class="course-select-modal-header">
        <h3>选择课程</h3>
        <button class="course-select-modal-close" @click="closeModal">×</button>
      </div>
      
      <div class="course-select-modal-body">
        <div class="course-select-list">
          <div 
            v-for="course in courses" 
            :key="course.id" 
            class="course-select-item"
            :class="{ 'course-select-item-selected': selectedId === course.id }"
            @click="selectCourse(course.id)"
          >
            <div class="course-select-item-info">
              <div class="course-select-item-name">{{ course.name }}</div>
              <div class="course-select-item-id">ID: {{ course.id }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="course-select-modal-footer">
        <button @click="closeModal" class="course-select-cancel-button">取消</button>
        <button @click="confirmSelection" class="course-select-confirm-button" :disabled="!selectedId">确定</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.course-select-modal-overlay {
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

.course-select-modal {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.course-select-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #eee;
}

.course-select-modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.course-select-modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.course-select-modal-body {
  padding: 16px 24px;
  flex: 1;
  overflow-y: auto;
}

.course-select-list {
  border: 1px solid #eee;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.course-select-item {
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.course-select-item:last-child {
  border-bottom: none;
}

.course-select-item:hover {
  background-color: #f5f5f5;
}

.course-select-item-selected {
  background-color: #e8f4ff;
}

.course-select-item-info {
  flex: 1;
}

.course-select-item-name {
  font-weight: 500;
}

.course-select-item-id {
  font-size: 12px;
  color: #666;
}

.course-select-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #eee;
}

.course-select-cancel-button,
.course-select-confirm-button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.course-select-cancel-button {
  background-color: #f5f5f5;
  color: #333;
}

.course-select-confirm-button {
  background-color: #42b983;
  color: white;
}

.course-select-confirm-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>