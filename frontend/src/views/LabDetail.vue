<template>
  <el-card v-loading="loading" shadow="never" class="page-card">
    <!-- 标题 + 操作按钮 -->
    <div class="detail-header">
      <span class="detail-title">{{ lab ? `${lab.name}设备列表` : '实验室设备列表' }}</span>
      <div class="header-actions">
        <el-button type="primary" :disabled="!lab || lab.status !== 1" @click="openLabReserve">
          预约实验室
        </el-button>
        <el-button @click="goBack">返回实验室列表</el-button>
      </div>
    </div>

    <!-- 实验室信息 -->
    <div class="lab-info">
      <div class="info-intro">简介:{{ lab?.intro || lab?.name || '-' }}</div>
      <div class="info-line">
        <span>位置:{{ lab?.location || '-' }}</span>
        <span class="divider">|</span>
        <span>容纳 {{ lab?.capacity ?? 0 }} 人</span>
        <span class="divider">|</span>
        <span>
          开放:<template v-if="lab?.open_start && lab?.open_end"
            >{{ lab.open_start }} - {{ lab.open_end }}</template
          ><template v-else>-</template>
        </span>
      </div>
    </div>

    <!-- 设备表格 -->
    <el-table :data="devices" border stripe style="width: 100%">
      <el-table-column prop="lab_name" label="所属实验室" min-width="140" />
      <el-table-column prop="name" label="设备名称" min-width="130" />
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
      <el-table-column prop="model_spec" label="型号规格" min-width="150">
        <template #default="{ row }">{{ row.model_spec || '-' }}</template>
      </el-table-column>
      <el-table-column prop="quantity" label="数量" width="80" align="center" />
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'warning'">
            {{ row.status === 1 ? '正常' : '维修' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" align="center" fixed="right">
        <template #default="{ row }">
          <el-button
            link
            type="primary"
            :disabled="row.status !== 1"
            @click="openDeviceReserve(row)"
            >预约</el-button
          >
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
        layout="total, prev, pager, next"
        background
        @size-change="loadDevices"
        @current-change="loadDevices"
      />
    </div>

    <!-- 预约弹窗(实验室级可选设备 / 设备行级锁定设备) -->
    <ReservationDialog
      v-model="reserveVisible"
      :lab-id="lab?.id ?? null"
      :lab-name="lab?.name ?? ''"
      :device-id="reserveDeviceId"
      :lock-device="reserveDeviceId !== null"
    />
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getLab, type LabItem } from '@/api/lab'
import { getDevices, type DeviceItem } from '@/api/device'
import ReservationDialog from '@/components/ReservationDialog.vue'

const route = useRoute()
const router = useRouter()

const labId = Number(route.params.id)

const loading = ref(false)
const lab = ref<LabItem | null>(null)
const devices = ref<DeviceItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const loadLab = async () => {
  try {
    lab.value = await getLab(labId)
  } catch {
    // 错误已由拦截器提示
  }
}

const loadDevices = async () => {
  loading.value = true
  try {
    const res = await getDevices({
      lab_id: labId,
      page: page.value,
      page_size: pageSize.value
    })
    devices.value = res.list
    total.value = res.total
  } catch {
    // 错误已由拦截器提示
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/lab')
}

/* ===== 预约 ===== */
const reserveVisible = ref(false)
const reserveDeviceId = ref<number | null>(null)

/** 预约整个实验室(可在弹窗中选择设备) */
const openLabReserve = () => {
  reserveDeviceId.value = null
  reserveVisible.value = true
}

/** 预约某台设备(弹窗中锁定该设备) */
const openDeviceReserve = (row: DeviceItem) => {
  reserveDeviceId.value = row.id
  reserveVisible.value = true
}

onMounted(() => {
  loadLab()
  loadDevices()
})
</script>

<style scoped lang="scss">
.page-card {
  border-radius: 4px;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;

  .detail-title {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
  }
}

.lab-info {
  background-color: #fafafa;
  border-radius: 4px;
  padding: 14px 18px;
  margin-bottom: 18px;

  .info-intro {
    font-size: 14px;
    color: #606266;
    margin-bottom: 10px;
  }

  .info-line {
    font-size: 14px;
    color: #606266;

    .divider {
      margin: 0 14px;
      color: #dcdfe6;
    }
  }
}

.text-muted {
  color: #c0c4cc;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
