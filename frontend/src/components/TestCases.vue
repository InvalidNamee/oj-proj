<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  title: {
    type: String,
    default: ''
  }
})
const emit = defineEmits(['update:modelValue'])

const nextId = ref((props.modelValue || []).length + 1)

// 本地 copy
const localCases = ref([...props.modelValue])

// 父组件更新时同步
watch(
  () => props.modelValue,
  (newVal) => {
    localCases.value = [...newVal]
    nextId.value = localCases.value.length + 1
  },
  { deep: true, immediate: true }
)

// 子组件修改时通知父组件
function updateCase(index, field, value) {
  const arr = [...localCases.value]
  arr[index] = { ...arr[index], [field]: value }  // 用新对象触发响应
  localCases.value = arr
  emit('update:modelValue', arr)
}

function addCase() {
  const arr = [...localCases.value, { id: nextId.value++, input: '', output: '' }]
  localCases.value = arr
  emit('update:modelValue', arr)
}

function removeCase(index) {
  const arr = [...localCases.value]
  arr.splice(index, 1)
  localCases.value = arr
  emit('update:modelValue', arr)
}
</script>

<template>
  <div class="space-y-4">
    <h3 v-if="title" class="text-base font-semibold text-gray-700">{{ title }}</h3>

    <div v-for="(tc, index) in localCases" :key="tc.id" class="space-y-2">
      <div class="flex justify-between items-center text-sm text-gray-600">
        <span>{{ title }} {{ index + 1 }}</span>
        <button @click="removeCase(index)" class="text-red-500 hover:underline">删除</button>
      </div>

      <div>
        <label class="block text-xs text-gray-500 mb-1">输入</label>
        <textarea
          :value="tc.input"
          @input="updateCase(index, 'input', $event.target.value)"
          rows="3"
          class="w-full rounded p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-400"
        />
      </div>

      <div>
        <label class="block text-xs text-gray-500 mb-1">期望输出</label>
        <textarea
          :value="tc.output"
          @input="updateCase(index, 'output', $event.target.value)"
          rows="3"
          class="w-full rounded p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-400"
        />
      </div>
    </div>

    <button @click="addCase" class="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 text-sm">
      添加{{ title }}
    </button>
  </div>
</template>
