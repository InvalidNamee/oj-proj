<script setup>
import '@/assets/components.css'
import { defineProps, defineEmits, computed } from 'vue';

const props = defineProps({
  courses: { type: Array, default: () => [] },
  modelValue: { type: Array, default: () => [] }
});

const emits = defineEmits(['update:modelValue']);

// computed 代理，避免双向 watch 循环
const selected = computed({
  get: () => props.modelValue,
  set: (val) => emits('update:modelValue', val)
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
