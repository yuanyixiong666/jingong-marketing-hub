<template>
  <view class="container">
    <!-- 顶部标题 -->
    <view class="header">
      <text class="header-title">金宫味业</text>
      <text class="header-sub">数字营销数据中台</text>
    </view>

    <!-- 核心指标卡片 -->
    <view class="stats-grid">
      <view class="card stat-card" v-for="item in stats" :key="item.label">
        <text class="stat-value">{{ item.value }}</text>
        <text class="stat-label">{{ item.label }}</text>
      </view>
    </view>

    <!-- 各平台数据概览 -->
    <view class="card">
      <text class="card-title">平台数据概览</text>
      <view class="platform-list">
        <view class="platform-item" v-for="p in platforms" :key="p.name">
          <text class="platform-name">{{ p.name }}</text>
          <text class="platform-count">{{ p.count }} 条</text>
        </view>
      </view>
    </view>

    <!-- 最近爬取任务 -->
    <view class="card">
      <text class="card-title">最近采集任务</text>
      <view class="task-list">
        <view class="task-item" v-for="t in tasks" :key="t.id">
          <text class="task-name">{{ t.name }}</text>
          <text class="task-status" :class="t.status">{{ t.statusText }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
/**
 * 首页 - 数据概览
 * AI生成：展示核心指标和平台数据概览
 */
import { getPlatformStats, getTasks } from "@/utils/api"

export default {
  data() {
    return {
      stats: [
        { label: "总数据量", value: "0" },
        { label: "今日采集", value: "0" },
        { label: "竞品监控", value: "5" },
        { label: "舆情预警", value: "0" },
      ],
      platforms: [
        { name: "抖音", count: 0 },
        { name: "小红书", count: 0 },
        { name: "天猫", count: 0 },
        { name: "京东", count: 0 },
      ],
      tasks: [
        { id: 1, name: "抖音热榜采集", status: "pending", statusText: "待执行" },
        { id: 2, name: "小红书笔记搜索", status: "pending", statusText: "待执行" },
        { id: 3, name: "竞品价格监控", status: "pending", statusText: "待执行" },
      ],
    }
  },
  onShow() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const statsRes = await getPlatformStats()
        if (statsRes.code === 200 && statsRes.data) {
          statsRes.data.forEach((item) => {
            const p = this.platforms.find((p) => p.name === this.getPlatformName(item.platform))
            if (p) p.count = item.total
          })
        }
      } catch (e) {
        console.log("数据加载失败，使用默认值", e)
      }
    },
    getPlatformName(key) {
      const map = { douyin: "抖音", xiaohongshu: "小红书", tmall: "天猫", jd: "京东" }
      return map[key] || key
    },
  },
}
</script>

<style scoped>
.header {
  text-align: center;
  padding: 40rpx 0;
}
.header-title {
  display: block;
  font-size: 44rpx;
  font-weight: 700;
  color: #1e3a5f;
}
.header-sub {
  display: block;
  font-size: 28rpx;
  color: #666;
  margin-top: 8rpx;
}
.stats-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 20rpx;
}
.stat-card {
  flex: 1;
  min-width: 45%;
  text-align: center;
  padding: 30rpx 16rpx;
}
.platform-list {
  display: flex;
  flex-direction: column;
}
.platform-item {
  display: flex;
  justify-content: space-between;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}
.platform-name { color: #333; }
.platform-count { color: #2c5282; font-weight: 600; }
.task-list { display: flex; flex-direction: column; }
.task-item {
  display: flex;
  justify-content: space-between;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}
.task-status.success { color: #38a169; }
.task-status.running { color: #3182ce; }
.task-status.pending { color: #999; }
.task-status.failed { color: #e53e3e; }
</style>
