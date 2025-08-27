<script setup>
import '@/assets/components.css'
import { ref, computed, watch } from "vue";

// Props: teachers 数组, modelValue 用于 v-model 双向绑定
const props = defineProps({
  teachers: {
    type: Array,
    default: () => [],
  },
  modelValue: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["update:modelValue"]);

const search = ref(""); // 搜索框
const selectedIds = ref([...props.modelValue]); // 本地选中状态

// 根据搜索过滤教师
const filteredTeachers = computed(() => {
  if (!search.value) return props.teachers;
  return props.teachers.filter((t) =>
    t.username.toLowerCase().includes(search.value.toLowerCase())
  );
});

// 监听 props.modelValue 变化，保持本地 selectedIds 同步
watch(
  () => props.modelValue,
  (val) => {
    if (JSON.stringify(val) !== JSON.stringify(selectedIds.value)) {
      selectedIds.value = [...val];
    }
  }
);

// 监听 selectedIds 变化，通知父组件更新
watch(selectedIds, (val) => {
  if (JSON.stringify(val) !== JSON.stringify(props.modelValue)) {
    emit("update:modelValue", val);
  }
});
</script>

<template>
  <div>
    <label class="teacher-selector-label">选择教师</label>

    <!-- 搜索框 -->
    <input
      v-model="search"
      placeholder="搜索教师..."
      class="teacher-selector-input"
    />

    <!-- 列表 -->
    <div class="teacher-selector-list">
      <label v-for="t in filteredTeachers" :key="t.id" class="teacher-selector-item">
        <input type="checkbox" :value="t.id" v-model="selectedIds"
               class="teacher-selector-checkbox" />
        <span class="teacher-selector-username">{{ t.username }}</span>
      </label>

      <div v-if="filteredTeachers.length === 0" class="teacher-selector-empty">
        无匹配教师
      </div>
    </div>
  </div>
</template>
