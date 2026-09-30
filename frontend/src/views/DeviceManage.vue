<template>
  <el-card shadow="never" class="page-card">
    <template #header>
      <span class="card-title">实验室设备管理</span>
    </template>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="keyword"
        placeholder="请输入名称查询"
        clearable
        style="width: 200px"
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      />
      <el-select
        v-model="labFilter"
        placeholder="选择实验室"
        clearable
        style="width: 160px"
        @change="handleSearch"
      >
        <el-option v-for="lab in labOptions" :key="lab.id" :label="lab.name" :value="lab.id" />
      </el-select>
      <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
      <el-button type="success" :icon="Plus" @click="openCreateDialog">新增</el-button>
    </div>

    <!-- 数据表格 -->
    <el-table v-loading="loading" :data="tableData" border stripe style="width: 100%">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column label="所属实验室" min-width="120">
        <template #default="{ row }">{{ row.lab_name || '-' }}</template>
      </el-table-column>
      <el-table-column prop="name" label="设备名称" min-width="120" />
      <el-table-column label="图片" width="90" align="center">
        <template #default="{ row }">
          <el-image
            v-if="row.image"
            :src="row.image"
            :preview-src-list="[row.image]"
            preview-teleported
            fit="cover"
            style="width: 50px; height: 50px; border-radius: 4px"
          />
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column label="型号规格" min-width="140">
        <template #default="{ row }">{{ row.model_spec || '-' }}</template>
      </el-table-column>
      <el-table-column prop="quantity" label="数量" width="80" align="center" />
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'">
            {{ row.status === 1 ? '正常' : '维修' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" align="center" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEditDialog(row)">编辑</el-button>
          <el-popconfirm
            title="确定删除该设备吗？"
            confirm-button-text="确定"
            cancel-button-text="取消"
            @confirm="handleDelete(row)"
          >
            <template #reference>
              <el-button link type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="formVisible"
      :title="editing ? '编辑' : '新增设备'"
      width="520px"
      @open="initForm"
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-form-item label="所属实验室" prop="lab_id">
          <el-select v-model="form.lab_id" placeholder="请选择实验室" style="width: 100%">
            <el-option v-for="lab in labOptions" :key="lab.id" :label="lab.name" :value="lab.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入设备名称" maxlength="128" />
        </el-form-item>
        <el-form-item label="图片" prop="image">
          <el-upload
            class="img-uploader"
            :show-file-list="false"
            :before-upload="beforeImgUpload"
            :http-request="handleImgUpload"
            accept="image/*"
          >
            <div v-if="form.image" class="img-preview">
              <el-image
                :src="form.image"
                fit="cover"
                style="width: 120px; height: 80px; border-radius: 4px"
              />
              <div class="img-mask">点击更换</div>
            </div>
            <div v-else class="img-placeholder">
              <el-icon class="img-icon"><Plus /></el-icon>
              <span>点击上传图片</span>
            </div>
          </el-upload>
        </el-form-item>
        <el-form-item label="型号规格" prop="model_spec">
          <el-input v-model="form.model_spec" placeholder="请输入型号规格" maxlength="255" />
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="form.quantity" :min="1" :max="99999" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">正常</el-radio>
            <el-radio :value="2">维修</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" :loading="saving" @click="handleSave">确定</el-button>
        <el-button @click="formVisible = false">取消</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import {
  ElMessage,
  type FormInstance,
  type FormRules,
  type UploadRequestOptions
} from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import {
  createDevice,
  deleteDevice,
  getDevices,
  getLabOptions,
  updateDevice,
  type DeviceItem,
  type LabOption
} from '@/api/device'
import { uploadFile } from '@/api/upload'

/* ===== 实验室下拉选项 ===== */
const labOptions = ref<LabOption[]>([])
const loadLabOptions = async () => {
  try {
    labOptions.value = await getLabOptions()
  } catch {
    // 错误已由拦截器提示
  }
}

/* ===== 列表数据 ===== */
const loading = ref(false)
const tableData = ref<DeviceItem[]>([])
const total = ref(0)
const keyword = ref('')
const labFilter = ref<number | null>(null)
const page = ref(1)
const pageSize = ref(10)

const loadData = async () => {
  loading.value = true
  try {
    const res = await getDevices({
      keyword: keyword.value,
      lab_id: labFilter.value,
      page: page.value,
      page_size: pageSize.value
    })
    tableData.value = res.list
    total.value = res.total
  } catch {
    // 错误已由拦截器提示
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  loadData()
}

/* ===== 新增/编辑弹窗 ===== */
const formVisible = ref(false)
const editing = ref(false)
const saving = ref(false)
const formRef = ref<FormInstance>()
const editTarget = ref<DeviceItem | null>(null)

const form = reactive({
  name: '',
  image: '',
  model_spec: '',
  quantity: 1,
  status: 1,
  lab_id: null as number | null
})

const formRules: FormRules = {
  lab_id: [{ required: true, message: '请选择所属实验室', trigger: 'change' }],
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }]
}

const openCreateDialog = () => {
  editing.value = false
  editTarget.value = null
  formVisible.value = true
}

const openEditDialog = (row: DeviceItem) => {
  editing.value = true
  editTarget.value = row
  formVisible.value = true
}

const initForm = () => {
  if (editing.value && editTarget.value) {
    const t = editTarget.value
    form.name = t.name
    form.image = t.image ?? ''
    form.model_spec = t.model_spec ?? ''
    form.quantity = t.quantity
    form.status = t.status
    form.lab_id = t.lab_id
  } else {
    form.name = ''
    form.image = ''
    form.model_spec = ''
    form.quantity = 1
    form.status = 1
    form.lab_id = null
  }
  formRef.value?.clearValidate()
}

/* ===== 图片上传 ===== */
const beforeImgUpload = (file: File) => {
  if (!file.type.startsWith('image/')) {
    ElMessage.error('只能上传图片')
    return false
  }
  return true
}

const handleImgUpload = async (options: UploadRequestOptions) => {
  try {
    const res = await uploadFile(options.file as File)
    form.image = res.url
    ElMessage.success('图片上传成功')
  } catch {
    ElMessage.error('图片上传失败')
  }
}

/* ===== 保存 ===== */
const handleSave = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid || !form.lab_id) return
    saving.value = true
    try {
      const payload = {
        name: form.name,
        image: form.image || null,
        model_spec: form.model_spec || null,
        quantity: form.quantity,
        status: form.status,
        lab_id: form.lab_id
      }
      if (editing.value && editTarget.value) {
        await updateDevice(editTarget.value.id, payload)
        ElMessage.success('修改成功')
      } else {
        await createDevice(payload)
        ElMessage.success('创建成功')
      }
      formVisible.value = false
      loadData()
    } catch {
      // 错误已由拦截器提示
    } finally {
      saving.value = false
    }
  })
}

/* ===== 删除 ===== */
const handleDelete = async (row: DeviceItem) => {
  try {
    await deleteDevice(row.id)
    ElMessage.success('删除成功')
    if (tableData.value.length === 1 && page.value > 1) {
      page.value--
    }
    loadData()
  } catch {
    // 错误已由拦截器提示
  }
}

onMounted(() => {
  loadLabOptions()
  loadData()
})
</script>

<style scoped lang="scss">
.page-card {
  border-radius: 4px;

  .card-title {
    font-weight: 600;
    color: #333;
  }
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.text-muted {
  color: #c0c4cc;
}

/* 图片上传 */
.img-uploader {
  :deep(.el-upload) {
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    overflow: hidden;
    transition: border-color 0.2s;

    &:hover {
      border-color: #409eff;
    }
  }
}

.img-placeholder {
  width: 120px;
  height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #999;
  font-size: 12px;

  .img-icon {
    font-size: 22px;
    color: #c0c4cc;
  }
}

.img-preview {
  position: relative;
  width: 120px;
  height: 80px;

  .img-mask {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.5);
    color: #fff;
    font-size: 12px;
    opacity: 0;
    transition: opacity 0.2s;
  }

  &:hover .img-mask {
    opacity: 1;
  }
}
</style>
