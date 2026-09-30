<template>
  <el-card shadow="never" class="page-card">
    <template #header>
      <div class="card-header">
        <span class="card-title">用户管理</span>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">新增用户</el-button>
      </div>
    </template>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="keyword"
        placeholder="搜索账号/昵称/邮箱/手机号"
        clearable
        style="width: 280px"
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      />
      <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
      <el-button :icon="Refresh" @click="handleReset">重置</el-button>
    </div>

    <!-- 用户表格 -->
    <el-table v-loading="loading" :data="tableData" border stripe style="width: 100%">
      <el-table-column type="index" label="#" width="60" align="center" />
      <el-table-column prop="username" label="账号" min-width="120" />
      <el-table-column prop="name" label="昵称" min-width="100" />
      <el-table-column label="角色" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">
            {{ row.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="email" label="邮箱" min-width="160" show-overflow-tooltip />
      <el-table-column prop="phone" label="手机号" min-width="130" />
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'warning'">
            {{ row.status === 1 ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="170" align="center">
        <template #default="{ row }">{{ formatTime(row.create_time) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200" align="center" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEditDialog(row)">编辑</el-button>
          <el-button link type="primary" @click="openResetDialog(row)">重置密码</el-button>
          <el-popconfirm
            title="确定删除该用户吗？"
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
      :title="editing ? '编辑用户' : '新增用户'"
      width="520px"
      @open="initForm"
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="90px">
        <el-form-item v-if="!editing" label="账号" prop="username">
          <el-input v-model="form.username" placeholder="2-32位登录账号" maxlength="32" />
        </el-form-item>
        <el-form-item v-else label="账号">
          <el-input :model-value="form.username" disabled />
        </el-form-item>
        <el-form-item label="昵称" prop="name">
          <el-input v-model="form.name" placeholder="请输入昵称" maxlength="64" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" style="width: 100%" :disabled="isSelf">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" clearable />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" clearable />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="form.status"
            :active-value="1"
            :inactive-value="0"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
        <el-button @click="formVisible = false">取消</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码弹窗 -->
    <el-dialog v-model="resetVisible" title="重置密码" width="440px" @open="initResetForm">
      <el-form ref="resetFormRef" :model="resetForm" :rules="resetRules" label-width="100px">
        <el-form-item label="账号">
          <el-input :model-value="resetTarget?.username" disabled />
        </el-form-item>
        <el-form-item label="新密码" prop="password">
          <el-input
            v-model="resetForm.password"
            type="password"
            show-password
            placeholder="6-64位新密码"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm">
          <el-input
            v-model="resetForm.confirm"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" :loading="resetSaving" @click="handleResetSave">确认</el-button>
        <el-button @click="resetVisible = false">取消</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Refresh, Search } from '@element-plus/icons-vue'
import { createUser, deleteUser, getUsers, updateUser, type UserListItem } from '@/api/user'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

/* ===== 列表数据 ===== */
const loading = ref(false)
const tableData = ref<UserListItem[]>([])
const total = ref(0)
const keyword = ref('')
const page = ref(1)
const pageSize = ref(10)

const formatTime = (t: string) => {
  if (!t) return '-'
  return t.replace('T', ' ').slice(0, 19)
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getUsers({
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

const handleReset = () => {
  keyword.value = ''
  page.value = 1
  loadData()
}

/* ===== 新增/编辑弹窗 ===== */
const formVisible = ref(false)
const editing = ref(false)
const saving = ref(false)
const formRef = ref<FormInstance>()
const editTarget = ref<UserListItem | null>(null)

/** 编辑自己时禁止修改角色 */
const isSelf = computed(() => editing.value && editTarget.value?.id === userStore.user?.id)

const form = reactive({
  username: '',
  name: '',
  role: 'user',
  email: '',
  phone: '',
  status: 1
})

const emailReg = /^[\w.-]+@[\w-]+\.[\w.-]+$/
const phoneReg = /^1[3-9]\d{9}$/

const formRules: FormRules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 2, max: 32, message: '账号长度 2-32 位', trigger: 'blur' }
  ],
  name: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  email: [
    {
      validator: (_r, v: string, cb) => {
        if (!v || emailReg.test(v)) cb()
        else cb(new Error('邮箱格式不正确'))
      },
      trigger: 'blur'
    }
  ],
  phone: [
    {
      validator: (_r, v: string, cb) => {
        if (!v || phoneReg.test(v)) cb()
        else cb(new Error('手机号格式不正确'))
      },
      trigger: 'blur'
    }
  ]
}

const openCreateDialog = () => {
  editing.value = false
  editTarget.value = null
  formVisible.value = true
}

const openEditDialog = (row: UserListItem) => {
  editing.value = true
  editTarget.value = row
  formVisible.value = true
}

const initForm = () => {
  if (editing.value && editTarget.value) {
    const t = editTarget.value
    form.username = t.username
    form.name = t.name
    form.role = t.role
    form.email = t.email ?? ''
    form.phone = t.phone ?? ''
    form.status = t.status
  } else {
    form.username = ''
    form.name = ''
    form.role = 'user'
    form.email = ''
    form.phone = ''
    form.status = 1
  }
  formRef.value?.clearValidate()
}

const handleSave = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      if (editing.value && editTarget.value) {
        await updateUser(editTarget.value.id, {
          name: form.name,
          role: form.role,
          email: form.email || null,
          phone: form.phone || null,
          status: form.status
        })
        ElMessage.success('修改成功')
      } else {
        await createUser({
          username: form.username,
          password: '123456',
          name: form.name,
          role: form.role,
          email: form.email || null,
          phone: form.phone || null,
          status: form.status
        })
        ElMessage.success('创建成功,初始密码为 123456')
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

/* ===== 重置密码弹窗 ===== */
const resetVisible = ref(false)
const resetSaving = ref(false)
const resetFormRef = ref<FormInstance>()
const resetTarget = ref<UserListItem | null>(null)

const resetForm = reactive({
  password: '',
  confirm: ''
})

const resetRules: FormRules = {
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 64, message: '密码长度 6-64 位', trigger: 'blur' }
  ],
  confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_r, v: string, cb) => {
        if (v !== resetForm.password) cb(new Error('两次输入的密码不一致'))
        else cb()
      },
      trigger: 'blur'
    }
  ]
}

const openResetDialog = (row: UserListItem) => {
  resetTarget.value = row
  resetVisible.value = true
}

const initResetForm = () => {
  resetForm.password = ''
  resetForm.confirm = ''
  resetFormRef.value?.clearValidate()
}

const handleResetSave = () => {
  resetFormRef.value?.validate(async (valid) => {
    if (!valid || !resetTarget.value) return
    resetSaving.value = true
    try {
      await updateUser(resetTarget.value.id, { password: resetForm.password })
      ElMessage.success('密码重置成功')
      resetVisible.value = false
    } catch {
      // 错误已由拦截器提示
    } finally {
      resetSaving.value = false
    }
  })
}

/* ===== 删除 ===== */
const handleDelete = async (row: UserListItem) => {
  try {
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    // 删除后如果当前页空了,回退一页
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
    justify-content: space-between;

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
</style>
