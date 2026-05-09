<template>
  <div>
    <PageHeader title="药品目录管理" description="维护药品规格、分类、安全库存、价格和默认供应商。">
      <el-button type="primary" :icon="Plus" @click="openDialog()">新增药品</el-button>
    </PageHeader>
    <ToolbarCard>
      <el-table :data="rows" stripe class="business-table" v-loading="loading">
        <el-table-column prop="code" label="药品编码" min-width="110" />
        <el-table-column prop="name" label="药品名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="specification" label="规格" min-width="130" />
        <el-table-column prop="category" label="分类" min-width="110" />
        <el-table-column prop="currentStock" label="当前库存" width="100" />
        <el-table-column prop="safetyStock" label="安全库存" width="100" />
        <el-table-column prop="supplierName" label="供应商" min-width="160" show-overflow-tooltip />
        <el-table-column prop="location" label="货位" width="100" />
        <el-table-column label="状态" width="90"><template #default="{ row }"><StatusTag :value="row.status" /></template></el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </ToolbarCard>
    <el-dialog v-model="visible" :title="form.id ? '编辑药品' : '新增药品'" width="760px" class="form-dialog">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="two-col-form">
        <el-form-item label="药品编码" prop="code"><el-input v-model.trim="form.code" /></el-form-item>
        <el-form-item label="药品名称" prop="name"><el-input v-model.trim="form.name" /></el-form-item>
        <el-form-item label="规格" prop="specification"><el-input v-model.trim="form.specification" /></el-form-item>
        <el-form-item label="单位" prop="unit"><el-input v-model.trim="form.unit" /></el-form-item>
        <el-form-item label="分类" prop="category"><el-input v-model.trim="form.category" /></el-form-item>
        <el-form-item label="货位" prop="location"><el-input v-model.trim="form.location" /></el-form-item>
        <el-form-item label="当前库存" prop="current_stock"><el-input-number v-model="form.current_stock" :min="0" /></el-form-item>
        <el-form-item label="安全库存" prop="safety_stock"><el-input-number v-model="form.safety_stock" :min="0" /></el-form-item>
        <el-form-item label="售价" prop="selling_price"><el-input-number v-model="form.selling_price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="进价" prop="purchase_price"><el-input-number v-model="form.purchase_price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="预警天数" prop="expiry_warning_days"><el-input-number v-model="form.expiry_warning_days" :min="1" /></el-form-item>
        <el-form-item label="默认供应商" prop="supplier_id">
          <el-select v-model="form.supplier_id" clearable placeholder="请选择供应商">
            <el-option v-for="item in suppliers" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { z } from 'zod'
import PageHeader from '../components/PageHeader.vue'
import ToolbarCard from '../components/ToolbarCard.vue'
import StatusTag from '../components/StatusTag.vue'
import { api } from '../api'

const rows = ref([])
const suppliers = ref([])
const loading = ref(false)
const saving = ref(false)
const visible = ref(false)
const formRef = ref()
const form = reactive(defaultForm())

function defaultForm() {
  return { id: null, code: '', name: '', specification: '', unit: '盒', category: '', current_stock: 0, safety_stock: 0, selling_price: 0, purchase_price: 0, expiry_warning_days: 90, supplier_id: null, location: '', status: 'active' }
}

const rules = {
  code: [{ required: true, message: '请输入药品编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入药品名称', trigger: 'blur' }],
  specification: [{ required: true, message: '请输入规格', trigger: 'blur' }],
  category: [{ required: true, message: '请输入分类', trigger: 'blur' }]
}
const schema = z.object({ code: z.string().min(2, '药品编码至少2个字符'), name: z.string().min(2, '药品名称至少2个字符') })

async function loadData() {
  loading.value = true
  try {
    ;[rows.value, suppliers.value] = await Promise.all([api.medicines(), api.suppliers()])
  } finally { loading.value = false }
}

function openDialog(row) {
  Object.assign(form, defaultForm())
  if (row) Object.assign(form, {
    id: row.id, code: row.code, name: row.name, specification: row.specification, unit: row.unit, category: row.category,
    current_stock: row.currentStock, safety_stock: row.safetyStock, selling_price: Number(row.sellingPrice),
    purchase_price: Number(row.purchasePrice), expiry_warning_days: row.expiryWarningDays, supplier_id: row.supplierId, location: row.location, status: row.status
  })
  visible.value = true
}

async function save() {
  const result = schema.safeParse(form)
  if (!result.success) return ElMessage.warning(result.error.issues[0].message)
  await formRef.value.validate()
  saving.value = true
  try {
    if (form.id) await api.updateMedicine(form.id, form)
    else await api.createMedicine(form)
    ElMessage.success('保存成功')
    visible.value = false
    await loadData()
  } catch (error) {
  } finally { saving.value = false }
}

async function remove(row) {
  await ElMessageBox.confirm(`确认删除 ${row.name} 吗？`, '删除药品', { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' })
  try {
    await api.deleteMedicine(row.id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) {}
}

onMounted(loadData)
</script>
