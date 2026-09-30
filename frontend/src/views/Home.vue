<template>
  <div class="layout-container">
    <el-container class="layout">
      <el-aside class="layout-aside" :width="isCollapse ? '64px' : '220px'">
        <div class="logo" @click="router.push('/dashboard')">
          <el-icon class="logo-icon"><Monitor /></el-icon>
          <span v-show="!isCollapse" class="logo-text">实验室预约系统</span>
        </div>
        <el-menu
          class="layout-menu"
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          :router="true"
          background-color="#001529"
          text-color="#b7b7b7"
          active-text-color="#ffffff"
        >
          <template v-for="item in visibleMenuItems" :key="item.path">
            <!-- 有子菜单：渲染为分组 -->
            <el-sub-menu v-if="getVisibleChildren(item).length" :index="item.path">
              <template #title>
                <el-icon v-if="item.meta?.icon">
                  <component :is="item.meta.icon" />
                </el-icon>
                <span>{{ item.meta?.title }}</span>
              </template>
              <el-menu-item
                v-for="child in getVisibleChildren(item)"
                :key="child.path"
                :index="child.path"
              >
                {{ child.meta?.title }}
              </el-menu-item>
            </el-sub-menu>
            <!-- 无子菜单：渲染为普通菜单项 -->
            <el-menu-item v-else :index="item.path">
              <el-icon v-if="item.meta?.icon">
                <component :is="item.meta.icon" />
              </el-icon>
              <template #title>{{ item.meta?.title }}</template>
            </el-menu-item>
          </template>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="layout-header">
          <div class="header-left">
            <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
              <Fold v-if="!isCollapse" />
              <Expand v-else />
            </el-icon>
            <el-breadcrumb separator="/">
              <el-breadcrumb-item
                v-for="(item, index) in breadcrumbs"
                :key="item.path"
                :to="index < breadcrumbs.length - 1 ? { path: item.path } : undefined"
              >
                {{ item.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <el-tooltip content="刷新" placement="bottom">
              <el-icon class="header-icon" @click="handleRefresh"><Refresh /></el-icon>
            </el-tooltip>
            <el-tooltip content="全屏" placement="bottom">
              <el-icon class="header-icon" @click="toggleFullscreen"><FullScreen /></el-icon>
            </el-tooltip>
            <el-dropdown @command="handleCommand">
              <div class="user-info">
                <el-avatar :size="32" :src="avatarUrl" />
                <span class="user-name">{{ userName }}</span>
                <el-icon><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item command="password">修改密码</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <el-main class="layout-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>

    <!-- 个人信息弹窗 -->
    <el-dialog v-model="profileVisible" title="个人信息" width="620px" @open="initProfileForm">
      <el-form ref="profileFormRef" :model="profileForm" :rules="profileRules" label-width="90px">
        <div class="profile-body">
          <div class="avatar-section">
            <el-upload
              class="avatar-uploader"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              :http-request="handleAvatarUpload"
              accept="image/*"
            >
              <el-avatar :size="110" :src="profileForm.avatar || undefined">
                <el-icon class="avatar-default-icon"><User /></el-icon>
              </el-avatar>
            </el-upload>
            <div class="avatar-tip">点击上传头像</div>
          </div>
          <div class="form-section">
            <el-form-item label="账号" prop="username">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>
            <el-form-item label="角色" prop="role">
              <el-input v-model="profileForm.role" disabled />
            </el-form-item>
            <el-form-item label="昵称" prop="name">
              <el-input v-model="profileForm.name" placeholder="请输入昵称" maxlength="64" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" placeholder="请输入邮箱" clearable />
            </el-form-item>
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="profileForm.phone" placeholder="请输入手机号" clearable />
            </el-form-item>
          </div>
        </div>
      </el-form>
      <template #footer>
        <el-button type="primary" :loading="profileSaving" @click="handleProfileSave"
          >保存</el-button
        >
        <el-button @click="profileVisible = false">取消</el-button>
      </template>
    </el-dialog>

    <!-- AI 智能助手浮窗 -->
    <AiAssistant />

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="pwdVisible" title="修改密码" width="440px" @open="initPwdForm">
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="100px">
        <el-form-item label="原密码" prop="old_password">
          <el-input
            v-model="pwdForm.old_password"
            type="password"
            show-password
            placeholder="请输入原密码"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="pwdForm.new_password"
            type="password"
            show-password
            placeholder="6-64位新密码"
          />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input
            v-model="pwdForm.confirm_password"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" :loading="pwdSaving" @click="handlePwdSave">确认</el-button>
        <el-button @click="pwdVisible = false">取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { ElMessage, type UploadRequestOptions } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import { layoutRoute } from '@/router'
import AiAssistant from '@/components/AiAssistant.vue'
import { changePassword, updateProfile } from '@/api/auth'
import { uploadFile } from '@/api/upload'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const route = useRoute()
const router = useRouter()

const isCollapse = ref(false)

/** 顶栏显示名:优先取 store(修改后实时),其次取 localStorage */
const userName = computed(
  () => userStore.user?.name || localStorage.getItem('userName') || '管理员'
)
/** 头像:store 里的 avatar,无则为空(Element 显示默认头像) */
const avatarUrl = computed(() => userStore.user?.avatar || '')

/** 菜单数据源：来自路由配置，按 hidden 和 roles 过滤 */
const visibleMenuItems = computed(() =>
  (layoutRoute.children ?? []).filter((item) => {
    if (item.meta?.hidden) return false
    const roles = item.meta?.roles as string[] | undefined
    if (roles && roles.length && !roles.includes(userStore.user?.role ?? '')) {
      return false
    }
    return true
  })
)

const getVisibleChildren = (item: RouteRecordRaw): RouteRecordRaw[] =>
  (item.children ?? []).filter((child) => !child.meta?.hidden)

/** 当前激活菜单：详情页可通过 meta.activeMenu 指向列表页 */
const activeMenu = computed(() => (route.meta.activeMenu as string) || route.path)

/** 面包屑：取自当前路由 matched 链上带 title 的记录 */
const breadcrumbs = computed(() =>
  route.matched
    .filter((record) => record.meta.title)
    .map((record) => ({ path: record.path, title: record.meta.title as string }))
)

const handleRefresh = () => {
  router.go(0)
}

/* ===== 个人信息弹窗 ===== */
const profileVisible = ref(false)
const profileFormRef = ref<FormInstance>()
const profileSaving = ref(false)

const profileForm = reactive({
  username: '',
  role: '',
  name: '',
  email: '',
  phone: '',
  avatar: ''
})

const emailReg = /^[\w.-]+@[\w-]+\.[\w.-]+$/
const phoneReg = /^1[3-9]\d{9}$/

const profileRules: FormRules = {
  name: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
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

const initProfileForm = () => {
  const u = userStore.user
  profileForm.username = u?.username ?? ''
  profileForm.role = u?.role ?? ''
  profileForm.name = u?.name ?? ''
  profileForm.email = u?.email ?? ''
  profileForm.phone = u?.phone ?? ''
  profileForm.avatar = u?.avatar ?? ''
}

const beforeAvatarUpload = (file: File) => {
  if (!file.type.startsWith('image/')) {
    ElMessage.error('只能上传图片')
    return false
  }
  return true
}

const handleAvatarUpload = async (options: UploadRequestOptions) => {
  try {
    const res = await uploadFile(options.file as File)
    profileForm.avatar = res.url
    ElMessage.success('头像上传成功')
  } catch {
    ElMessage.error('头像上传失败')
  }
}

const handleProfileSave = () => {
  profileFormRef.value?.validate(async (valid) => {
    if (!valid) return
    profileSaving.value = true
    try {
      const updated = await updateProfile({
        name: profileForm.name,
        email: profileForm.email || null,
        avatar: profileForm.avatar || null,
        phone: profileForm.phone || null
      })
      userStore.updateUser(updated)
      localStorage.setItem('userName', updated.name)
      ElMessage.success('保存成功')
      profileVisible.value = false
    } catch {
      // 错误已由拦截器提示
    } finally {
      profileSaving.value = false
    }
  })
}

const handleCommand = (command: string) => {
  if (command === 'profile') {
    profileVisible.value = true
  } else if (command === 'password') {
    pwdVisible.value = true
  } else if (command === 'logout') {
    localStorage.removeItem('token')
    localStorage.removeItem('userName')
    userStore.reset()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}

/* ===== 修改密码弹窗 ===== */
const pwdVisible = ref(false)
const pwdFormRef = ref<FormInstance>()
const pwdSaving = ref(false)

const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const pwdRules: FormRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 64, message: '密码长度 6-64 位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (_r, v: string, cb) => {
        if (v !== pwdForm.new_password) cb(new Error('两次输入的密码不一致'))
        else cb()
      },
      trigger: 'blur'
    }
  ]
}

