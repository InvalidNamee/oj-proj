<script setup>
import { ref, computed, onMounted, watch } from "vue";
import axios from "axios";
import { useUserStore } from "@/stores/user";

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(["update:modelValue"]);

const userStore = useUserStore();
const problems = ref([]);
const search = ref("");

// 获取课程下的代码题
const fetchProblems = async () => {
  if (!userStore.currentCourseId) return;
  const res = await axios.get("/api/problems/", {
    params: { course_id: userStore.currentCourseId },
  });
  problems.value = res.data.problems || [];
};

onMounted(fetchProblems);
watch(() => userStore.currentCourseId, fetchProblems);

// 搜索过滤
const filteredProblems = computed(() => {
  if (!search.value) return problems.value;
  const key = search.value.toLowerCase();
  return problems.value.filter(p => p.title.toLowerCase().includes(key));
});

// 双向绑定选中值
const updateSelection = (id) => {
  const newValue = [...props.modelValue];
  const idx = newValue.indexOf(id);
  if (idx >= 0) {
    newValue.splice(idx, 1);
  } else {
    newValue.push(id);
  }
  emit("update:modelValue", newValue);
};
</script>

<template>
  <div>
    <input
      v-model="search"
      placeholder="搜索题目名..."
      class="w-full p-2 mb-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
    />
    <div class="grid grid-cols-2 gap-2 max-h-48 overflow-auto border border-gray-300 rounded p-2">
      <label
        v-for="p in filteredProblems"
        :key="p.id"
        class="flex items-center space-x-2"
      >
        <input
          type="checkbox"
          :checked="props.modelValue.includes(p.id)"
          @change="updateSelection(p.id)"
          class="w-4 h-4"
        />
        <span>{{ p.title }}</span>
      </label>
      <div v-if="filteredProblems.length === 0" class="text-gray-400 text-sm">
        无匹配题目
      </div>
    </div>
  </div>
</template>
