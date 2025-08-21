
<script setup>
import { ref } from "vue";
import axios from "axios";

const result = ref({});

// 1. 创建组
const createForm = ref({ course_id: "", name: "", description: "" });
const createGroup = async () => {
  try {
    const res = await axios.post("/groups", createForm.value, {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
    });
    result.value = res.data;
  } catch (err) {
    result.value = err.response?.data || err.message;
  }
};

// 2. 删除组
const deleteIds = ref("");
const deleteGroups = async () => {
  try {
    const res = await axios.delete("/groups", {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
      data: { group_ids: deleteIds.value.split(",").map(id => Number(id.trim())) },
    });
    result.value = res.data;
  } catch (err) {
    result.value = err.response?.data || err.message;
  }
};

// 3. 分配学生
const updateForm = ref({ group_id: "", student_ids: "", problemset_ids: ""});
const updateGroup = async () => {
  try {
    const res = await axios.put(`/groups/${updateForm.value.group_id}`, {
      student_ids: updateForm.value.student_ids.split(",").map(id => Number(id.trim())),
      problemset_ids: updateForm.value.problemset_ids.split(",").map(id => Number(id.trim()))
    }, {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
    });
    result.value = res.data;
  } catch (err) {
    result.value = err.response?.data || err.message;
  }
};

// 4. 获取组列表
const queryCourseId = ref("");
const getGroups = async () => {
  try {
    const res = await axios.get("/groups", {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
      params: queryCourseId.value ? { course_id: queryCourseId.value } : {}
    });
    result.value = res.data;
  } catch (err) {
    result.value = err.response?.data || err.message;
  }
};

// 5. 获取组详情
const detailGroupId = ref("");
const getGroupDetail = async () => {
  try {
    const res = await axios.get(`/groups/${detailGroupId.value}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
    });
    result.value = res.data;
  } catch (err) {
    result.value = err.response?.data || err.message;
  }
};
</script>


<template>
  <div class="p-6 space-y-4">
    <h1 class="text-xl font-bold">Groups API 调试面板</h1>

    <!-- 创建组 -->
    <div class="p-4 border rounded">
      <h2 class="font-semibold mb-2">1. 创建组</h2>
      <input v-model="createForm.course_id" placeholder="course_id" class="border p-1 mr-2" />
      <input v-model="createForm.name" placeholder="组名" class="border p-1 mr-2" />
      <input v-model="createForm.description" placeholder="描述" class="border p-1 mr-2" />
      <button class="bg-blue-500 text-white px-3 py-1" @click="createGroup">提交</button>
    </div>

    <!-- 删除组 -->
    <div class="p-4 border rounded">
      <h2 class="font-semibold mb-2">2. 删除组</h2>
      <input v-model="deleteIds" placeholder="组id, 用逗号分隔" class="border p-1 mr-2" />
      <button class="bg-red-500 text-white px-3 py-1" @click="deleteGroups">删除</button>
    </div>

    <!-- 分配学生 -->
    <div class="p-4 border rounded">
      <h2 class="font-semibold mb-2">3. 分配学生到组</h2>
      <input v-model="updateForm.group_id" placeholder="组id" class="border p-1 mr-2" />
      <input v-model="updateForm.student_ids" placeholder="学生id, 用逗号分隔" class="border p-1 mr-2" />
      <input v-model="updateForm.problemset_ids" placeholder="题单id, 用逗号分隔" class="border p-1 mr-2" />
      <button class="bg-green-500 text-white px-3 py-1" @click="updateGroup">分配</button>
    </div>

    <!-- 获取组列表 -->
    <div class="p-4 border rounded">
      <h2 class="font-semibold mb-2">4. 获取组列表</h2>
      <input v-model="queryCourseId" placeholder="course_id (可选)" class="border p-1 mr-2" />
      <button class="bg-gray-500 text-white px-3 py-1" @click="getGroups">查询</button>
    </div>

    <!-- 获取组详情 -->
    <div class="p-4 border rounded">
      <h2 class="font-semibold mb-2">5. 获取组详情</h2>
      <input v-model="detailGroupId" placeholder="组id" class="border p-1 mr-2" />
      <button class="bg-purple-500 text-white px-3 py-1" @click="getGroupDetail">查看</button>
    </div>

    <!-- 输出结果 -->
    <div class="p-4 border rounded bg-gray-50">
      <h2 class="font-semibold mb-2">返回结果</h2>
      <pre class="text-sm">{{ JSON.stringify(result, null, 2) }}</pre>
    </div>
  </div>
</template>