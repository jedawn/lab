import request from '@/utils/request'

export interface UploadResult {
  original_name: string
  disk_name: string
  size: number
  url: string
}

/** 上传文件(返回可直接访问的 url) */
export function uploadFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<unknown, UploadResult>('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
