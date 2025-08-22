<template>
  <div class="editor-container">
    <Codemirror v-model="code" :extensions="extensions" class="editor" />

    <div class="controls">
      <label>
        语言：
        <select v-model="language" @change="updateLanguage">
          <option value="cpp">C++</option>
          <option value="c">C</option>
          <option value="python">Python</option>
        </select>
      </label>
      <button @click="runCode">运行代码</button>
    </div>

    <pre class="output">{{ output }}</pre>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Codemirror } from 'vue-codemirror'

// CodeMirror 核心模块
import { keymap } from '@codemirror/view'
import { defaultKeymap } from '@codemirror/commands'

// 语言模式
import { cpp } from '@codemirror/lang-cpp'
import { python } from '@codemirror/lang-python'

// 响应式代码
const code = ref(``)

// 当前语言
const language = ref('cpp')

// 输出面板
const output = ref('')

// 编辑器扩展
const extensions = ref([
  cpp(),
  keymap.of(defaultKeymap)
])

// 切换语言
function updateLanguage() {
  if (language.value === 'python') {
    extensions.value = [python(), keymap.of(defaultKeymap)]
  } else {
    extensions.value = [cpp(), keymap.of(defaultKeymap)]
  }
}

// 模拟运行代码
function runCode() {
  if (language.value === 'python') {
    output.value = 'Python 代码运行模拟结果'
  } else {
    output.value = 'C/C++ 代码运行模拟结果'
  }
}
</script>

<style scoped>
.editor-container {
  display: flex;
  flex-direction: column;
  height: 600px;
  width: 100%;
  border: 1px solid #333;
}

.editor {
  flex: 1;
  border-bottom: 1px solid #555;
}

.controls {
  margin: 8px 0;
  display: flex;
  gap: 16px;
  align-items: center;
}

.output {
  /* background: #1e1e1e; */
  /* color: #d4d4d4; */
  padding: 8px;
  height: 150px;
  overflow: auto;
}
</style>
