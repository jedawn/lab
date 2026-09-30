<template>
  <div class="login-container">
    <el-card class="login-card" shadow="always">
      <div class="login-header">
        <div class="logo-badge">
          <el-icon class="login-logo"><Monitor /></el-icon>
        </div>
        <div class="login-title">实验室预约系统</div>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" size="large" @keyup.enter="handleLogin">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入账号"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="login-btn" :loading="loading" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
        <div class="login-footer">
          <span class="login-tip">默认账号：admin　密码：123456</span>
          <el-link type="primary" :underline="false" @click="router.push('/register')">
            注册账号
          </el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Lock, User } from '@element-plus/icons-vue'
import { login } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const route = useRoute()
const router = useRouter()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: 'admin',
  password: ''
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const { token, user } = await login({
        username: form.username,
        password: form.password
      })
      localStorage.setItem('token', token)
      localStorage.setItem('userName', user.name)
      userStore.setUser(user)
      ElMessage.success('登录成功')
      router.push((route.query.redirect as string) || '/dashboard')
    } catch {
      // 错误信息已由响应拦截器统一提示
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1890ff 0%, #001529 100%);
}

.login-card {
  width: 400px;
  border-radius: 8px;

  :deep(.el-card__body) {
    padding: 40px 36px 28px;
  }

  .login-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 28px;

    .logo-badge {
      width: 56px;
      height: 56px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      background-color: #e6f4ff;
      margin-bottom: 12px;
    }

    .login-logo {
      font-size: 32px;
      color: #1890ff;
    }

    .login-title {
      font-size: 22px;
      font-weight: 600;
      color: #001529;
      letter-spacing: 2px;
    }
  }

  .login-btn {
    width: 100%;
    letter-spacing: 4px;
  }

  .login-tip {
    font-size: 12px;
    color: #999;
  }

  .login-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}
</style>
