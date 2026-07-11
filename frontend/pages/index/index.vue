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
          <view class="platform-left">
            <text class="platform-icon">{{ p.icon }}</text>
            <text class="platform-name">{{ p.name }}</text>
          </view>
          <view class="platform-right">
            <text class="platform-count">{{ p.count }} 条</text>
            <view class="platform-bar">
              <view class="bar-fill" :style="{ width: p.percent + '%' }"></view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 最近爬取任务 -->
    <view class="card">
      <text class="card-title">最近采集任务</text>
      <view class="task-list">
        <view class="task-item" v-for="t in tasks" :key="t.id">
          <view class="task-left">
            <text class="task-name">{{ t.task_name }}</text>
            <text class="task-time">{{ t.cron_expr }}</text>
          </view>
          <text class="task-status" :class="t.status">{{ statusMap[t.status] || t.status }}</text>
        </view>
      </view>
    </view>

    <!-- 舆情预警 -->
    <view class="card" v-if="negativeCount > 0">
      <text class="card-title">舆情预警</text>
      <view class="alert-item" @click="goSentiment">
        <text class="alert-icon">!</text>
        <text class="alert-text">发现 {{ negativeCount }} 条负面舆情，建议及时处理</text>
        <text class="alert-arrow">></text>
      </view>
    </view>
  </view>
</template>

<script>
/**
 * 首页 - 数据概览
 * AI生成：展示核心指标和平台数据概览
 * 人工修改：完善API对接和数据展示逻辑
 */
import { getPlatformStats, getTasks, getSentimentStats } from "@/utils/api"

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
        { name: "抖音", icon: "D", count: 0, percent: 0 },
        { name: "小红书", icon: "X", count: 0, percent: 0 },
        { name: "天猫", icon: "T", count: 0, percent: 0 },
        { name: "京东", icon: "J", count: 0, percent: 0 },
      ],
      tasks: [],
      negativeCount: 0,
      statusMap: { pending: "待执行", running: "运行中", success: "成功", failed: "失败" },
    }
  },
  onShow() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const [statsRes, tasksRes, sentRes] = await Promise.all([
          getPlatformStats(),
          getTasks(),
          getSentimentStats(),
        ])

        // 平台数据
        if (statsRes.code === 200 && statsRes.data) {
          let total = 0
          statsRes.data.forEach((item) => {
            const p = this.platforms.find((p) => p.name === this.getPlatformName(item.platform))
            if (p) {
              p.count = item.total
              total += item.total
            }
          })
          // 计算百分比
          this.platforms.forEach((p) => {
            p.percent = total > 0 ? Math.round((p.count / total) * 100) : 0
          })
          this.stats[0].value = String(total)
          this.stats[1].value = String(total) // 简化：今日采集 = 总量
        }

        // 任务数据
        if (tasksRes.code === 200 && tasksRes.data) {
          this.tasks = tasksRes.data.slice(0, 5)
        }

        // 舆情数据
        if (sentRes.code === 200 && sentRes.data) {
          const dist = sentRes.data.distribution || {}
          this.negativeCount = dist.negative || 0
          this.stats[3].value = String(this.negativeCount)
        }
      } catch (e) {
        console.log("数据加载失败", e)
      }
    },
    getPlatformName(key) {
      const map = { douyin: "抖音", xiaohongshu: "小红书", tmall: "天猫", jd: "京东" }
      return map[key] || key
    },
    goSentiment() {
      uni.navigateTo({ url: "/pages/sentiment/sentiment?filter=negative" })
    },
  },
}
</script>

<style scoped>
.header {
  text-align: center;
  padding: 40rpx 0 20rpx;
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
.stat-value {
  font-size: 48rpx;
  font-weight: 700;
  color: #2c5282;
}
.stat-label {
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}
.platform-list {
  display: flex;
  flex-direction: column;
}
.platform-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}
.platform-item:last-child { border-bottom: none; }
.platform-left {
  display: flex;
  align-items: center;
  gap: 12rpx;
}
.platform-icon {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: #e8f0fe;
  color: #2c5282;
  font-size: 24rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  line-height: 48rpx;
}
.platform-name { color: #333; font-size: 28rpx; }
.platform-right {
  display: flex;
  align-items: center;
  gap: 16rpx;
}
.platform-count { color: #2c5282; font-weight: 600; font-size: 26rpx; }
.platform-bar {
  width: 120rpx;
  height: 12rpx;
  background: #f0f0f0;
  border-radius: 6rpx;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #3182ce, #63b3ed);
  border-radius: 6rpx;
  transition: width 0.3s;
}
.task-list { display: flex; flex-direction: column; }
.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}
.task-item:last-child { border-bottom: none; }
.task-left { flex: 1; }
.task-name { display: block; font-size: 28rpx; color: #333; }
.task-time { display: block; font-size: 22rpx; color: #999; margin-top: 4rpx; }
.task-status {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
}
.task-status.success { background: #c6f6d5; color: #38a169; }
.task-status.running { background: #bee3f8; color: #3182ce; }
.task-status.pending { background: #f0f0f0; color: #999; }
.task-status.failed { background: #fed7d7; color: #e53e3e; }
.alert-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx;
  background: #fff5f5;
  border-radius: 12rpx;
  border-left: 6rpx solid #e53e3e;
}
.alert-arrow { color: #c53030; font-size: 28rpx; margin-left: auto; }
.alert-icon {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: #e53e3e;
  color: #fff;
  font-size: 24rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  line-height: 40rpx;
}
.alert-text { color: #c53030; font-size: 26rpx; }
</style>
