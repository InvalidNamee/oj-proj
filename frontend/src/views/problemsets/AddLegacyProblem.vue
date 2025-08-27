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
    type: props.problemType,
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
</script>

<template>
  <div class="add-legacy-problem-container">
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
