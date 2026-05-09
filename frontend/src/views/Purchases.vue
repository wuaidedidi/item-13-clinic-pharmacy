<template>
  <div>
    <PageHeader title="采购补货管理" description="针对缺货和低库存药品创建补货申请，药房管理员或系统管理员审核。">
      <el-button type="primary" :icon="Plus" @click="openDialog">新增采购申请</el-button>
    </PageHeader>
    <ToolbarCard>
      <el-table :data="rows" stripe class="business-table" v-loading="loading">
        <el-table-column prop="orderNo" label="采购单号" min-width="160" />
        <el-table-column prop="medicineName" label="药品名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="supplierName" label="供应商" min-width="160" show-overflow-tooltip />
        <el-table-column prop="requestedQty" label="申请数量" width="100" />
        <el-table-column prop="suggestedQty" label="建议数量" width="100" />
        <el-table-column prop="reason" label="补货原因" min-width="180" show-overflow-tooltip />
        <el-table-column label="状态" width="90"><template #default="{ row }"><StatusTag :value="row.status" /></template></el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" :disabled="row.status !== 'pending' || auth.user?.role === 'purchaser'" @click="approve(row)">通过</el-button>
          </template>
        </el-table-column>
      </el-table>
    </ToolbarCard>
    <el-dialog v-model="visible" title="新增采购申请" width="680px" class="form-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="two-col-form">
        <el-form-item label="补货药品" prop="medicine_id">
          <el-select v-model="form.medicine_id" filterable placeholder="请选择药品">
            <el-option v-for="item in medicines" :key="item.id" :label="`${item.name} 库存${item.currentStock}`" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="供应商" prop="supplier_id">
          <el-select v-model="form.supplier_id" filterable placeholder="请选择供应商">
            <el-option v-for="item in suppliers" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="申请数量" prop="requested_qty"><el-input-number v-model="form.requested_qty" :min="1" /></el-form-item>
        <el-form-item label="建议数量" prop="suggested_qty"><el-input-number v-model="form.suggested_qty" :min="1" /></el-form-item>
        <el-form-item label="补货原因" prop="reason"><el-input v-model.trim="form.reason" /></el-form-item>
        <el-form-item label="备注" prop="remark"><el-input v-model.trim="form.remark" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">提交申请</el-button>
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
import { useAuthStore } from '../store'

const auth = useAuthStore()
const rows = ref([])
const medicines = ref([])
const suppliers = ref([])
const loading = ref(false)
const saving = ref(false)
const visible = ref(false)
const formRef = ref()
const form = reactive({ medicine_id: null, supplier_id: null, requested_qty: 1, suggested_qty: 1, reason: '', created_by: 1, remark: '' })
const rules = {
  medicine_id: [{ required: true, message: '请选择补货药品', trigger: 'change' }],
  supplier_id: [{ required: true, message: '请选择供应商', trigger: 'change' }],
  reason: [{ required: true, message: '请输入补货原因', trigger: 'blur' }]
}
async function loadData() {
  loading.value = true
  try { ;[rows.value, medicines.value, suppliers.value] = await Promise.all([api.purchases(), api.medicines(), api.suppliers()]) } finally { loading.value = false }
}
function openDialog() { Object.assign(form, { medicine_id: null, supplier_id: null, requested_qty: 1, suggested_qty: 1, reason: '', created_by: auth.user?.id || 1, remark: '' }); visible.value = true }
async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    await api.createPurchase(form)
    ElMessage.success('采购申请已提交')
    visible.value = false
    await loadData()
  } catch (error) {} finally { saving.value = false }
}
async function approve(row) {
  try {
    await api.approvePurchase(row.id)
    ElMessage.success('采购单已通过')
    await loadData()
  } catch (error) {}
}
onMounted(loadData)
</script>
