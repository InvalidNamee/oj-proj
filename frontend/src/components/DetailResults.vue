<script setup>
import { ref } from "vue";
import '@/assets/pr3.css';

const props = defineProps({
  results: {
    type: Object,
    required: true
  },
  colors: {
    type: Object,
    default: () => ({
      Pending: "bg-gray-200 text-gray-700",
      Judging: "bg-blue-200 text-blue-700",
      AC: "bg-green-200 text-green-700",
      WA: "bg-red-200 text-red-700",
      TLE: "bg-yellow-200 text-yellow-800",
      MLE: "bg-purple-200 text-purple-700",
      OLE: "bg-pink-200 text-pink-700",
      CE: "bg-orange-200 text-orange-700",
      RE: "bg-indigo-200 text-indigo-700",
      IE: "bg-black text-white",
    })
  }
});

const expanded = ref({}); // 用例展开状态

function toggle(id) {
  expanded.value[id] = !expanded.value[id];
}
</script>

<template>
  <div class="space-y-4">
    <!-- 总体状态 -->
    <div class="p-3 rounded" :class="colors[results.status]">
      <p class="font-semibold">自测总体状态: {{ results.status }}</p>
      <p v-if="results.score !== undefined">得分: {{ results.score }}</p>
    </div>

    <!-- 每个用例 -->
    <div v-for="r in results.result" :key="r.name" class="p-3 border rounded space-y-2">
      <div class="flex justify-between items-center">
        <div>
          <span>用例 {{ r.name }}</span>
          <span class="ml-2 px-2 py-1 rounded text-sm font-medium" :class="colors[r.status]">
            {{ r.status }}
          </span>
        </div>
        <button
          v-if="r.diff || r.message"
          @click="toggle(r.name)"
          class="text-blue-500 text-sm hover:underline"
        >
          {{ expanded[r.name] ? "收起" : "展开错误信息" }}
        </button>
      </div>

      <div v-if="expanded[r.name]" class="text-sm text-red-600 whitespace-pre-line">
        <p v-if="r.diff">Diff: {{ r.diff }}</p>
        <p v-if="r.message">Message: {{ r.message }}</p>
      </div>

      <div class="text-xs text-gray-600">
        <span v-if="r.time">时间: {{ r.time }} ms</span>
        <span v-if="r.memory" class="ml-2">内存: {{ r.memory }} KB</span>
      </div>
    </div>
  </div>
</template>
