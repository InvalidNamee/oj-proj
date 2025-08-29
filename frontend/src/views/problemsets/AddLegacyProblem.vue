<script setup>
import { ref, computed } from "vue";
import { useUserStore } from "@/stores/user";
import { useRouter } from "vue-router";
import axios from "axios";
import LegacyEditor from "@/components/LegacyEditor.vue";

const props = defineProps({
  problemType: { type: String, required: true },
  courseId: { type: Number, required: true }
});

const problemType = ref(props.problemType);

const userStore = useUserStore();
const router = useRouter();

const courseName = computed(() => {
  const course = userStore.courses.find(c => c.id === userStore.currentCourseId);
  return course ? course.name : "";
});

const title = ref("");
const description = ref("");
const testCases = ref({});

function updateTestCases(val) {
  testCases.value = val;
}

const submitting = ref(false);
async function submit() {
  if (submitting.value) return;
  submitting.value = true;

  const payload = {
    course_id: props.courseId,
    title: title.value,
    description: description.value,
    type: problemType.value,
    test_cases: testCases.value,
  };

  try {
    await axios.post("/api/problems/legacy", payload);
    alert("题目创建成功！");
    router.push("/problems");
  } catch (err) {
    console.error(err);
    alert(err.response?.data?.error || "创建失败");
  } finally {
    submitting.value = false;
  }
}

// 处理题目类型变更
const handleProblemTypeChange = () => {
  if (problemType.value === 'coding') {
    // 跳转到编程题创建页面
    router.push(`/problems/add`);
  } else if (problemType.value !== props.problemType) {
    // 跳转到对应的题目创建页面
    router.push(`/problems/add/${problemType.value}`);
  }
}
</script>

<template>
  <div class="add-legacy-problem-container">
    <div class="add-problem-header">
      <h2 class="add-problem-title">新建题目</h2>
      <!-- 题目类型选择器 -->
      <div>
        <label>题目类型:</label>
        <select v-model="problemType" @change="handleProblemTypeChange">
          <option value="single">单选题</option>
          <option value="multiple">多选题</option>
          <option value="fill">填空题</option>
          <option value="subjective">主观题</option>
          <option value="coding">编程题</option>
        </select>
      </div>
    </div>
    <!-- 标题 -->
    <div>
      <input v-model="title" placeholder="请输入题目标题"
        class="add-legacy-problem-input" />
    </div>

    <!-- 描述 -->
    <div>
      <textarea v-model="description" rows="6" placeholder="请输入题目描述"
        class="add-legacy-problem-textarea"></textarea>
    </div>

    <!-- 子组件 -->
    <LegacyEditor :problemType="props.problemType" @update:testCases="updateTestCases" />

    <!-- 所属课程 -->
    <div>
      <label class="block mb-1 font-medium">所属课程</label>
      <input type="text" :value="courseName" disabled
        class="add-legacy-problem-course-input" />
    </div>

    <!-- 提交按钮 -->
    <div class="add-legacy-problem-pt-2">
      <button @click="submit" :disabled="submitting"
        class="add-legacy-problem-submit-button"
        :class="submitting ? 'add-legacy-problem-disabled-input' : ''">
        {{ submitting ? "提交中…" : "提交" }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.add-problem-header {
  background-color: transparent;
  border: none;
}
</style>