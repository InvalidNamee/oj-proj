<template>
  <div class="self-test-panel p-4 border rounded space-y-4">
    <h2 class="text-lg font-semibold">自测测试用例</h2>

    <div v-for="(tc, index) in localCases" :key="tc.id" class="border p-2 rounded space-y-2">
      <div class="flex justify-between items-center">
        <span>测试用例 {{ index + 1 }}</span>
        <button @click="removeCase(index)" class="text-red-500 text-sm">删除</button>
      </div>

      <div>
        <label class="block text-sm font-medium">输入</label>
        <textarea v-model="tc.input" rows="3" class="w-full border rounded p-1"></textarea>
      </div>

      <div>
        <label class="block text-sm font-medium">期望输出</label>
        <textarea v-model="tc.output" rows="3" class="w-full border rounded p-1"></textarea>
      </div>
    </div>

    <button @click="addCase" class="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600">
      添加测试用例
    </button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  }
})
const emit = defineEmits(['update:modelValue'])

// 给每个已有用例补上 id
const localCases = ref(
  props.modelValue.map((tc, idx) => ({ id: tc.id ?? idx + 1, ...tc }))
)
let nextId = localCases.value.length + 1

watch(localCases, (newVal) => {
  emit('update:modelValue', newVal)
}, { deep: true })

function addCase() {
  localCases.value.push({ id: nextId++, input: '', output: '' })
}

function removeCase(index) {
  localCases.value.splice(index, 1)
}
</script>

<style scoped>
textarea {
  resize: vertical;
}
</style>
