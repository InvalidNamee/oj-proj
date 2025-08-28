<script setup>
import { ref, onMounted, watch } from "vue"
import axios from "axios"

const props = defineProps({
  modelValue: Boolean,
  selectedUserId: String
})

const emit = defineEmits(['update:modelValue', 'userSelected'])

const users = ref([])
const selectedId = ref(props.selectedUserId || '')

// 获取用户列表
const fetchUsers = async () => {
  try {
    const res = await axios.get("/api/users", {
      params: {
        per_page: 100  // 获取较多用户以供选择
      }
    })
    users.value = res.data.users
  } catch (err) {
    console.error(err)
  }
}

// 选择用户
const selectUser = (userId) => {
  selectedId.value = userId
}

// 确认选择
const confirmSelection = () => {
  emit('userSelected', selectedId.value)
  closeModal()
}

// 关闭弹窗
const closeModal = () => {
  emit('update:modelValue', false)
}

// 监听弹窗打开事件
onMounted(() => {
  fetchUsers()
})

// 监听modelValue变化
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    fetchUsers()
  }
})
</script>

<template>
  <div v-if="modelValue" class="user-select-modal-overlay" @click="closeModal">
    <div class="user-select-modal" @click.stop>
      <div class="user-select-modal-header">
        <h3>选择用户</h3>
        <button class="user-select-modal-close" @click="closeModal">×</button>
      </div>
      
      <div class="user-select-modal-body">
        <div class="user-select-list">
          <div 
            v-for="user in users" 
            :key="user.id" 
            class="user-select-item"
            :class="{ 'user-select-item-selected': selectedId === user.id }"
            @click="selectUser(user.id)"
          >
            <div class="user-select-item-info">
              <div class="user-select-item-name">{{ user.username }}</div>
              <div class="user-select-item-id">ID: {{ user.id }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="user-select-modal-footer">
        <button @click="closeModal" class="user-select-cancel-button">取消</button>
        <button @click="confirmSelection" class="user-select-confirm-button" :disabled="!selectedId">确定</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-select-modal-overlay {
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

.user-select-modal {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.user-select-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #eee;
}

.user-select-modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.user-select-modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.user-select-modal-body {
  padding: 16px 24px;
  flex: 1;
  overflow-y: auto;
}

.user-select-search {
  display: flex;
  border: 1px solid #eee;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.user-select-list {
  border: 1px solid #eee;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.user-select-item {
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.user-select-item:last-child {
  border-bottom: none;
}

.user-select-item:hover {
  background-color: #f5f5f5;
}

.user-select-item-selected {
  background-color: #e8f4ff;
}

.user-select-item-info {
  flex: 1;
}

.user-select-item-name {
  font-weight: 500;
}

.user-select-item-id {
  font-size: 12px;
  color: #666;
}

.user-select-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #eee;
}

.user-select-cancel-button,
.user-select-confirm-button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.user-select-cancel-button {
  background-color: #f5f5f5;
  color: #333;
}

.user-select-confirm-button {
  background-color: #42b983;
  color: white;
}

.user-select-confirm-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>