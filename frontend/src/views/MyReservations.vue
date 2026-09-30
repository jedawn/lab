<template>
  <el-card shadow="never" class="page-card">
    <template #header>
      <div class="card-header">
        <span class="card-title">我的预约记录</span>
      </div>
    </template>

    <!-- 状态筛选 -->
    <div class="search-bar">
      <el-select
        v-model="statusFilter"
        placeholder="请选择状态"
        clearable
        style="width: 200px"
        @change="handleSearch"
      >
        <el-option
          v-for="opt in statusOptions"
          :key="opt.value"
          :label="opt.label"
          :value="opt.value"
        />
      </el-select>
      <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
    </div>

    <!-- 预约记录表格 -->
    <el-table v-loading="loading" :data="tableData" border stripe style="width: 100%">
      <el-table-column prop="lab_name" label="实验室" min-width="140" />
      <el-table-column label="预约类型" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.device_id ? 'primary' : 'success'">
            {{ row.device_id ? '设备' : '实验室' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="设备" min-width="130">
        <template #default="{ row }">{{ row.device_name || '-' }}</template>
      </el-table-column>
      <el-table-column prop="date" label="日期" width="120" align="center" />
      <el-table-column label="预约时段" width="160" align="center">
        <template #default="{ row }">
          <span v-if="row.start_time && row.end_time"
            >{{ row.start_time }} - {{ row.end_time }}</span
          >
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column label="备注" min-width="140" show-overflow-tooltip>
        <template #default="{ row }">{{ row.remark || '-' }}</template>
      </el-table-column>
      <el-table-column label="预约状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="statusMeta(row.status).type">{{ statusMeta(row.status).label }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="90" align="center" fixed="right">
        <template #default="{ row }">
          <el-popconfirm
            v-if="row.status === 1"
            title="确定取消该预约吗？"
            confirm-button-text="确定"
            cancel-button-text="再想想"
            @confirm="handleCancel(row)"
          >
            <template #reference>
              <el-button link type="danger">取消</el-button>
            </template>
          </el-popconfirm>
          <span v-else class="text-muted">-</span>
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
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { cancelReservation, getMyReservations, type ReservationItem } from '@/api/reservation'

const statusOptions = [
  { value: 1, label: '待审核' },
  { value: 2, label: '已通过' },
  { value: 3, label: '已拒绝' },
  { value: 4, label: '已取消' },
  { value: 5, label: '已过期' }
]

const statusMeta = (status: number) => {
  switch (status) {
    case 1:
      return { label: '待审核', type: 'warning' as const }
    case 2:
      return { label: '已通过', type: 'success' as const }
    case 3:
      return { label: '已拒绝', type: 'danger' as const }
    case 5:
      return { label: '已过期', type: 'info' as const }
    default:
      return { label: '已取消', type: 'info' as const }
  }
}

const loading = ref(false)
const tableData = ref<ReservationItem[]>([])
const total = ref(0)
const statusFilter = ref<number | null>(null)
const page = ref(1)
const pageSize = ref(10)

const loadData = async () => {
  loading.value = true
  try {
    const res = await getMyReservations({
      status: statusFilter.value,
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

const handleCancel = async (row: ReservationItem) => {
  try {
    await cancelReservation(row.id)
    ElMessage.success('已取消')
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
</style>
