<script setup>
const props = defineProps({
  status: { type: String, required: true, default: 'Pending' },
  score: { type: Number, default: 0.0 }
})

const statusClasses = {
  Pending: "status-badge-pending",
  Judging: "status-badge-judging",
  AC: "status-badge-ac",
  WA: "status-badge-wa",
  TLE: "status-badge-tle",
  MLE: "status-badge-mle",
  OLE: "status-badge-ole",
  CE: "status-badge-ce",
  RE: "status-badge-re",
  IE: "status-badge-ie",
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
    class="status-badge"
    :class="statusClasses[props.status] || 'status-badge-default'"
  >
    {{ statusMap[props.status] || props.status }}
    <template v-if="['WA','TLE','MLE','OLE','RE'].includes(props.status) && props.score !== null">
      得分: {{ props.score }}
    </template>
  </span>
</template>
