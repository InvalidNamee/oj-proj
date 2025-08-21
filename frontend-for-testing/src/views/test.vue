<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const problemSetId = ref('');
const codingProblems = ref([]);

const fetchProblems = async () => {
  try {
    const res = await axios.get('/coding_problems/', {
      params: problemSetId.value ? { psid: problemSetId.value } : {},
    });
    codingProblems.value = res.data.coding_problems;
  } catch (err) {
    console.error('获取题目失败', err);
    codingProblems.value = [];
  }
};

const handleSubmit = (e) => {
  e.preventDefault();
  fetchProblems();
};

onMounted(() => {
  fetchProblems(); // 默认加载全部题目
});
</script>

<template>
  <div>
    <h2>Coding Problems 列表</h2>
    <form @submit="handleSubmit">
      <input type="text" v-model="problemSetId" placeholder="题单 ID (可选)" />
      <button type="submit">筛选</button>
    </form>

    <ul>
      <li v-for="p in codingProblems" :key="p.id">
        <strong>{{ p.title }}</strong> (ID: {{ p.id }})<br/>
        描述: {{ p.description }}<br/>
        测试用例数: {{ p.num_test_cases }}<br/>
        更新时间: {{ p.timestamp }}
      </li>
    </ul>
  </div>
</template>

<style scoped>
ul {
  list-style: none;
  padding: 0;
}
li {
  margin-bottom: 12px;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
</style>
