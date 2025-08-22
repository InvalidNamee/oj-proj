<template>
  <div class="p-4 space-y-6">
    <h2 class="text-xl font-bold">传统题测试面板</h2>

    <!-- 提交传统题 -->
    <div class="space-y-2 p-4 border rounded">
      <h3 class="font-semibold">提交传统题</h3>
      <label>Problem ID:
        <input v-model.number="submitForm.problem_id" type="number" class="border px-2" />
      </label>
      <label>Problem Set ID:
        <input v-model.number="submitForm.problem_set_id" type="number" class="border px-2" />
      </label>
      <label>语言:
        <select v-model="submitForm.language" class="border px-2">
          <option value="cpp">C++</option>
          <option value="c">C</option>
          <option value="python">Python</option>
        </select>
      </label>
      <textarea v-model="submitForm.user_answer" rows="6" class="w-full border px-2"></textarea>
      <button @click="submitLegacy" class="px-3 py-1 bg-blue-500 text-white rounded">提交</button>
    </div>

    <!-- 查询提交记录列表 -->
    <div class="space-y-2 p-4 border rounded">
      <h3 class="font-semibold">提交记录列表</h3>
      <button @click="fetchSubmissions" class="px-3 py-1 bg-green-500 text-white rounded">刷新记录</button>
      <ul>
        <li v-for="s in submissions" :key="s.id" class="cursor-pointer hover:underline"
            @click="fetchSubmissionDetail(s.submission_id)">
          #{{ s.submission_id }} - Problem {{ s.problem_id }} - 状态: {{ s.status }} - 得分 {{ s.score }}
        </li>
      </ul>
    </div>

    <!-- 查询提交详情 -->
    <div class="space-y-2 p-4 border rounded" v-if="submissionDetail">
      <h3 class="font-semibold">提交详情 #{{ submissionDetail.submission_id }}</h3>
      <p>题目 ID: {{ submissionDetail.problem_id }}</p>
      <p>题单 ID: {{ submissionDetail.problem_set_id }}</p>
      <p>状态: {{ submissionDetail.status }}</p>
      <p>得分: {{ submissionDetail.score }}</p>
      <p>extra: {{ submissionDetail.extra }}</p>
      <h4 class="font-semibold mt-2">代码:</h4>
      <pre class="bg-gray-100 p-2 rounded text-sm">{{ submissionDetail.user_answer }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";

const submitForm = ref({
  problem_id: 1,
  problem_set_id: 1,
  language: "cpp",
  user_answer: "#include <bits/stdc++.h>\nusing namespace std;\nint main(){cout<<42;}"
});

const submissions = ref([]);
const submissionDetail = ref(null);

// 提交传统题
const submitLegacy = async () => {
  try {
    const res = await axios.post(`/submissions/legacy/${11}`, submitForm.value);
    alert("提交成功, 提交 ID: " + res.data.submission_id);
  } catch (err) {
    console.error(err);
    alert("提交失败");
  }
};

// 查询提交记录列表
const fetchSubmissions = async () => {
  try {
    const res = await axios.get("/submissions/");
    submissions.value = res.data.items;
  } catch (err) {
    console.error(err);
  }
};

// 查询提交详情
const fetchSubmissionDetail = async (id) => {
  try {
    const res = await axios.get(`/submissions/${id}`);
    submissionDetail.value = res.data;
  } catch (err) {
    console.error(err);
  }
};
</script>
