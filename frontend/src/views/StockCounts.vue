<template>
  <div>
    <PageHeader title="库存盘点管理" description="记录实盘数量，系统自动生成差异调整单，由管理员确认后生效。">
      <el-button type="primary" :icon="Plus" @click="openDialog">新增盘点</el-button>
    </PageHeader>
    <div class="split-grid">
      <ToolbarCard>
        <h2>盘点记录</h2>
        <el-table :data="counts" stripe class="business-table" v-loading="loading">
          <el-table-column prop="countNo" label="盘点单号" min-width="150" />
          <el-table-column prop="medicineName" label="药品名称" min-width="140" />
          <el-table-column prop="systemQuantity" label="账面" width="80" />
          <el-table-column prop="countedQuantity" label="实盘" width="80" />
          <el-table-column prop="differenceQty" label="差异" width="80" />
          <el-table-column prop="countedBy" label="盘点人" width="100" />
          <el-table-column label="状态" width="90"><template #default="{ row }"><StatusTag :value="row.status" /></template></el-table-column>
        </el-table>
      </ToolbarCard>
      <ToolbarCard>
        <h2>调整单确认</h2>
        <el-table :data="adjustments" stripe class="business-table" v-loading="loading">
          <el-table-column prop="orderNo" label="调整单号" min-width="150" />
          <el-table-column prop="medicineName" label="药品" min-width="120" />
          <el-table-column prop="differenceQty" label="差异" width="80" />
          <el-table-column label="状态" width="90"><template #default="{ row }"><StatusTag :value="row.status" /></template></el-table-column>
          <el-table-column label="操作" width="110" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="primary" :disabled="row.status !== 'pending'" @click="approve(row)">确认</el-button>
            </template>
          </el-table-column>
        </el-table>
      </ToolbarCard>
    </div>
    <el-dialog v-model="visible" title="新增库存盘点" width="620px" class="form-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="two-col-form">
        <el-form-item label="盘点药品" prop="medicine_id">
          <el-select v-model="form.medicine_id" filterable placeholder="请选择药品">
            <el-option v-for="item in medicines" :key="item.id" :label="`${item.name} 账面${item.currentStock}`" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="实盘数量" prop="counted_quantity"><el-input-number v-model="form.counted_quantity" :min="0" /></el-form-item>
        <el-form-item label="盘点人" prop="counted_by"><el-input v-model.trim="form.counted_by" /></el-form-item>
        <el-form-item label="备注" prop="remark"><el-input v-model.trim="form.remark" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">提交盘点</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import PageHeader from '../components/PageHeader.vue'
import ToolbarCard from '../components/ToolbarCard.vue'
import StatusTag from '../components/StatusTag.vue'
import { api } from '../api'

const counts = ref([])
const adjustments = ref([])
const medicines = ref([])
const loading = ref(false)
const saving = ref(false)
const visible = ref(false)
const formRef = ref()
const form = reactive({ medicine_id: null, counted_quantity: 0, counted_by: '药房管理员', remark: '' })
const rules = {
  medicine_id: [{ required: true, message: '请选择盘点药品', trigger: 'change' }],
  counted_by: [{ required: true, message: '请输入盘点人', trigger: 'blur' }]
}
async function loadData() {
  loading.value = true
  try { ;[counts.value, adjustments.value, medicines.value] = await Promise.all([api.stockCounts(), api.adjustments(), api.medicines()]) } finally { loading.value = false }
}
function openDialog() { Object.assign(form, { medicine_id: null, counted_quantity: 0, counted_by: '药房管理员', remark: '' }); visible.value = true }
async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    await api.createStockCount(form)
    ElMessage.success('盘点提交成功')
    visible.value = false
    await loadData()
  } catch (error) {} finally { saving.value = false }
}
async function approve(row) {
  try {
    await api.approveAdjustment(row.id)
    ElMessage.success('调整单已确认')
    await loadData()
  } catch (error) {}
}
onMounted(loadData)
</script>
