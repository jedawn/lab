<template>
  <el-card shadow="never" class="page-card">
    <template #header>
      <div class="card-header">
        <span class="card-title">实验室管理</span>
      </div>
    </template>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="keyword"
        placeholder="请输入名称查询"
        clearable
        style="width: 240px"
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      />
      <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
      <el-button type="success" :icon="Plus" @click="openCreateDialog">新增</el-button>
    </div>

    <!-- 数据表格 -->
    <el-table v-loading="loading" :data="tableData" border stripe style="width: 100%">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="name" label="名称" min-width="120" />
      <el-table-column prop="intro" label="简介" min-width="140" show-overflow-tooltip>
        <template #default="{ row }">{{ row.intro || '-' }}</template>
      </el-table-column>
      <el-table-column label="封面" width="90" align="center">
        <template #default="{ row }">
          <el-image
            v-if="row.cover"
            :src="row.cover"
            :preview-src-list="[row.cover]"
            preview-teleported
            fit="cover"
            style="width: 50px; height: 50px; border-radius: 4px"
          />
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="location" label="位置" min-width="120">
        <template #default="{ row }">{{ row.location || '-' }}</template>
      </el-table-column>
      <el-table-column prop="capacity" label="容量" width="80" align="center" />
      <el-table-column label="开放时间" width="150" align="center">
        <template #default="{ row }">
          <span v-if="row.open_start && row.open_end"
            >{{ row.open_start }} - {{ row.open_end }}</span
          >
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'info'">
            {{ row.status === 1 ? '开启' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" align="center" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEditDialog(row)">编辑</el-button>
          <el-popconfirm
            title="确定删除该实验室吗？"
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
      :title="editing ? '编辑' : '新增实验室'"
      width="600px"
      @open="initForm"
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="90px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入实验室名称" maxlength="128" />
        </el-form-item>
        <el-form-item label="简介" prop="intro">
          <el-input
            v-model="form.intro"
            type="textarea"
            :rows="3"
            placeholder="请输入简介"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="封面" prop="cover">
          <el-upload
            class="cover-uploader"
            :show-file-list="false"
            :before-upload="beforeCoverUpload"
            :http-request="handleCoverUpload"
            accept="image/*"
          >
            <div v-if="form.cover" class="cover-preview">
              <el-image
                :src="form.cover"
                fit="cover"
                style="width: 120px; height: 80px; border-radius: 4px"
              />
              <div class="cover-mask">点击更换</div>
            </div>
            <div v-else class="cover-placeholder">
              <el-icon class="cover-icon"><Plus /></el-icon>
              <span>点击上传封面</span>
            </div>
          </el-upload>
        </el-form-item>
        <el-form-item label="位置" prop="location">
          <el-input v-model="form.location" placeholder="请输入位置" maxlength="255" />
        </el-form-item>
        <el-form-item label="容量" prop="capacity">
          <el-input-number v-model="form.capacity" :min="1" :max="9999" />
        </el-form-item>
        <el-form-item label="开放时间" prop="openTime">
          <div class="time-range">
            <el-time-picker
              v-model="form.open_start"
              format="HH:mm"
              value-format="HH:mm"
              placeholder="开始时间"
              :clearable="true"
            />
            <span class="time-separator">-</span>
            <el-time-picker
              v-model="form.open_end"
              format="HH:mm"
              value-format="HH:mm"
              placeholder="结束时间"
              :clearable="true"
            />
          </div>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">正常</el-radio>
            <el-radio :value="0">禁用</el-radio>
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
import { createLab, deleteLab, getLabs, updateLab, type LabItem } from '@/api/lab'
import { uploadFile } from '@/api/upload'

/* ===== 列表数据 ===== */
const loading = ref(false)
const tableData = ref<LabItem[]>([])
const total = ref(0)
const keyword = ref('')
const page = ref(1)
const pageSize = ref(10)

const loadData = async () => {
  loading.value = true
  try {
    const res = await getLabs({
      keyword: keyword.value,
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
const editTarget = ref<LabItem | null>(null)

const form = reactive({
  name: '',
  intro: '',
  cover: '',
  location: '',
  capacity: 1,
  open_start: '' as string | null,
  open_end: '' as string | null,
  status: 1
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入实验室名称', trigger: 'blur' }],
  capacity: [{ required: true, message: '请输入容量', trigger: 'blur' }]
}

const openCreateDialog = () => {
  editing.value = false
  editTarget.value = null
  formVisible.value = true
}

const openEditDialog = (row: LabItem) => {
  editing.value = true
  editTarget.value = row
  formVisible.value = true
}

const initForm = () => {
  if (editing.value && editTarget.value) {
    const t = editTarget.value
    form.name = t.name
    form.intro = t.intro ?? ''
    form.cover = t.cover ?? ''
    form.location = t.location ?? ''
    form.capacity = t.capacity
    form.open_start = t.open_start ?? ''
    form.open_end = t.open_end ?? ''
    form.status = t.status
  } else {
    form.name = ''
    form.intro = ''
    form.cover = ''
    form.location = ''
    form.capacity = 1
    form.open_start = ''
    form.open_end = ''
    form.status = 1
  }
  formRef.value?.clearValidate()
}

/* ===== 封面上传 ===== */
const beforeCoverUpload = (file: File) => {
  if (!file.type.startsWith('image/')) {
    ElMessage.error('只能上传图片')
    return false
  }
  return true
}

const handleCoverUpload = async (options: UploadRequestOptions) => {
  try {
    const res = await uploadFile(options.file as File)
    form.cover = res.url
    ElMessage.success('封面上传成功')
  } catch {
    ElMessage.error('封面上传失败')
  }
}

/* ===== 保存 ===== */
const handleSave = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid) return
    // 开放时间校验:填写了一个就必须填另一个
    if (!!form.open_start !== !!form.open_end) {
      ElMessage.warning('开放时间请填写完整(开始和结束时间)')
      return
    }
    saving.value = true
    try {
      const payload = {
        name: form.name,
        intro: form.intro || null,
        cover: form.cover || null,
        location: form.location || null,
        capacity: form.capacity,
        open_start: form.open_start || null,
        open_end: form.open_end || null,
        status: form.status
      }
      if (editing.value && editTarget.value) {
        await updateLab(editTarget.value.id, payload)
        ElMessage.success('修改成功')
      } else {
        await createLab(payload)
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
const handleDelete = async (row: LabItem) => {
  try {
    await deleteLab(row.id)
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
  loadData()
})
</script>

<style scoped lang="scss">
.page-card {
  border-radius: 4px;

  .card-header {
    display: flex;
    align-items: center;

    .card-title {
      font-weight: 600;
      color: #333;
    }
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

/* 封面上传 */
.cover-uploader {
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

.cover-placeholder {
  width: 120px;
  height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #999;
  font-size: 12px;

  .cover-icon {
    font-size: 22px;
    color: #c0c4cc;
  }
}

.cover-preview {
  position: relative;
  width: 120px;
  height: 80px;

  .cover-mask {
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

  &:hover .cover-mask {
    opacity: 1;
  }
}

/* 开放时间 */
.time-range {
  display: flex;
  align-items: center;
  gap: 8px;

  .time-separator {
    color: #999;
  }
}
</style>
