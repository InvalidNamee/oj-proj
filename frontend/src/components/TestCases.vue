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

const localCases = ref(
  props.modelValue.map((tc, idx) => ({ id: tc.id ?? idx + 1, ...tc }))
)
let nextId = localCases.value.length + 1

watch(
  () => props.modelValue,
  (newVal) => {
    localCases.value = (newVal || []).map((tc, idx) => ({ id: tc.id ?? idx + 1, ...tc }));
    nextId = localCases.value.length + 1;
  },
  { deep: true, immediate: true } // immediate 保证初始化时也同步
);


function addCase() {
  localCases.value.push({ id: nextId++, input: '', output: '' })
}
function removeCase(index) {
  localCases.value.splice(index, 1)
}
</script>

<template>
  <div class="space-y-4">
    <!-- 这里显示标题 -->
    <h3 v-if="title" class="text-base font-semibold text-gray-700">{{ title }}</h3>

    <div v-for="(tc, index) in localCases" :key="tc.id" class="space-y-2">
      <div class="flex justify-between items-center text-sm text-gray-600">
        <span>{{ title }} {{ index + 1 }}</span>
        <button @click="removeCase(index)" class="text-red-500 hover:underline">删除</button>
      </div>

      <div>
        <label class="block text-xs text-gray-500 mb-1">输入</label>
        <textarea v-model="tc.input" rows="3"
          class="w-full rounded p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-400" />
      </div>

      <div>
        <label class="block text-xs text-gray-500 mb-1">期望输出</label>
        <textarea v-model="tc.output" rows="3"
          class="w-full rounded p-2 border border-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-400" />
      </div>
    </div>

    <button @click="addCase" class="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 text-sm">
      添加{{ title }}
    </button>
  </div>
</template>
