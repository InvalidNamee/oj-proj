<template>
  <div class="submission-panel">
    <h2>代码题提交</h2>

    <div class="form-group">
      <label>Problem ID: <input v-model.number="problemId" type="number" /></label>
    </div>

    <div class="form-group">
      <label>语言:
        <select v-model="language">
          <option value="cpp">C++</option>
          <option value="python">Python</option>
        </select>
      </label>
    </div>

    <div class="form-group">
      <label>源码:</label>
      <textarea v-model="sourceCode" rows="10" cols="60"></textarea>
    </div>

    <button @click="submitCode" :disabled="submitting">提交代码</button>

    <h3>判题状态: {{ status }}</h3>
    <h3>详细信息:</h3>
    <pre class="log">{{ log }}</pre>
  </div>
</template>

<script setup>
import { ref } from "vue";

const problemId = ref(1002);
const language = ref("cpp");
const sourceCode = ref("// 在这里输入代码");
const status = ref("未提交");
const log = ref("");
const submitting = ref(false);
const submissionId = ref(null);

function appendLog(msg) {
  log.value += msg + "\n";
}

async function submitCode() {
  if (!sourceCode.value) {
    alert("请输入源码");
    return;
  }

  submitting.value = true;
  status.value = "提交中...";
  appendLog("正在提交代码...");

  try {
    // 1. 提交代码
    const resp = await fetch(`http://121.249.151.214/submissions/coding/${problemId.value}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        language: language.value,
        source_code: sourceCode.value,
      }),
    });

    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || "提交失败");
    submissionId.value = data.submission_id;

    status.value = "排队中";
    appendLog(`提交成功, Submission ID: ${submissionId.value}`);

    // 2. 轮询
    let finished = false;
    while (!finished) {
      await new Promise(resolve => setTimeout(resolve, 1000)); // 1 秒轮询
      const pollResp = await fetch(`http://121.249.151.214/submissions/${submissionId.value}`);
      const pollData = await pollResp.json();
      status.value = pollData.status;
      if (pollData.extra) {
        try {
          const extra = JSON.parse(pollData.extra);
          appendLog(JSON.stringify(extra, null, 2));
        } catch {
          appendLog(pollData.extra);
        }
      }
      finished = !["queued", "running"].includes(pollData.status);
    }

    appendLog("判题完成");
  } catch (e) {
    appendLog(`错误: ${e.message}`);
    status.value = "提交失败";
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.submission-panel { max-width: 700px; margin: 0 auto; font-family: sans-serif; }
.form-group { margin-bottom: 10px; }
textarea { width: 100%; font-family: monospace; }
.log { background: #f4f4f4; padding: 10px; border: 1px solid #ddd; max-height: 300px; overflow-y: auto; }
button:disabled { opacity: 0.5; }
</style>
