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
  const res = await axios.get(`/api/problems/${problemId}`);
  testCasesList.value = res.data.test_cases?.cases || [];
};

const deleteSelectedCases = async () => {
  if (!selectedTestCases.value.length) return;
  try {
    await axios.patch(`/api/problems/${problemId}/test_cases/delete`, {
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
    await axios.patch(`/api/problems/${problemId}/test_cases/add`, form);
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

// 下载测试用例
const downloadTestCases = async () => {
  try {
    const response = await axios.get(`/api/problems/${problemId}/test_cases/download`, {
      responseType: 'blob'
    });
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `test_cases_${problemId}.zip`);
    document.body.appendChild(link);
    link.click();
    
    // 清理
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert(err.response?.data?.error || "下载失败");
  }
};

onMounted(fetchProblem);
</script>

<template>
  <div class="edit-test-cases-container">
    <h2 class="edit-test-cases-title">管理测试用例</h2>
    <button @click="downloadTestCases" class="edit-test-cases-download-button">
      下载测试用例
    </button>

    <!-- 已有测试用例 -->
    <div v-if="testCasesList.length">
      <label class="edit-test-cases-label">已有测试用例</label>
      <div class="edit-test-cases-list">
        <label v-for="(tc, idx) in testCasesList" :key="idx" class="edit-test-cases-item">
          <input type="checkbox" v-model="selectedTestCases" :value="tc.name"
            class="edit-test-cases-checkbox" />
          <span>{{ tc.name }} ({{ tc.in }} → {{ tc.out }})</span>
        </label>
      </div>
      <button @click="deleteSelectedCases" class="edit-test-cases-delete-button">
        删除选中
      </button>
    </div>

    <!-- 上传新测试用例 -->
    <div class="mt-4">
      <label class="edit-test-cases-upload-label">上传新的测试用例 (zip)</label>
      <input type="file" @change="handleFileChange" accept=".zip"
        class="edit-test-cases-file-input" />
      <button @click="uploadNewTestCases"
              :disabled="uploading"
              class="edit-test-cases-upload-button"
              :class="uploading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600'">
        {{ uploading ? '上传中…' : '上传测试用例' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.edit-test-cases-container {
  border: 1px solid #e2e8f0; /* 柔和边框 */
  background-color: #ffffff; /* 白色背景 */
  max-width: 800px; /* 限制容器宽度 */
  margin: 20px auto; /* 居中显示 */
  padding: 30px; /* 内边距 */
  border-radius: 12px; /* 圆角 */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); /* 阴影效果 */
}

.edit-test-cases-title {
  color: #1a202c;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 24px;
  text-align: center;
  position: relative;
}

.edit-test-cases-title::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #4f46e5, #7c3aed);
  border-radius: 2px;
}

.edit-test-cases-download-button {
  background-color: #4CAF50; /* 绿色 */
  border: none;
  color: white;
  padding: 12px 24px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 6px;
  transition: background-color 0.3s ease;
}

.edit-test-cases-download-button:hover {
  background-color: #45a049;
}

.edit-test-cases-label {
  display: block;
  font-weight: 600;
  margin: 20px 0 10px;
  color: #4a5568;
}

.edit-test-cases-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 15px;
  background-color: #f8fafc;
}

.edit-test-cases-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #edf2f7;
}

.edit-test-cases-item:last-child {
  border-bottom: none;
}

.edit-test-cases-checkbox {
  margin-right: 10px;
  width: 16px;
  height: 16px;
}

.edit-test-cases-delete-button {
  background-color: #e53e3e;
  color: white;
  border: none;
  padding: 12px 40px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 10px;
  transition: background-color 0.3s ease;
  font-size: 16px;
  text-align: center;
  display: inline-block;
}

.edit-test-cases-delete-button:hover {
  background-color: #c53030;
}

.edit-test-cases-upload-label {
  display: block;
  font-weight: 600;
  margin: 20px 0 10px;
  color: #4a5568;
}

.edit-test-cases-file-input {
  display: block;
  margin: 10px 0;
  padding: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  width: 100%;
  box-sizing: border-box;
}

.edit-test-cases-upload-button {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  text-align: center;
  display: inline-block;
}

.edit-test-cases-upload-button:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}

.edit-test-cases-upload-button:not(:disabled) {
  background-color: #4299e1;
}

.edit-test-cases-upload-button:not(:disabled):hover {
  background-color: #3182ce;
}
</style>
