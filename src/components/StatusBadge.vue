<script setup>
const props = defineProps({
  status: { type: String, required: true },
  score: { type: Number, default: null }
})

const colors = {
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
}

const statusMap = {
  Pending: "排队中",
  Judging: "运行中",
  AC: "正确",
  WA: "答案错误",
  CE: "编译错误",
  TLE: "时间超限",
  MLE: "内存超限",
  OLE: "输出超限",
  RE: "运行错误",
  IE: "内部错误",
}
</script>

<template>
  <span
    class="px-2 py-1 text-xs font-medium rounded inline-block"
    :class="colors[props.status] || 'bg-gray-100 text-gray-500'"
  >
    {{ statusMap[props.status] || props.status }}
    <template v-if="['WA','TLE','MLE','OLE','RE'].includes(props.status) && props.score !== null">
      得分: {{ props.score }}
    </template>
  </span>
</template>
