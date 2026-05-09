<template>
  <div>
    <PageHeader title="批次入库管理" description="药品到货后登记批号、供应商、有效期与货位，系统同步增加库存。">
      <el-button type="primary" :icon="Plus" @click="openDialog">登记入库</el-button>
    </PageHeader>
    <ToolbarCard>
      <el-table :data="rows" stripe class="business-table" v-loading="loading">
        <el-table-column prop="orderNo" label="入库单号" min-width="160" />
        <el-table-column prop="medicineName" label="药品名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="batchNo" label="批号" min-width="120" />
        <el-table-column prop="quantity" label="数量" width="90" />
        <el-table-column prop="purchasePrice" label="进价" width="100" />
        <el-table-column prop="receivedBy" label="接收人" width="110" />
        <el-table-column prop="receivedAt" label="入库时间" min-width="170" />
        <el-table-column label="状态" width="90"><template #default="{ row }"><StatusTag :value="row.status" /></template></el-table-column>
      </el-table>
    </ToolbarCard>
    <el-dialog v-model="visible" title="登记批次入库" width="760px" class="form-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="two-col-form">
        <el-form-item label="药品" prop="medicine_id">
          <el-select v-model="form.medicine_id" filterable placeholder="请选择药品">
            <el-option v-for="item in medicines" :key="item.id" :label="`${item.name} ${item.specification}`" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="供应商" prop="supplier_id">
          <el-select v-model="form.supplier_id" filterable clearable placeholder="请选择供应商">
            <el-option v-for="item in suppliers" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="批号" prop="batch_no"><el-input v-model.trim="form.batch_no" /></el-form-item>
        <el-form-item label="入库数量" prop="quantity"><el-input-number v-model="form.quantity" :min="1" /></el-form-item>
        <el-form-item label="进价" prop="purchase_price"><el-input-number v-model="form.purchase_price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="接收人" prop="received_by"><el-input v-model.trim="form.received_by" /></el-form-item>
        <el-form-item label="生产日期" prop="production_date"><el-date-picker v-model="form.production_date" type="date" value-format="YYYY-MM-DD" /></el-form-item>
        <el-form-item label="有效期至" prop="expiry_date"><el-date-picker v-model="form.expiry_date" type="date" value-format="YYYY-MM-DD" /></el-form-item>
        <el-form-item label="货位" prop="location"><el-input v-model.trim="form.location" /></el-form-item>
        <el-form-item label="备注" prop="remark"><el-input v-model.trim="form.remark" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">确认入库</el-button>
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

const rows = ref([])
const medicines = ref([])
const suppliers = ref([])
const loading = ref(false)
const saving = ref(false)
const visible = ref(false)
const formRef = ref()
const form = reactive(defaultForm())
function defaultForm() { return { medicine_id: null, supplier_id: null, batch_no: '', quantity: 1, purchase_price: 0, received_by: '药房管理员', production_date: '', expiry_date: '', location: '', remark: '' } }
const rules = {
  medicine_id: [{ required: true, message: '请选择药品', trigger: 'change' }],
  batch_no: [{ required: true, message: '请输入批号', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入入库数量', trigger: 'change' }],
  received_by: [{ required: true, message: '请输入接收人', trigger: 'blur' }],
  expiry_date: [{ required: true, message: '请选择有效期', trigger: 'change' }]
}
async function loadData() {
  loading.value = true
  try { ;[rows.value, medicines.value, suppliers.value] = await Promise.all([api.inbounds(), api.medicines(), api.suppliers()]) } finally { loading.value = false }
}
function openDialog() { Object.assign(form, defaultForm()); visible.value = true }
async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    await api.createInbound(form)
    ElMessage.success('入库成功')
    visible.value = false
    await loadData()
  } catch (error) {} finally { saving.value = false }
}
onMounted(loadData)
</script>
