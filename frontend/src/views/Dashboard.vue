<template>
  <div>
    <PageHeader title="药房看板" description="聚合近效期、库存、领用金额、缺货和采购待审，辅助药房每日巡检。" />
    <div class="metric-grid">
      <div v-for="item in metrics" :key="item.label" class="metric-card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <small>{{ item.hint }}</small>
      </div>
    </div>
    <div class="dashboard-grid">
      <ToolbarCard>
        <h2>近效期批次</h2>
        <div class="dense-list">
          <div v-for="item in summary.expiring_batches" :key="item.batchNo">
            <span>{{ item.medicineName }} / {{ item.batchNo }}</span>
            <strong>{{ item.daysLeft }} 天</strong>
          </div>
          <el-empty v-if="!summary.expiring_batches?.length" description="暂无近效期批次" />
        </div>
      </ToolbarCard>
      <ToolbarCard>
        <h2>缺货关注</h2>
        <div class="dense-list">
          <div v-for="item in summary.shortage_items" :key="item.medicineName">
            <span>{{ item.medicineName }} · {{ item.location }}</span>
            <strong>{{ item.currentStock }}/{{ item.safetyStock }}</strong>
          </div>
          <el-empty v-if="!summary.shortage_items?.length" description="暂无缺货风险" />
        </div>
      </ToolbarCard>
      <ToolbarCard>
        <h2>待确认调整单</h2>
        <div class="dense-list">
          <div v-for="item in summary.pending_adjustments" :key="item.orderNo">
            <span>{{ item.medicineName }} · {{ item.reason }}</span>
            <strong>{{ item.differenceQty }}</strong>
          </div>
          <el-empty v-if="!summary.pending_adjustments?.length" description="暂无待确认调整单" />
        </div>
      </ToolbarCard>
      <ToolbarCard>
        <h2>近期领用</h2>
        <div class="dense-list">
          <div v-for="item in summary.recent_issues" :key="item.issueNo">
            <span>{{ item.patientName }} · {{ item.doctorName }}</span>
            <strong>￥{{ item.totalAmount }}</strong>
          </div>
          <el-empty v-if="!summary.recent_issues?.length" description="暂无领用记录" />
        </div>
      </ToolbarCard>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import PageHeader from '../components/PageHeader.vue'
import ToolbarCard from '../components/ToolbarCard.vue'
import { api } from '../api'

const summary = ref({})
const metrics = computed(() => [
  { label: '近效期批次数', value: summary.value.expiring_batch_count ?? 0, hint: '按预警阈值滚动刷新' },
  { label: '库存周转率', value: summary.value.turnover_rate ?? 0, hint: '累计入库 / 当前库存' },
  { label: '今日领用金额', value: `￥${summary.value.today_issue_amount ?? 0}`, hint: '处方领用实时累加' },
  { label: '缺货药品数', value: summary.value.shortage_medicine_count ?? 0, hint: '低于安全库存' },
  { label: '采购待审数', value: summary.value.pending_purchase_count ?? 0, hint: '采购补货待处理' }
])

async function loadData() {
  summary.value = await api.dashboard()
}

onMounted(loadData)
</script>
