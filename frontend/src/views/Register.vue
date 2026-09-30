<template>
  <div class="register-container">
    <el-card class="register-card" shadow="always">
      <div class="register-header">
        <div class="logo-badge">
          <el-icon class="register-logo"><Monitor /></el-icon>
        </div>
        <div class="register-title">注册账号</div>
      </div>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        size="large"
        @keyup.enter="handleRegister"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名(2-32 个字符)"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码(至少 6 位)"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            class="register-btn"
            :loading="loading"
            @click="handleRegister"
          >
            注 册
          </el-button>
        </el-form-item>
        <div class="register-footer">
          <el-link type="primary" :underline="false" @click="router.push('/login')">
            已有账号?返回登录
          </el-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Lock, Monitor, User } from '@element-plus/icons-vue'
import { register } from '@/api/auth'

const router = useRouter()

const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
})

const validateConfirm = (_rule: unknown, value: string, callback: (err?: Error) => void) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 32, message: '用户名长度为 2-32 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 64, message: '密码长度至少 6 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' },
  ],
}

const handleRegister = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await register({
        username: form.username,
        password: form.password,
        confirm_password: form.confirmPassword,
      })
      ElMessage.success('注册成功,请登录')
      router.push('/login')
    } catch {
      // 错误信息已由响应拦截器统一提示
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.register-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1890ff 0%, #001529 100%);
}

.register-card {
  width: 400px;
  border-radius: 8px;

  :deep(.el-card__body) {
    padding: 40px 36px 28px;
  }

  .register-header {
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

    .register-logo {
      font-size: 32px;
      color: #1890ff;
    }

    .register-title {
      font-size: 22px;
      font-weight: 600;
      color: #001529;
      letter-spacing: 2px;
    }
  }

  .register-btn {
    width: 100%;
    letter-spacing: 4px;
  }

  .register-footer {
    text-align: center;
  }
}
</style>
