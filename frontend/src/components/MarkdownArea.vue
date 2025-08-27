<script setup>
import { ref, watch } from 'vue'
import MarkdownIt from 'markdown-it'
import markdownItKatex from 'markdown-it-katex'
import 'katex/dist/katex.min.css'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  renderHtml: {
    type: Boolean,
    default: false // 是否允许渲染 HTML
  }
})

const renderedHtml = ref('')

// 初始化 markdown-it
const md = new MarkdownIt({
  html: props.renderHtml,
  linkify: true,
  typographer: true
}).use(markdownItKatex)

// 监听 modelValue 更新
watch(() => props.modelValue, (val) => {
  renderedHtml.value = md.render(val || '')
}, { immediate: true })
</script>

<template>
  <div class="markdown-area" v-html="renderedHtml"></div>
</template>

<style scoped>
.markdown-area {
  overflow-wrap: break-word;
}
</style>
