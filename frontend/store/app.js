/**
 * Pinia 状态管理 - 全局数据存储
 * AI生成：Pinia store 定义
 * 人工修改：对接实际API数据结构
 */
import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    // 平台统计数据
    platformStats: [],
    // 舆情统计数据
    sentimentStats: null,
    // 爬虫任务列表
    tasks: [],
    // 竞品列表
    competitors: [],
    // 加载状态
    loading: false,
    // 最后刷新时间
    lastRefresh: null,
  }),

  getters: {
    totalDataCount: (state) => {
      return state.platformStats.reduce((sum, item) => sum + (item.total || 0), 0)
    },
    negativeCount: (state) => {
      return state.sentimentStats?.distribution?.negative || 0
    },
    platformMap: (state) => {
      const nameMap = { douyin: '抖音', xiaohongshu: '小红书', tmall: '天猫', jd: '京东', weibo: '微博' }
      return state.platformStats.map(item => ({
        ...item,
        name: nameMap[item.platform] || item.platform,
      }))
    },
  },

  actions: {
    setPlatformStats(data) {
      this.platformStats = data
      this.lastRefresh = new Date().toISOString()
    },
    setSentimentStats(data) {
      this.sentimentStats = data
    },
    setTasks(data) {
      this.tasks = data
    },
    setCompetitors(data) {
      this.competitors = data
    },
    setLoading(loading) {
      this.loading = loading
    },
    clearAll() {
      this.platformStats = []
      this.sentimentStats = null
      this.tasks = []
      this.competitors = []
      this.lastRefresh = null
    },
  },
})
