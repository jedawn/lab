<template>
  <el-card shadow="never" class="page-card">
    <template #header>
      <div class="card-header">
        <span>快捷入口</span>
      </div>
    </template>
    <div class="quick-entry">
      <div
        class="entry-item"
        v-for="item in quickEntries"
        :key="item.title"
        @click="router.push(item.path)"
      >
        <el-icon class="entry-icon" :style="{ color: item.color }">
          <component :is="item.icon" />
        </el-icon>
        <span class="entry-text">{{ item.title }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const quickEntries = [
  { title: '实验室管理', icon: 'OfficeBuilding', color: '#409eff', path: '/lab' },
  { title: '设备列表管理', icon: 'Box', color: '#e6a23c', path: '/device' },
  { title: '用户管理', icon: 'User', color: '#67c23a', path: '/user' }
]
</script>

<style scoped lang="scss">
.page-card {
  border-radius: 4px;

  .card-header {
    display: flex;
    align-items: center;
    font-weight: 600;
    color: #333;
  }

  .quick-entry {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 20px;

    .entry-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 16px 0;
      border-radius: 4px;
      cursor: pointer;
      transition: background-color 0.2s;

      &:hover {
        background-color: #f5f7fa;
      }

      .entry-icon {
        font-size: 32px;
        margin-bottom: 8px;
      }

      .entry-text {
        font-size: 13px;
        color: #595959;
      }
    }
  }
}
</style>
