<template>
  <el-dialog
    :model-value="modelValue"
    title="实验室预约"
    width="520px"
    @update:model-value="(v: boolean) => emit('update:modelValue', v)"
    @open="initForm"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="实验室">
        <el-input :model-value="labName" disabled />
      </el-form-item>
      <el-form-item label="设备">
        <el-select
          v-model="selectedDeviceId"
          :disabled="lockDevice"
          placeholder="不指定设备(预约整个实验室)"
          style="width: 100%"
        >
          <el-option label="不指定设备(预约整个实验室)" :value="null" />
          <el-option
            v-for="d in deviceOptions"
            :key="d.id"
            :label="`${d.name}${d.model_spec ? ' (' + d.model_spec + ')' : ''}`"
            :value="d.id"
            :disabled="d.status !== 1"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="预约日期" prop="date">
        <el-date-picker
          v-model="form.date"
          type="date"
          placeholder="请选择预约日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          :disabled-date="disabledPastDate"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="开始时间" prop="start_time">
        <el-time-picker
          v-model="form.start_time"
          format="HH:mm"
          value-format="HH:mm"
          placeholder="开始时间"
          :clearable="true"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="结束时间" prop="end_time">
        <el-time-picker
          v-model="form.end_time"
          format="HH:mm"
          value-format="HH:mm"
          placeholder="结束时间"
          :clearable="true"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="备注" prop="remark">
        <el-input
          v-model="form.remark"
          type="textarea"
          :rows="3"
          placeholder="请输入备注信息"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { createReservation } from '@/api/reservation'
import { getDevices, type DeviceItem } from '@/api/device'

const props = defineProps<{
  modelValue: boolean
  labId: number | null
  labName: string
  /** 预选设备ID(从设备行预约时传入) */
  deviceId?: number | null
  /** 是否锁定设备(设备行预约时为 true,不可改选) */
  lockDevice?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const formRef = ref<FormInstance>()
const saving = ref(false)
const deviceOptions = ref<DeviceItem[]>([])
const selectedDeviceId = ref<number | null>(null)

const form = reactive({
  date: '',
  start_time: '' as string | null,
  end_time: '' as string | null,
  remark: ''
})

const rules: FormRules = {
  date: [{ required: true, message: '请选择预约日期', trigger: 'change' }]
}

/** 禁止选择今天之前的日期 */
const disabledPastDate = (date: Date) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return date.getTime() < today.getTime()
}

const initForm = async () => {
  form.date = ''
  form.start_time = ''
  form.end_time = ''
  form.remark = ''
  formRef.value?.clearValidate()

  // 设备选择:设备行预约时锁定为该设备;实验室级预约默认为空(整个实验室)
  selectedDeviceId.value = props.lockDevice ? (props.deviceId ?? null) : null
  deviceOptions.value = []
  if (props.labId) {
    try {
      const res = await getDevices({ lab_id: props.labId, page: 1, page_size: 100 })
      deviceOptions.value = res.list
    } catch {
      // 错误已由拦截器提示
    }
  }
}

const handleSubmit = () => {
  formRef.value?.validate(async (valid) => {
    if (!valid) return
    // 时间区间校验:两者都填了时,结束时间必须晚于开始时间
    if (form.start_time && form.end_time && form.end_time <= form.start_time) {
      ElMessage.warning('结束时间必须晚于开始时间')
      return
    }
    if (!props.labId) {
      ElMessage.warning('实验室信息缺失')
      return
    }
    saving.value = true
    try {
      await createReservation({
        lab_id: props.labId,
        device_id: selectedDeviceId.value,
        date: form.date,
        start_time: form.start_time || null,
        end_time: form.end_time || null,
        remark: form.remark || null
      })
      ElMessage.success('预约成功,请等待管理员审核')
      emit('update:modelValue', false)
      emit('success')
    } catch {
      // 错误已由拦截器提示
    } finally {
      saving.value = false
    }
  })
}
</script>
