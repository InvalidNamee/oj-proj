<script setup>
import '@/assets/components.css'
import { ref, watch } from 'vue'

const props = defineProps({
  problemData: { type: Object, required: true }
})
const emit = defineEmits(['update:modelValue'])

const problemType = ref('single')
const options = ref([])
const answers = ref(null)  // 单选存值，多选存数组

// 初始化数据
const initData = (data) => {
  problemType.value = data?.type || 'single'
  if (problemType.value === 'single') {
    answers.value = data?.user_answer ?? null
    options.value = data?.test_cases?.options || []
  } else if (problemType.value === 'multiple') {
    answers.value = Array.isArray(data?.user_answer) ? [...data.user_answer] : []
    options.value = data?.test_cases?.options || []
  } else if (problemType.value === 'fill') {
    answers.value = Array.isArray(data?.user_answer) ? [...data.user_answer] : []
  } else {
    answers.value = data?.user_answer || ''
  }
}

// watch problemData
watch(() => props.problemData, (data) => initData(data), { immediate: true, deep: true })

// 单选/多选操作
const toggleOption = (id) => {
  if (problemType.value === 'single') {
    answers.value = id
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
  if (problemType.value === 'single') {
    answers.value = null
  } else if (problemType.value === 'multiple') {
    answers.value = []
  } else if (problemType.value === 'fill') {
    answers.value = []
  } else {
    answers.value = ''
  }
}

// watch answers 变化
watch(answers, () => {
  emit('update:modelValue', answers.value)
}, { deep: true })
</script>

<template>
  <div class="legacy-answer-area-container">
    <div class="legacy-answer-area-header">
      <button @click="clearAnswers" class="legacy-answer-area-clear-button">
        清空
      </button>
    </div>

    <!-- 单选题 -->
    <div v-if="problemType === 'single' && options.length">
      <div v-for="opt in options" :key="opt.id" class="legacy-answer-area-option-item">
        <input
          type="radio"
          :value="opt.id"
          :checked="answers === opt.id"
          @change="toggleOption(opt.id)"
        />
        <span>{{ opt.content }}</span>
      </div>
    </div>

    <!-- 多选题 -->
    <div v-else-if="problemType === 'multiple' && options.length">
      <div v-for="opt in options" :key="opt.id" class="legacy-answer-area-option-item">
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
      <div v-for="(ans, idx) in answers" :key="idx" class="legacy-answer-area-fill-item">
        <input
          v-model="answers[idx]"
          placeholder="填空答案"
          class="legacy-answer-area-fill-input"
        />
        <button @click="removeFillAnswer(idx)" class="legacy-answer-area-delete-button">删除</button>
      </div>
      <button @click="addFillAnswer" class="legacy-answer-area-add-button">添加填空</button>
    </div>

    <!-- 主观题 -->
    <div v-else>
      <textarea
        v-model="answers"
        rows="6"
        placeholder="请输入答案"
        class="legacy-answer-area-textarea"
      ></textarea>
    </div>
  </div>
</template>
