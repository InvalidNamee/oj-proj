<script setup>
// filepath: /Users/star/tmp/test/src/views/CodingTesting.vue
import { ref } from 'vue';
import axios from 'axios';

// 题目创建/修改相关
const pid = ref('');
const title = ref('');
const description = ref('');
const timeLimit = ref('');
const memoryLimit = ref('');
const file = ref(null);
const createStatus = ref('');
const course_id = ref('')

// 题目信息获取/测试用例相关
const infoPid = ref(1); // 用于获取/操作题目的 pid
const problemInfo = ref(null);
const deleteStatus = ref('');
const addStatus = ref('');
const addFile = ref(null);

// 创建/修改题目
const handleFileChange = (e) => {
  file.value = e.target.files[0];
};

const handleSubmit = async (e) => {
  e.preventDefault();

  const limitations = {
    maxTime: Number(timeLimit.value) || 1,
    maxMemory: Number(memoryLimit.value) || 128,
    maxStack: 128,
    maxOutput: 10
  };

  const meta = {
    title: title.value,
    description: description.value,
    course_id: course_id.value,
    limitations
  };

  const formData = new FormData();
  formData.append('meta', JSON.stringify(meta));
  if (file.value) formData.append('test_cases.zip', file.value);

  try {
    if (pid.value) {
      const res = await axios.put(`/coding_problems/${pid.value}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      createStatus.value = '修改成功';
    } else {
      const res = await axios.post('/coding_problems/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      createStatus.value = '创建成功';
    }
  } catch (err) {
    console.error('提交失败', err);
    createStatus.value = '提交失败';
  }
};

// 题目信息获取
const fetchProblem = async () => {
  try {
    const res = await axios.get(`/coding_problems/${infoPid.value}`);
    problemInfo.value = res.data;
  } catch (err) {
    console.error(err);
    problemInfo.value = null;
  }
};

// 删除测试用例
const deleteTestCases = async () => {
  try {
    const res = await axios.patch(`/coding_problems/${infoPid.value}/test_cases/delete`, {
      cases: problemInfo.value?.test_cases?.cases || []
    });
    deleteStatus.value = '删除成功';
    problemInfo.value.test_cases = res.data;
  } catch (err) {
    console.error(err);
    deleteStatus.value = '删除失败';
  }
};

// 添加测试用例
const handleAddFileChange = (e) => {
  addFile.value = e.target.files[0];
};

const addTestCases = async () => {
  if (!addFile.value) return;
  const formData = new FormData();
  formData.append('test_cases.zip', addFile.value);

  try {
    const res = await axios.patch(`/coding_problems/${infoPid.value}/test_cases/add`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    addStatus.value = '添加成功';
    problemInfo.value.test_cases = res.data.remaining;
  } catch (err) {
    console.error(err);
    addStatus.value = '添加失败';
  }
};
</script>

<template>
  <div>
    <h3>创建/修改题目</h3>
    <form @submit="handleSubmit">
      <input type="text" v-model="pid" placeholder="题目 id (留空为创建)" id="pid" />
      <input type="text" v-model="course_id" placeholder="课程 id 不能留空" id="course_id">
      <input type="text" v-model="title" placeholder="题目名称" id="title" />
      <textarea name="描述" v-model="description" id="description"></textarea>
      <input type="text" v-model="timeLimit" placeholder="时间限制" id="timeLimit" />
      <input type="text" v-model="memoryLimit" placeholder="内存限制" id="memoryLimit" />
      <input type="file" id="file" @change="handleFileChange" />
      <button type="submit">提交</button>
      <p>{{ createStatus }}</p>
    </form>
  </div>

  <div>
    <h3>题目信息获取/测试用例操作</h3>
    <input type="text" v-model="infoPid" placeholder="填写 pid" />
    <button @click="fetchProblem">获取题目信息</button>
    <pre>{{ problemInfo }}</pre>

    <h4>删除测试用例</h4>
    <button @click="deleteTestCases">删除全部测试用例</button>
    <p>{{ deleteStatus }}</p>

    <h4>添加测试用例</h4>
    <input type="file" @change="handleAddFileChange" />
    <button @click="addTestCases">添加测试用例</button>
    <p>{{ addStatus }}</p>
  </div>
</template>

<style scoped>
form {
  display: flex;
  flex-direction: column;
}
div {
  margin: 2;
}
</style>