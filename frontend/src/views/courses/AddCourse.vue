<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import TeacherSelector from "@/components/TeacherSelector.vue";

const router = useRouter();

// 表单数据
const courseName = ref("");
const courseDescription = ref("");
const teachers = ref([]);
const selectedTeacherIds = ref([]);

// 拉教师列表（管理员创建课程时可选）
const fetchTeachers = async () => {
  try {
    const res = await axios.get("/api/users", { params: { usertype: "teacher", per_page: 100 } });
    teachers.value = res.data.users;
  } catch (err) {
    console.error("获取教师列表失败", err);
  }
};

onMounted(() => {
  fetchTeachers();
});

// 提交课程
const submitCourse = async () => {
  if (!courseName.value.trim()) {
    alert("课程名称不能为空");
    return;
  }
  try {
    await axios.post("/api/courses", {
      course_name: courseName.value,
      course_description: courseDescription.value,
      teacher_ids: selectedTeacherIds.value
    });
    router.push("/courses");
  } catch (err) {
    alert(err.response?.data?.error || "添加课程失败");
  }
};
</script>

<template>
  <div class="course-add-container">
    <h2 class="course-add-title">添加课程</h2>

    <div class="mb-4">
      <label class="course-add-label">课程名称</label>
      <input v-model="courseName" class="course-add-input" placeholder="请输入课程名称" />
    </div>

    <div class="mb-4">
      <label class="course-add-label">课程描述</label>
      <textarea v-model="courseDescription" class="course-add-textarea" placeholder="请输入课程描述"></textarea>
    </div>

    <TeacherSelector v-model="selectedTeacherIds" :teachers="teachers" class="mb-4" />
    
    <div class="course-add-spacer"></div>

    <div class="course-add-button-container">
      <button @click="submitCourse" class="course-add-submit-button">提交</button>
      <button @click="router.back()" class="course-add-cancel-button">取消</button>
    </div>
  </div>
</template>
