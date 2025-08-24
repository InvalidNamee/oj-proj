<script setup>
import { defineProps, defineEmits, watch, ref } from 'vue';

const props = defineProps({
  courses: { type: Array, default: () => [] },        // 可选课程列表 [{id, name}, ...]
  modelValue: { type: Array, default: () => [] }     // 初始选中的课程 id 列表
});

const emits = defineEmits(['update:modelValue']);

// 本地选中状态
const selected = ref([...props.modelValue]);

// 当本地选中改变时通知父组件
watch(selected, (val) => {
  emits('update:modelValue', val);
});
</script>

<template>
  <div>
    <label class="block text-gray-700 mb-1">选择课程</label>
    <div class="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto border border-gray-300 rounded p-2">
      <label v-for="c in courses" :key="c.id" class="flex items-center space-x-2">
        <input type="checkbox" :value="c.id" v-model="selected"
               class="w-4 h-4 border-gray-300 rounded focus:ring-2 focus:ring-blue-400" />
        <span class="text-gray-700">{{ c.name }}</span>
      </label>
    </div>
  </div>
</template>
