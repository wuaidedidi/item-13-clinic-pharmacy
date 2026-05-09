<template>
  <div>
    <PageHeader title="批次入库管理" description="查看每个批次的剩余库存、效期、货位和入库来源。">
      <el-button type="primary" :icon="Plus" @click="$router.push('/inbounds')">新增入库</el-button>
    </PageHeader>
    <ToolbarCard>
      <el-table :data="rows" stripe class="business-table" v-loading="loading">
        <el-table-column prop="medicineName" label="药品名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="batchNo" label="批号" min-width="120" />
        <el-table-column prop="inboundOrderNo" label="入库单号" min-width="160" />
        <el-table-column prop="quantity" label="入库数量" width="100" />
        <el-table-column prop="remainingQuantity" label="剩余数量" width="100" />
        <el-table-column prop="productionDate" label="生产日期" width="120" />
        <el-table-column prop="expiryDate" label="有效期至" width="120" />
        <el-table-column label="剩余天数" width="110">
          <template #default="{ row }"><el-tag :type="daysType(row.expiryDate)">{{ daysLeft(row.expiryDate) }} 天</el-tag></template>
        </el-table-column>
        <el-table-column prop="location" label="货位" width="100" />
        <el-table-column label="状态" width="90"><template #default="{ row }"><StatusTag :value="row.status" /></template></el-table-column>
      </el-table>
    </ToolbarCard>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'
import ToolbarCard from '../components/ToolbarCard.vue'
import StatusTag from '../components/StatusTag.vue'
import { api } from '../api'

const rows = ref([])
const loading = ref(false)
function daysLeft(date) { return Math.ceil((new Date(date) - new Date()) / 86400000) }
function daysType(date) {
  const days = daysLeft(date)
  if (days <= 30) return 'danger'
  if (days <= 60) return 'warning'
  return 'success'
}
async function loadData() {
  loading.value = true
  try { rows.value = await api.batches() } finally { loading.value = false }
}
onMounted(loadData)
</script>
