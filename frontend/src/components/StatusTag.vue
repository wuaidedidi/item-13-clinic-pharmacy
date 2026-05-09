<template>
  <el-tag :type="tag.type" effect="light">{{ tag.label }}</el-tag>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ value: { type: String, default: '' } })
const map = {
  active: ['success', '启用'],
  enabled: ['success', '启用'],
  available: ['success', '可用'],
  completed: ['success', '已完成'],
  submitted: ['warning', '待确认'],
  pending: ['warning', '待审核'],
  approved: ['success', '已通过'],
  inactive: ['info', '停用'],
  disabled: ['info', '停用']
}
const tag = computed(() => {
  const item = map[props.value] || ['info', props.value || '-']
  return { type: item[0], label: item[1] }
})
</script>
