import request from '@/utils/request'
import router from '@/router'

/** AI 聊天对话(非流式,AI 响应较慢,单独放宽超时到 120s) */
export function chatWithAi(content: string) {
  return request.post<unknown, string>('/ai/chat', { content }, { timeout: 120000 })
}

/**
 * AI 流式聊天对话(SSE)
 * 逐 token 回调,前端实时渲染打字机效果
 */
export async function chatWithAiStream(
  content: string,
  onToken: (token: string) => void,
  signal?: AbortSignal
): Promise<void> {
  const token = localStorage.getItem('token')
  const response = await fetch('/api/ai/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: JSON.stringify({ content }),
    signal
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  // 鉴权失败等错误:后端返回 JSON 而非 SSE 流
  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    const result = await response.json()
    if (result.code === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userName')
      if (router.currentRoute.value.path !== '/login') {
        router.push('/login')
      }
      throw new Error(result.message || '登录已失效')
    }
    throw new Error(result.message || '请求失败')
  }

  if (!response.body) {
    throw new Error('响应体为空')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    // SSE 事件以 \n\n 分隔
    const events = buffer.split('\n\n')
    buffer = events.pop() || ''

    for (const event of events) {
      const line = event.trim()
      if (!line.startsWith('data: ')) continue
      const data = line.slice(6)
      if (data === '[DONE]') return

      let parsed: { content?: string; error?: string }
      try {
        parsed = JSON.parse(data)
      } catch {
        continue
      }
      if (parsed.error) {
        throw new Error(parsed.error)
      }
      if (parsed.content) {
        onToken(parsed.content)
      }
    }
  }
}
