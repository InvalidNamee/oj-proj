<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const legacyProblems = ref([]);
const selectedProblem = ref(null);
const pidToDelete = ref('');
const updateData = ref({ title: '', description: '', options: '', answers: '' });
const importData = ref('[{"problem_type":"choice","title":"示例题","description":"题目描述","options":["A","B","C"],"answers":["A"]}]');

// 获取所有题目列表
const fetchLegacyProblems = async () => {
  try {
    const res = await axios.get('/legacy_problems/');
    legacyProblems.value = res.data.legacy_problems;
    console.log(legacyProblems)
  } catch (err) {
    console.error('获取失败', err);
  }
};

// 查询单个题目
const fetchProblem = async (pid) => {
  try {
    const res = await axios.get(`/legacy_problems/${pid}`);
    selectedProblem.value = res.data;
    updateData.value = { 
      title: res.data.title, 
      type: res.data.problem_type,
      description: res.data.description, 
      options: res.data.options || '', 
      answers: '' 
    };
  } catch (err) {
    console.error('查询失败', err);
  }
};

// 删除题目
const deleteProblem = async () => {
  try {
    const problem_id_list = pidToDelete.value.split(',').map(id => parseInt(id.trim()));
    const res = await axios.delete('/legacy_problems/', { data: { problem_id_list } });
    console.log('删除结果', res.data);
    fetchLegacyProblems();
  } catch (err) {
    console.error('删除失败', err);
  }
};

// 更新题目
const updateProblem = async (pid) => {
  try {
    const res = await axios.put(`/legacy_problems/${pid}`, updateData.value);
    console.log('更新成功', res.data);
    fetchLegacyProblems();
  } catch (err) {
    console.error('更新失败', err);
  }
};

// 批量导入题目
const importProblems = async () => {
  try {
    const problem_list = JSON.parse(importData.value);
    const res = await axios.post('/legacy_problems/import', { problem_list });
    console.log('导入结果', res.data);
    fetchLegacyProblems();
  } catch (err) {
    console.error('导入失败', err);
  }
};

onMounted(fetchLegacyProblems);
</script>

<template>
  <div>
    <h1>Legacy 题目列表</h1>
    <ul>
      <li v-for="p in legacyProblems" :key="p.id">
        {{ p.id }} - {{ p.problem_type }} - {{ p.title }} - {{ p.timestamp }}
        <button @click="fetchProblem(p.id)">查看/修改</button>
      </li>
    </ul>

    <h2>查询/修改题目</h2>
    <div v-if="selectedProblem">
      <p>ID: {{ selectedProblem.id }}</p>
      <input v-model="updateData.title" placeholder="标题" />
      <textarea v-model="updateData.description" placeholder="描述"></textarea>
      <input v-model="updateData.options" placeholder="选项 (JSON)" />
      <input v-model="updateData.answers" placeholder="答案" />
      <button @click="updateProblem(selectedProblem.id)">更新题目</button>
    </div>

    <h2>批量删除</h2>
    <input v-model="pidToDelete" placeholder="输入要删除的ID，用逗号分隔" />
    <button @click="deleteProblem">删除</button>

    <h2>批量导入</h2>
    <textarea v-model="importData" rows="6" style="width:100%"></textarea>
    <button @click="importProblems">导入题目</button>
  </div>
</template>
