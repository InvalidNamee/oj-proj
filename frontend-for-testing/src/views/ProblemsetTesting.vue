<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

// 题单列表
const problemsets = ref([]);
const page = ref(1);
const perPage = ref(10);
const courseId = ref('');
const total = ref(0);

// 创建/更新表单
const form = ref({
  id: null, // 更新时用
  title: '',
  description: '',
  course_id: '',
  legacy_problem_ids: '',
  coding_problem_ids: ''
});

// 获取题单列表
const fetchProblemsets = async () => {
  try {
    const res = await axios.get('/problemsets/', {
      params: {
        page: page.value,
        per_page: perPage.value,
        course_id: courseId.value || undefined,
      },
    });
    problemsets.value = res.data.problemsets;
    total.value = res.data.total;
  } catch (err) {
    console.error('获取题单失败', err);
  }
};

// 查看单个题单详情
const fetchProblemsetDetail = async (psid) => {
  try {
    const res = await axios.get(`/problemsets/${psid}`);
    alert(JSON.stringify(res.data, null, 2));
  } catch (err) {
    console.error('获取题单详情失败', err);
  }
};

// 创建题单
const createProblemset = async () => {
  try {
    const res = await axios.post('/problemsets/', {
      title: form.value.title,
      description: form.value.description,
      course_id: form.value.course_id || null,
      legacy_problem_ids: form.value.legacy_problem_ids.split(',').map(id => parseInt(id.trim())),
      coding_problem_ids: form.value.coding_problem_ids.split(',').map(id => parseInt(id.trim())),
    });
    alert(`创建成功，ID: ${res.data.id}`);
    fetchProblemsets();
  } catch (err) {
    console.error('创建题单失败', err);
  }
};

// 更新题单
const updateProblemset = async () => {
  if (!form.value.id) {
    alert('请填写要更新的题单ID');
    return;
  }
  try {
    const res = await axios.put(`/problemsets/${form.value.id}`, {
      title: form.value.title,
      description: form.value.description,
      course_id: form.value.course_id || null,
      legacy_problem_ids: form.value.legacy_problem_ids.split(',').map(id => parseInt(id.trim())),
      coding_problem_ids: form.value.coding_problem_ids.split(',').map(id => parseInt(id.trim())),
    });
    alert(`更新成功，ID: ${res.data.id}`);
    fetchProblemsets();
  } catch (err) {
    console.error('更新题单失败', err);
  }
};

// 删除题单
const deleteProblemsets = async () => {
  const ids = prompt('请输入要删除的题单ID，用逗号分隔');
  if (!ids) return;
  const idList = ids.split(',').map(id => parseInt(id.trim()));
  try {
    const res = await axios.delete('/problemsets/', { data: { ids: idList } });
    alert(`删除完成，成功: ${res.data.deleted}, 失败: ${res.data.failed.length}`);
    fetchProblemsets();
  } catch (err) {
    console.error('删除题单失败', err);
  }
};

onMounted(() => {
  fetchProblemsets();
});

const handlePageChange = (newPage) => {
  page.value = newPage;
  fetchProblemsets();
};
</script>

<template>
  <div>
    <h2>题单管理测试页</h2>

    <div style="margin-bottom: 1em; border: 1px solid #ccc; padding: 8px;">
      <h3>创建 / 更新题单</h3>
      <div>
        <label>ID(更新用)：<input v-model="form.id" /></label><br />
        <label>标题：<input v-model="form.title" /></label><br />
        <label>描述：<input v-model="form.description" /></label><br />
        <label>课程ID：<input v-model="form.course_id" /></label><br />
        <label>Legacy题ID(逗号分隔)：<input v-model="form.legacy_problem_ids" /></label><br />
        <label>Coding题ID(逗号分隔)：<input v-model="form.coding_problem_ids" /></label><br />
        <button @click="createProblemset">创建题单</button>
        <button @click="updateProblemset">更新题单</button>
      </div>
    </div>

    <div style="margin-bottom: 1em;">
      <button @click="deleteProblemsets">批量删除题单</button>
    </div>

    <div>
      <h3>题单列表</h3>
      <input v-model="courseId" placeholder="课程ID过滤(可选)" />
      <button @click="fetchProblemsets">筛选</button>
      <table border="1" cellpadding="4">
        <thead>
          <tr>
            <th>ID</th>
            <th>标题</th>
            <th>描述</th>
            <th>课程</th>
            <th>Legacy 题数</th>
            <th>Coding 题数</th>
            <th>更新时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ps in problemsets" :key="ps.id">
            <td>{{ ps.id }}</td>
            <td>{{ ps.title }}</td>
            <td>{{ ps.description }}</td>
            <td>{{ ps.course?.title || '-' }}</td>
            <td>{{ ps.num_legacy_problems }}</td>
            <td>{{ ps.num_coding_problems }}</td>
            <td>{{ ps.timestamp }}</td>
            <td>
              <button @click="fetchProblemsetDetail(ps.id)">查看详情</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div style="margin-top: 0.5em;">
        <button :disabled="page === 1" @click="handlePageChange(page - 1)">上一页</button>
        <span>第 {{ page }} 页</span>
        <button :disabled="page * perPage >= total" @click="handlePageChange(page + 1)">下一页</button>
      </div>
    </div>
  </div>
</template>
