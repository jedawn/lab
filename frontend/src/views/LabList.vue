<template>
  <el-card shadow="never" class="page-card">
    <template #header>
      <div class="card-header">
        <span class="card-title">实验室列表</span>
      </div>
    </template>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="keyword"
        placeholder="请输入名称查询"
        clearable
        style="width: 280px"
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      />
      <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
    </div>

    <!-- 实验室卡片网格 -->
    <div v-loading="loading" class="lab-grid">
      <el-card
        v-for="item in list"
        :key="item.id"
        shadow="hover"
        class="lab-card"
        :body-style="{ padding: '0' }"
      >
        <div class="cover" @click="goDetail(item)">
          <el-image v-if="item.cover" :src="item.cover" fit="cover" class="cover-img" />
          <div v-else class="cover-empty">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <el-tag
            v-if="item.status !== 1"
            type="info"
            size="small"
            class="cover-tag"
          >已禁用</el-tag>
        </div>
        <div class="card-body">
          <div class="lab-name" :title="item.name">{{ item.name }}</div>
          <div class="lab-meta">位置:{{ item.location || '-' }}</div>
          <div class="lab-meta">容量:{{ item.capacity }} 人</div>
          <div class="lab-meta">
            开放:<span v-if="item.open_start && item.open_end"
              >{{ item.open_start }} - {{ item.open_end }}</span
            ><span v-else>-</span>
          </div>
          <div class="lab-actions">
            <el-button class="action-btn" @click="goDetail(item)">查看设备</el-button>
            <el-button
              class="action-btn"
              type="primary"
              :disabled="item.status !== 1"
              @click="openReserve(item)"
            >预约</el-button>
          </div>
        </div>
      </el-card>

      <el-empty v-if="!loading && list.length === 0" description="暂无实验室" class="empty" />
    </div>

    <!-- 分页 -->
    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[12, 24, 48]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>

    <!-- 预约弹窗 -->
    <ReservationDialog
      v-model="reserveVisible"
      :lab-id="reserveLab?.id ?? null"
      :lab-name="reserveLab?.name ?? ''"
    />
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { OfficeBuilding, Search } from '@element-plus/icons-vue'
import { getLabs, type LabItem } from '@/api/lab'
import ReservationDialog from '@/components/ReservationDialog.vue'

const router = useRouter()

const loading = ref(false)
const list = ref<LabItem[]>([])
const total = ref(0)
const keyword = ref('')
const page = ref(1)
const pageSize = ref(12)

const loadData = async () => {
  loading.value = true
  try {
    const res = await getLabs({
      keyword: keyword.value,
      page: page.value,
      page_size: pageSize.value
    })
    list.value = res.list
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

const goDetail = (item: LabItem) => {
  router.push(`/lab/${item.id}`)
}

/* ===== 预约 ===== */
const reserveVisible = ref(false)
const reserveLab = ref<LabItem | null>(null)

const openReserve = (item: LabItem) => {
  reserveLab.value = item
  reserveVisible.value = true
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

.lab-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 18px;
  min-height: 120px;
}

.lab-card {
  border-radius: 6px;
  overflow: hidden;

  .cover {
    position: relative;
    width: 100%;
    height: 170px;
    cursor: pointer;
    background-color: #f5f7fa;

    .cover-img {
      width: 100%;
      height: 100%;
      display: block;
    }

    .cover-empty {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #c0c4cc;

      .el-icon {
        font-size: 48px;
      }
    }

    .cover-tag {
      position: absolute;
      top: 8px;
      right: 8px;
    }
  }

  .card-body {
    padding: 14px 16px 16px;
  }

  .lab-name {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 10px;
  }

  .lab-meta {
    font-size: 14px;
    color: #606266;
    line-height: 1.9;
  }

  .lab-actions {
    display: flex;
    gap: 10px;
    margin-top: 14px;

    .action-btn {
      flex: 1;
      margin: 0;
    }
  }
}

.empty {
  grid-column: 1 / -1;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
</style>
