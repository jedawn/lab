import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import type { App } from 'vue'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

export default function (app: App) {
  app.use(ElementPlus, {
    locale: zhCn
  })

  for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
  }
}
