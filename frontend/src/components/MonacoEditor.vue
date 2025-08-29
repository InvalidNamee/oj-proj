<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as monaco from 'monaco-editor'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({ language: 'python', code: '' })
  },
  readonly: { type: Boolean, default: false },
  height: { type: String, default: '300px' }, // 支持 'auto'
  maxHeight: { type: String, default: '600px' }, // 仅 auto 时生效
  minHeight: { type: String, default: '100px' }
})

const emit = defineEmits(['update:modelValue'])
const editorContainer = ref(null)
let editorInstance = null

const supportedLanguages = { python: 'python', cpp: 'cpp', java: 'java' }

const adjustHeight = () => {
  if (!editorInstance || !editorContainer.value) return
  if (props.height === 'auto') {
    const contentHeight = Math.min(
      Math.max(editorInstance.getContentHeight(), parseInt(props.minHeight)),
      parseInt(props.maxHeight)
    )
    editorContainer.value.style.height = `${contentHeight}px`
    editorInstance.layout()
  } else {
    editorContainer.value.style.height = props.height
  }
}

const createEditor = () => {
  if (!editorContainer.value) return

  editorInstance = monaco.editor.create(editorContainer.value, {
    value: props.modelValue.code,
    language: supportedLanguages[props.modelValue.language] || 'python',
    readOnly: props.readonly,
    theme: 'vs',
    automaticLayout: true,
    tabSize: 4,
    insertSpaces: true,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    lineNumbers: 'on',
  })

  editorInstance.onDidChangeModelContent(() => {
    emit('update:modelValue', {
      language: props.modelValue.language,
      code: editorInstance.getValue()
    })
    nextTick(adjustHeight)
  })

  nextTick(adjustHeight)
}

watch(
  () => props.modelValue,
  (newVal) => {
    if (!editorInstance) return
    if (editorInstance.getValue() !== newVal.code) {
      editorInstance.setValue(newVal.code)
    }
    const lang = supportedLanguages[newVal.language] || 'python'
    monaco.editor.setModelLanguage(editorInstance.getModel(), lang)
    nextTick(adjustHeight)
  },
  { deep: true }
)

watch(
  () => props.readonly,
  (val) => {
    if (editorInstance) editorInstance.updateOptions({ readOnly: val })
  }
)

watch(
  () => props.height,
  () => nextTick(adjustHeight)
)

onMounted(createEditor)
onBeforeUnmount(() => {
  if (editorInstance) editorInstance.dispose()
})
</script>

<template>
  <div>
    <div v-if="!readonly" class="language-selector">
      <label>语言: </label>
      <select v-model="modelValue.language" @change="$emit('update:modelValue', { ...modelValue })">
        <option value="python">Python</option>
        <option value="cpp">C++</option>
        <option value="java">Java</option>
      </select>
    </div>
    <div ref="editorContainer" class="monaco-editor-container"></div>
  </div>
</template>

<style scoped>
.monaco-editor-container {
  border: 1px solid #d1d5db;
  border-radius: 6px;
  overflow: hidden;
}
.language-selector {
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.language-selector label {
  font-weight: 500;
  color: #374151;
}

.language-selector select {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: white;
  font-size: 14px;
  color: #374151;
  transition: all 0.2s ease;
  cursor: pointer;
  outline: none;
}

.language-selector select:hover {
  border-color: #9ca3af;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.language-selector select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}
</style>
