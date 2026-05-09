<template>
  <div>
    <PageHeader title="效期预警管理" description="持续跟踪近效期批次，帮助药房优先处置高风险库存。" />
    <ToolbarCard>
      <el-table :data="rows" stripe class="business-table" v-loading="loading">
        <el-table-column prop="medicineName" label="药品名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="specification" label="规格" min-width="130" />
        <el-table-column prop="batchNo" label="批号" min-width="120" />
        <el-table-column prop="remainingQuantity" label="剩余数量" width="100" />
        <el-table-column prop="expiryDate" label="有效期至" width="120" />
        <el-table-column label="风险等级" width="110">
          <template #default="{ row }"><el-tag :type="levelType(row.level)">{{ levelText(row.level) }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="daysLeft" label="剩余天数" width="110" />
        <el-table-column prop="location" label="货位" width="120" />
      </el-table>
    </ToolbarCard>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import PageHeader from '../components/PageHeader.vue'
import ToolbarCard from '../components/ToolbarCard.vue'
import { api } from '../api'

const rows = ref([])
const loading = ref(false)
function levelType(level) { return { critical: 'danger', high: 'danger', medium: 'warning', info: 'success' }[level] || 'info' }
function levelText(level) { return { critical: '已过期', high: '高风险', medium: '中风险', info: '关注' }[level] || '关注' }
async function loadData() {
  loading.value = true
  try { rows.value = await api.warnings() } finally { loading.value = false }
}
onMounted(loadData)
</script>
