<script setup>
import { ref } from 'vue'

const timeRange = ref([]) // [开始时间, 结束时间]
</script>

<template>
  <el-form>
    <el-form-item label="题单时间">
      <el-date-picker
        v-model="timeRange"
        type="datetimerange"
        start-placeholder="开始时间"
        end-placeholder="结束时间"
        format="YYYY-MM-DD HH:mm:ss"
        value-format="YYYY-MM-DD HH:mm:ss"
      >
      </el-date-picker>
    </el-form-item>
  </el-form>
</template>
