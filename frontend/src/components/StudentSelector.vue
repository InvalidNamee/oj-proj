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
    <label class="student-selector-label">选择学生</label>

    <input
      v-model="search"
      placeholder="搜索用户名/专业..."
      class="student-selector-input"
    />

    <div class="student-selector-list">
      <label v-for="s in filteredStudents" :key="s.id" class="student-selector-item">
        <input type="checkbox" :value="s.id" v-model="selectedIds"
               class="student-selector-checkbox" />
        <span class="student-selector-username">{{ s.username }} <span v-if="s.major" class="student-selector-major">({{ s.major }})</span></span>
      </label>
      <div v-if="filteredStudents.length === 0" class="student-selector-empty">无匹配学生</div>
    </div>
  </div>
</template>
