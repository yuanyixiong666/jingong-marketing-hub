/**
 * 应用入口
 * AI生成：uni-app 应用初始化
 * 人工修改：集成 uview-plus UI组件库、Pinia 状态管理、ECharts 图表库
 */
import App from "./App"

// #ifndef VUE3
import Vue from "vue"
Vue.config.productionTip = false
App.mpType = "app"
const app = new Vue({ ...App })
app.$mount()
// #endif

// #ifdef VUE3
import { createSSRApp } from "vue"
import uviewPlus from 'uview-plus'
import 'uview-plus/index.scss'
import { createPinia } from 'pinia'

export function createApp() {
  const app = createSSRApp(App)
  const pinia = createPinia()

  // 注册 uview-plus UI 组件库
  app.use(uviewPlus)
  // 注册 Pinia 状态管理
  app.use(pinia)

  return { app }
}
// #endif
