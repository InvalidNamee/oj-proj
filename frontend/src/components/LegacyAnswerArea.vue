<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  problemData: { type: Object, required: true } // 父组件传入的题目数据
})
const emit = defineEmits(['update:modelValue'])

const problemType = ref('single')
const options = ref([]) // 单选/多选选项
const answers = ref([]) // 答案

// 初始化数据
const initData = (data) => {
  problemType.value = data?.type || 'single'
  if (problemType.value === 'single' || problemType.value === 'multiple') {
    options.value = data?.test_cases?.options || []
    if (Array.isArray(data?.user_answer)) {
      answers.value = [...data.user_answer]
    } else if (data?.user_answer != null) {
      answers.value = [data.user_answer]
    } else {
      answers.value = []
    }
  } else if (problemType.value === 'fill') {
    answers.value = Array.isArray(data?.user_answer) ? [...data.user_answer] : []
  } else {
    answers.value = data?.user_answer || ''
  }
}

// watch problemData
watch(
  () => props.problemData,
  (data) => initData(data),
  { immediate: true, deep: true }
)

// 单选/多选操作
const toggleOption = (id) => {
  if (problemType.value === 'single') {
    answers.value = [id]
  } else if (problemType.value === 'multiple') {
    if (answers.value.includes(id)) {
      answers.value = answers.value.filter(a => a !== id)
    } else {
      answers.value.push(id)
    }
  }
}

// 填空题操作
const updateFillAnswer = (index, value) => {
  answers.value[index] = value
}
const addFillAnswer = () => {
  answers.value.push('')
}
const removeFillAnswer = (index) => {
  answers.value.splice(index, 1)
}

// 清空答案
const clearAnswers = () => {
  if (problemType.value === 'single' || problemType.value === 'multiple') {
    answers.value = []
  } else if (problemType.value === 'fill') {
    answers.value = []
  } else {
    answers.value = ''
  }
}

// watch answers 变化
watch(
  answers,
  () => {
    emit('update:modelValue', answers.value)
  },
  { deep: true }
)
</script>

<template>
  <div class="space-y-4 mt-4">
    <div class="flex justify-end mb-2">
      <button @click="clearAnswers" class="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600">
        清空
      </button>
    </div>

    <!-- 单选题 -->
    <div v-if="problemType === 'single' && options.length">
      <div v-for="opt in options" :key="opt.id" class="flex items-center space-x-2">
        <input
          type="radio"
          :value="opt.id"
          :checked="answers.includes(opt.id)"
          @change="toggleOption(opt.id)"
        />
        <span>{{ opt.content }}</span>
      </div>
    </div>

    <!-- 多选题 -->
    <div v-else-if="problemType === 'multiple' && options.length">
      <div v-for="opt in options" :key="opt.id" class="flex items-center space-x-2">
        <input
          type="checkbox"
          :value="opt.id"
          :checked="answers.includes(opt.id)"
          @change="toggleOption(opt.id)"
        />
        <span>{{ opt.content }}</span>
      </div>
    </div>

    <!-- 填空题 -->
    <div v-else-if="problemType === 'fill'">
      <div v-for="(ans, idx) in answers" :key="idx" class="flex items-center space-x-2">
        <input
          v-model="answers[idx]"
          placeholder="填空答案"
          class="flex-1 border border-gray-300 rounded px-2 py-1"
        />
        <button @click="removeFillAnswer(idx)" class="text-red-500">删除</button>
      </div>
      <button @click="addFillAnswer" class="mt-2 bg-gray-200 px-2 py-1 rounded">添加填空</button>
    </div>

    <!-- 主观题 -->
    <div v-else>
      <textarea
        v-model="answers"
        rows="6"
        placeholder="请输入答案"
        class="w-full border border-gray-300 rounded px-3 py-2"
      ></textarea>
    </div>
  </div>
</template>
