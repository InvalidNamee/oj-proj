<template>
  <div class="prose" v-html="markdownContent" />
</template>

<script>
import { marked } from "marked";
import katex from "katex";
import "katex/dist/katex.min.css";

import hljs from "highlight.js";
import "highlight.js/styles/github-dark.css"; // 可以换你喜欢的主题

export default {
  name: "MarkdownArea",
  props: {
    markdown: {
      type: String,
      required: true,
    },
  },
  computed: {
    markdownContent() {
      // 数学公式替换
      let formula = this.markdown
        .replace(/\$\$(.+?)\$\$/gs, (_, equation) => {
          return (
            "<katex-formula-ml>" +
            katex.renderToString(equation, { throwOnError: false }) +
            "</katex-formula-ml>"
          );
        })
        .replace(/\$(.+?)\$/g, (_, equation) => {
          return (
            "<katex-formula>" +
            katex.renderToString(equation, { throwOnError: false }) +
            "</katex-formula>"
          );
        });

      return marked(formula);
    },
  },
};
</script>

<script setup>
import { marked } from "marked";
import hljs from "highlight.js";

const renderer = new marked.Renderer();

// 代码高亮 + 复制按钮
renderer.code = ({ text, lang }) => {
  let highlighted;
  if (lang && hljs.getLanguage(lang)) {
    highlighted = hljs.highlight(text, { language: lang }).value;
  } else {
    highlighted = hljs.highlightAuto(text).value;
    lang = "text";
  }
  // 加一个复制按钮
  return `
    <pre class="code-block relative group">
      <button class="copy-btn absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition"
        onclick="navigator.clipboard.writeText(\`${text.replace(/`/g, "\\`")}\`)">
        📋
      </button>
      <code class="hljs ${lang}">${highlighted}</code>
    </pre>
  `;
};

marked.setOptions({
  renderer: renderer,
  gfm: true,
  breaks: true,
  smartLists: true,
});
</script>
