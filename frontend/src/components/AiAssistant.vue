<template>
  <div class="ai-assistant">
    <transition name="ai-fade">
      <div v-if="visible" class="ai-panel">
        <div class="ai-header">
          <div class="ai-title">
            <el-icon class="ai-title-icon"><Promotion /></el-icon>
            <span>AI 智能助手</span>
          </div>
          <el-icon class="ai-close-btn" @click="visible = false"><Close /></el-icon>
        </div>

        <div ref="bodyRef" class="ai-body">
          <div v-if="!messages.length" class="ai-welcome">
            <el-icon class="ai-welcome-icon"><ChatDotRound /></el-icon>
            <p>你好!我是 AI 智能助手,有什么可以帮你?</p>
          </div>
          <template v-else>
            <div
              v-for="(msg, idx) in messages"
              :key="idx"
              class="ai-msg"
              :class="`ai-msg-${msg.role}`"
            >
              <div class="ai-bubble">{{ msg.content }}</div>
            </div>
          </template>
          <div
            v-if="loading && messages[messages.length - 1]?.role === 'user'"
            class="ai-msg ai-msg-assistant"
          >
            <div class="ai-bubble ai-typing">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        </div>

        <div class="ai-footer">
          <el-input
            v-model="input"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 4 }"
            placeholder="输入问题,Enter 发送"
            resize="none"
            :disabled="loading"
            @keydown.enter.exact.prevent="handleSend"
          />
          <el-button
            class="ai-send-btn"
            type="primary"
            :loading="loading"
            :disabled="!input.trim()"
            @click="handleSend"
          >
            <el-icon v-if="!loading"><Promotion /></el-icon>
          </el-button>
        </div>
      </div>
    </transition>

    <div class="ai-fab" @click="visible = !visible">
      <el-icon class="ai-fab-icon">
        <Close v-if="visible" />
        <ChatDotRound v-else />
      </el-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, ref } from 'vue'
import { ChatDotRound, Close, Promotion } from '@element-plus/icons-vue'
import { chatWithAiStream } from '@/api/ai'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const visible = ref(false)
const input = ref('')
const loading = ref(false)
const messages = ref<Message[]>([])
const bodyRef = ref<HTMLElement>()

const scrollToBottom = async () => {
  await nextTick()
  const el = bodyRef.value
  if (el) el.scrollTop = el.scrollHeight
}

const handleSend = async () => {
  const content = input.value.trim()
  if (!content || loading.value) return

  messages.value.push({ role: 'user', content })
  input.value = ''
  loading.value = true
  await scrollToBottom()

  let msgIndex = -1
  try {
    await chatWithAiStream(content, (token) => {
      // 首个 token:创建助手消息气泡;后续 token 追加
      if (msgIndex === -1) {
        msgIndex = messages.value.push({ role: 'assistant', content: token }) - 1
      } else {
        const msg = messages.value[msgIndex]
        if (msg) msg.content += token
      }
      const el = bodyRef.value
      if (el) el.scrollTop = el.scrollHeight
    })
    // 流结束但没收到任何 token
    if (msgIndex === -1) {
      messages.value.push({ role: 'assistant', content: '(空回复)' })
    }
  } catch (e) {
    const errorMsg = e instanceof Error ? e.message : '服务暂时不可用,请稍后重试。'
    if (msgIndex === -1) {
      messages.value.push({ role: 'assistant', content: `抱歉,${errorMsg}` })
    } else {
      const errorTarget = messages.value[msgIndex]
      if (errorTarget) errorTarget.content += `\n\n(出错:${errorMsg})`
    }
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}
</script>

<style scoped lang="scss">
.ai-assistant {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 999;
}

/* 浮窗按钮 */
.ai-fab {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition:
    transform 0.2s,
    box-shadow 0.2s;

  &:hover {
    transform: scale(1.08);
    box-shadow: 0 6px 16px rgba(24, 144, 255, 0.5);
  }

  .ai-fab-icon {
    font-size: 24px;
    color: #fff;
  }
}

/* 聊天面板 */
.ai-panel {
  position: absolute;
  right: 0;
  bottom: 60px;
  width: 360px;
  max-width: 90vw;
  height: 500px;
  max-height: 70vh;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ai-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: #fff;

  .ai-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 15px;
    font-weight: 600;

    .ai-title-icon {
      font-size: 18px;
    }
  }

  .ai-close-btn {
    font-size: 18px;
    cursor: pointer;
    opacity: 0.85;
    transition: opacity 0.2s;

    &:hover {
      opacity: 1;
    }
  }
}

.ai-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;

  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.15);
    border-radius: 3px;
  }
}

.ai-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  text-align: center;

  .ai-welcome-icon {
    font-size: 40px;
    color: #1890ff;
    margin-bottom: 12px;
  }

  p {
    font-size: 14px;
    margin: 0;
  }
}

.ai-msg {
  display: flex;
  margin-bottom: 12px;

  &-user {
    justify-content: flex-end;
  }

  &-assistant {
    justify-content: flex-start;
  }
}

.ai-bubble {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}

.ai-msg-user .ai-bubble {
  background: #1890ff;
  color: #fff;
  border-bottom-right-radius: 4px;
}

.ai-msg-assistant .ai-bubble {
  background: #f0f2f5;
  color: #333;
  border-bottom-left-radius: 4px;
}

/* 打字动画 */
.ai-typing {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;

  .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #999;
    animation: ai-bounce 1.2s infinite ease-in-out;

    &:nth-child(2) {
      animation-delay: 0.2s;
    }
    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
}

@keyframes ai-bounce {
  0%,
  60%,
  100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-6px);
    opacity: 1;
  }
}

.ai-footer {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;

  :deep(.el-textarea__inner) {
    box-shadow: none;
    border: 1px solid #d9d9d9;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
  }

  .ai-send-btn {
    flex-shrink: 0;
    height: 40px;
    width: 40px;
    padding: 0;
    border-radius: 8px;
  }
}

/* 面板显隐过渡 */
.ai-fade-enter-active,
.ai-fade-leave-active {
  transition:
    opacity 0.2s,
    transform 0.2s;
}
.ai-fade-enter-from,
.ai-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
