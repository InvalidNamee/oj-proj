<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import TeacherSelector from "@/components/TeacherSelector.vue"; // 你刚写的组件

const route = useRoute();
const router = useRouter();
const courseId = route.params.id;

// 数据
const courseName = ref("");
const courseDescription = ref("");
const teachers = ref([]); // 可选教师列表
const selectedTeacherIds = ref([]); // 已选教师

// 加载课程详情
const fetchCourse = async () => {
  try {
    const res = await axios.get(`/api/courses/${courseId}`);
    courseName.value = res.data.course_name;
    courseDescription.value = res.data.description;
    selectedTeacherIds.value = res.data.teachers.map(t => t.id);
  } catch (err) {
    alert(err.response?.data?.error || "获取课程失败");
  }
};

// 拉取所有教师
const fetchTeachers = async () => {
  try {
    const res = await axios.get("/api/users", {
      params: { usertype: "teacher" }
    });
    teachers.value = res.data.users;
  } catch (err) {
    console.error(err);
  }
};

onMounted(() => {
  fetchCourse();
  fetchTeachers();
});

// 保存修改
const saveCourse = async () => {
  try {
    const res = await axios.put(`/api/courses/${courseId}`, {
      course_name: courseName.value,
      course_description: courseDescription.value,
      teacher_ids: selectedTeacherIds.value
    });
    if (res.data.success) {
      alert("保存成功");
      router.push("/courses");
    }
  } catch (err) {
    alert(err.response?.data?.error || "保存失败");
  }
};
</script>

<template>
  <div class="course-add-container">
    <h2 class="course-edit-title">编辑课程</h2>

    <div class="mb-4">
      <label class="course-edit-label">课程名称</label>
      <input v-model="courseName" type="text" class="course-edit-input" />
    </div>

    <div class="mb-4">
      <label class="course-edit-label">课程描述</label>
      <textarea v-model="courseDescription" class="course-edit-textarea" rows="3" />
    </div>

    <div class="mb-4">
      <TeacherSelector
        v-model="selectedTeacherIds"
        :teachers="teachers"
      />
    </div>
    
    <div class="course-edit-spacer"></div>

    <div class="course-edit-button-container">
      <button @click="router.back()" class="course-edit-cancel-button">取消</button>
      <button @click="saveCourse" class="course-edit-save-button">保存</button>
    </div>
  </div>
</template>
