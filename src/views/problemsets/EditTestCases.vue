<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";

const route = useRoute();
const problemId = route.params.id;

const testCasesList = ref([]);
const selectedTestCases = ref([]);
const newTestCases = ref(null);
const uploading = ref(false); // 上传状态

const fetchProblem = async () => {
  const res = await axios.get(`/api/coding_problems/${problemId}`);
  testCasesList.value = res.data.test_cases?.cases || [];
};

const deleteSelectedCases = async () => {
  if (!selectedTestCases.value.length) return;
  try {
    await axios.patch(`/api/coding_problems/${problemId}/test_cases/delete`, {
      cases: testCasesList.value.filter(tc => selectedTestCases.value.includes(tc.name))
    });
    testCasesList.value = testCasesList.value.filter(tc => !selectedTestCases.value.includes(tc.name));
    selectedTestCases.value = [];
  } catch (err) {
    alert(err.response?.data?.error || "删除失败");
  }
};

const uploadNewTestCases = async () => {  
  if (!newTestCases.value) return;
  try {
    uploading.value = true; // 开始上传
    const form = new FormData();
    form.append("test_cases.zip", newTestCases.value);
    await axios.patch(`/api/coding_problems/${problemId}/test_cases/add`, form);
    await fetchProblem();
    newTestCases.value = null;
  } catch (err) {
    alert(err.response?.data?.error || "上传失败");
  } finally {
    uploading.value = false; // 上传结束
  }
};

const handleFileChange = (e) => {
  newTestCases.value = e.target.files[0];
};

onMounted(fetchProblem);
</script>

<template>
  <div class="max-w-2xl mx-auto mt-12 p-6 rounded-xl bg-white shadow">
    <h2 class="text-2xl font-bold mb-6">管理测试用例</h2>

    <!-- 已有测试用例 -->
    <div v-if="testCasesList.length">
      <label class="block mb-1 font-semibold">已有测试用例</label>
      <div class="space-y-1 max-h-48 overflow-auto border border-gray-300 rounded p-2">
        <label v-for="(tc, idx) in testCasesList" :key="idx" class="flex items-center space-x-2">
          <input type="checkbox" v-model="selectedTestCases" :value="tc.name"
            class="w-4 h-4 border-gray-300 rounded focus:ring-2 focus:ring-blue-400" />
          <span>{{ tc.name }} ({{ tc.in }} → {{ tc.out }})</span>
        </label>
      </div>
      <button @click="deleteSelectedCases" class="mt-2 w-full bg-red-500 text-white px-3 py-2 rounded hover:bg-red-600">
        删除选中
      </button>
    </div>

    <!-- 上传新测试用例 -->
    <div class="mt-4">
      <label class="block mb-1">上传新的测试用例 (zip)</label>
      <input type="file" @change="handleFileChange" accept=".zip"
        class="w-full border border-gray-300 rounded px-3 py-2 text-gray-700" />
      <button @click="uploadNewTestCases"
              :disabled="uploading"
              class="mt-2 w-full px-3 py-2 rounded text-white"
              :class="uploading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600'">
        {{ uploading ? '上传中…' : '上传测试用例' }}
      </button>
    </div>
  </div>
</template>
