<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import axios from "axios";
import ProblemSelector from "@/components/ProblemSelector.vue";
import "@/assets/pr6.css";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const psid = route.params.id;

const title = ref("");
const description = ref("");
const Selected = ref([]);
const timeRange = ref([]); // [开始时间, 结束时间]

// 当前课程
const courseId = computed(() => userStore.currentCourseId);
const courseName = computed(() => {
  const course = userStore.courses.find(c => c.id === userStore.currentCourseId);
  return course ? course.name : '';
});

const fetchProblemSet = async () => {
  const res = await axios.get(`/api/problemsets/${psid}`);
  const data = res.data;
  title.value = data.title;
  description.value = data.description;
  Selected.value = data.problems.map(p => p.id);
  // 设置时间范围
  if (data.start_time || data.end_time) {
    timeRange.value = [data.start_time, data.end_time];
  }
};

const submit = async () => {
  if (!courseId.value) {
    alert("请先选择课程");
    return;
  }
  await axios.put(`/api/problemsets/${psid}`, {
    title: title.value,
    description: description.value,
    course_id: courseId.value,
    problem_ids: Selected.value,
    start_time: timeRange.value[0], // 添加开始时间
    end_time: timeRange.value[1]     // 添加结束时间
  });
  router.push("/problemsets");
};

onMounted(fetchProblemSet);
</script>

<template>
  <div class="edit-problem-set-container">
    <h2 class="edit-problem-set-title">编辑题单</h2>
    <div class="edit-problem-set-space-y-4">
      <input
        v-model="title"
        placeholder="题单标题"
        class="edit-problem-set-input"
      />
      <textarea
        v-model="description"
        rows="4"
        placeholder="描述"
        class="edit-problem-set-textarea"
      ></textarea>

      <!-- 时间选择器 -->
      <div>
        <label class="edit-problem-set-label">题单时间</label>
        <el-date-picker
          v-model="timeRange"
          type="datetimerange"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DD HH:mm:ss"
          class="edit-problem-set-date-picker"
        >
        </el-date-picker>
      </div>

      <!-- 课程显示 -->
      <div>
        <label class="edit-problem-set-label">所属课程（不可更改）</label>
        <input
          type="text"
          :value="courseName"
          disabled
          class="edit-problem-set-disabled-input"
        />
      </div>

      <!-- Coding 题目选择器 -->
      <div>
        <label class="edit-problem-set-label">选题</label>
        <ProblemSelector v-model="Selected" />
      </div>

      <button
        @click="submit"
        class="edit-problem-set-button"
      >
        提交修改
      </button>
    </div>
  </div>
</template>
