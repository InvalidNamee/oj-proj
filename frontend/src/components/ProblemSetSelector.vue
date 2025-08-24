<script setup>
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
    <label class="block text-gray-700 mb-1">选择题单</label>

    <input
      v-model="search"
      placeholder="搜索题单..."
      class="w-full p-2 mb-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
    />

    <div class="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto border border-gray-300 rounded p-2">
      <label v-for="p in filteredProblemSets" :key="p.id" class="flex items-center space-x-2">
        <input type="checkbox" :value="p.id" v-model="selectedIds"
               class="w-4 h-4 border-gray-300 rounded focus:ring-2 focus:ring-blue-400" />
        <span class="text-gray-700">{{ p.title }}</span>
      </label>
      <div v-if="filteredProblemSets.length === 0" class="text-gray-400 text-sm">无匹配题单</div>
    </div>
  </div>
</template>