const initPwdForm = () => {
  pwdForm.old_password = ''
  pwdForm.new_password = ''
  pwdForm.confirm_password = ''
  pwdFormRef.value?.clearValidate()
}

const handlePwdSave = () => {
  pwdFormRef.value?.validate(async (valid) => {
    if (!valid) return
    pwdSaving.value = true
    try {
      await changePassword({
        old_password: pwdForm.old_password,
        new_password: pwdForm.new_password,
        confirm_password: pwdForm.confirm_password
      })
      ElMessage.success('密码修改成功,请重新登录')
      pwdVisible.value = false
      // 修改密码后清除登录态,跳转登录页
      localStorage.removeItem('token')
      localStorage.removeItem('userName')
      userStore.reset()
      router.push('/login')
    } catch {
      // 错误已由拦截器提示
    } finally {
      pwdSaving.value = false
    }
  })
}

const toggleFullscreen = () => {
  if (document.fullscreenElement) {
    document.exitFullscreen()
  } else {
    document.documentElement.requestFullscreen()
  }
}
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
}

.layout {
  height: 100%;
}

.layout-aside {
  background-color: #001529;
  transition: width 0.28s;
  overflow: hidden;

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    color: #fff;
    background-color: #002140;
    cursor: pointer;

    .logo-icon {
      font-size: 24px;
      color: #1890ff;
    }

    .logo-text {
      font-size: 16px;
      font-weight: 600;
      white-space: nowrap;
    }
  }

  .layout-menu {
    border-right: none;
    height: calc(100% - 60px);
    overflow-x: hidden;
    overflow-y: auto;

    &::-webkit-scrollbar {
      width: 6px;
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.2);
      border-radius: 3px;
    }

    :deep(.el-menu-item.is-active) {
      background-color: #1890ff;
    }

    :deep(.el-menu-item:hover),
    :deep(.el-sub-menu__title:hover) {
      background-color: rgba(255, 255, 255, 0.08);
    }
  }
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  border-bottom: 1px solid #f0f0f0;
  padding: 0 20px;
  height: 60px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);

  .header-left {
    display: flex;
    align-items: center;
    gap: 20px;

    .collapse-btn {
      font-size: 20px;
      cursor: pointer;
      color: #595959;
      transition: color 0.2s;

      &:hover {
        color: #1890ff;
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 20px;

    .header-icon {
      font-size: 18px;
      color: #595959;
      cursor: pointer;
      transition: color 0.2s;

      &:hover {
        color: #1890ff;
      }
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 0 8px;

      .user-name {
        font-size: 14px;
        color: #333;
      }
    }
  }
}

.layout-main {
  background-color: #f0f2f5;
  padding: 20px;
}

/* 个人信息弹窗 */
.profile-body {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 8px;
}

.avatar-uploader {
  :deep(.el-upload) {
    width: 110px;
    height: 110px;
    border: 1px dashed #d9d9d9;
    border-radius: 8px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    transition: border-color 0.2s;

    &:hover {
      border-color: #1890ff;
    }
  }
}

.avatar-default-icon {
  font-size: 48px;
  color: #c0c4cc;
}

.avatar-tip {
  margin-top: 10px;
  font-size: 12px;
  color: #999;
}

.form-section {
  flex: 1;
}
</style>
