<script setup>
import '@/assets/groups.css';
import { ref, computed, watch } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";

const groupName = ref("");
const description = ref("");
const router = useRouter();
const userStore = useUserStore();

const courseName = computed(() => {
  const course = userStore.courses.find(c => c.id === userStore.currentCourseId);
  return course ? course.name : '';
});

const createGroup = async () => {
  if (!groupName.value) {
    alert("请填写分组名称");
    return;
  }

  await axios.post("/api/groups", {
    course_id: userStore.currentCourseId,
    name: groupName.value,
    description: description.value
  });
  router.push("/groups");
};
</script>

<template>
  <div class="groups-add-container">
    <h2 class="groups-add-title">创建分组</h2>

    <!-- 当前课程显示 -->
    <div class="groups-add-form-group">
      <label class="groups-add-label">课程</label>
      <input type="text" :value="courseName" disabled class="groups-add-input groups-add-input-disabled" />
    </div>

    <div class="groups-add-form-group">
      <label class="groups-add-label">分组名称</label>
      <input v-model="groupName" type="text" class="groups-add-input" placeholder="请输入分组名称" />
    </div>

    <div class="groups-add-form-group">
      <label class="groups-add-label">描述</label>
      <textarea v-model="description" class="groups-add-textarea" placeholder="请输入分组描述"></textarea>
    </div>

    <button @click="createGroup" class="groups-add-button">
      创建
    </button>
  </div>
</template>
