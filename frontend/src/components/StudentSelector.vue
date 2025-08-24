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

const students = ref([]);
const search = ref(""); // 搜索框
const selectedIds = ref([...props.modelValue]);

// 获取当前课程的学生
const fetchStudents = async () => {
  const res = await axios.get("/api/users", {
    params: { course_id: props.currentCourseId, usertype: "student", per_page: 1000},
  });
  students.value = res.data.users || [];
};
onMounted(fetchStudents);

// 根据搜索条件过滤学生（用户名或专业）
const filteredStudents = computed(() => {
  if (!search.value) return students.value;
  const key = search.value.toLowerCase();
  return students.value.filter(
    (s) =>
      s.username.toLowerCase().includes(key) ||
      (s.major && s.major.toLowerCase().includes(key))
  );
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
    <label class="block text-gray-700 mb-1">选择学生</label>

    <input
      v-model="search"
      placeholder="搜索用户名/专业..."
      class="w-full p-2 mb-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
    />

    <div class="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto border border-gray-300 rounded p-2">
      <label v-for="s in filteredStudents" :key="s.id" class="flex items-center space-x-2">
        <input type="checkbox" :value="s.id" v-model="selectedIds"
               class="w-4 h-4 border-gray-300 rounded focus:ring-2 focus:ring-blue-400" />
        <span class="text-gray-700">{{ s.username }} <span v-if="s.major" class="text-gray-400">({{ s.major }})</span></span>
      </label>
      <div v-if="filteredStudents.length === 0" class="text-gray-400 text-sm">无匹配学生</div>
    </div>
  </div>
</template>
