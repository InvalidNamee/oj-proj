<script setup>
import '@/assets/components.css'
import { ref, computed, watch, onMounted } from "vue";
import axios from "axios";

const props = defineProps({
  currentCourseId: {
    type: Number,
    required: true,
  },
  modelValue: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["update:modelValue"]);

const problemsets = ref([]);
const search = ref(""); // 搜索框
const selectedIds = ref([...props.modelValue]);

// 获取当前课程的题单
const fetchProblemSets = async () => {
  const res = await axios.get("/api/problemsets/", {
    params: { course_id: props.currentCourseId },
  });
  problemsets.value = res.data.problemsets || [];
};
onMounted(fetchProblemSets);

// 根据搜索条件过滤题单（按标题）
const filteredProblemSets = computed(() => {
  if (!search.value) return problemsets.value;
  const key = search.value.toLowerCase();
  return problemsets.value.filter((p) => p.title.toLowerCase().includes(key));
});

// 同步外部 v-model
watch(
  () => props.modelValue,
  (val) => {
    if (JSON.stringify(val) !== JSON.stringify(selectedIds.value)) {
      selectedIds.value = [...val];
    }
  }
);
watch(selectedIds, (val) => {
  if (JSON.stringify(val) !== JSON.stringify(props.modelValue)) {
    emit("update:modelValue", val);
  }
});
</script>

<template>
  <div>
    <label class="problemset-selector-label">选择题单</label>

    <input
      v-model="search"
      placeholder="搜索题单..."
      class="problemset-selector-input"
    />

    <div class="problemset-selector-list">
      <label v-for="p in filteredProblemSets" :key="p.id" class="problemset-selector-item">
        <input type="checkbox" :value="p.id" v-model="selectedIds"
               class="problemset-selector-checkbox" />
        <span class="problemset-selector-title">{{ p.title }}</span>
      </label>
      <div v-if="filteredProblemSets.length === 0" class="problemset-selector-empty">无匹配题单</div>
    </div>
  </div>
</template>
