<script setup>
import '@/assets/components.css'
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

// 当父组件传入的modelValue改变时，更新本地选中状态
watch(() => props.modelValue, (newVal) => {
  selected.value = [...newVal];
});
</script>

<template>
  <div>
    <label class="course-selector-label">选择课程</label>
    <div class="course-selector-list">
      <label v-for="c in courses" :key="c.id" class="course-selector-item">
        <input type="checkbox" :value="c.id" v-model="selected"
               class="course-selector-checkbox" />
        <span class="course-selector-name">{{ c.name }}</span>
      </label>
    </div>
  </div>
</template>
