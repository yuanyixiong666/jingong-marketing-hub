<template>
  <view class="container">
    <!-- 顶部标题 -->
    <view class="header">
      <text class="header-title">金宫味业</text>
      <text class="header-sub">数字营销数据中台</text>
    </view>

    <!-- 核心指标卡片 - 使用 uview-plus u-grid -->
    <u-grid :col="2" :border="false">
      <u-grid-item v-for="(item, index) in stats" :key="item.label" @click="onStatClick(index)">
        <view class="stat-card">
          <text class="stat-value">{{ item.value }}</text>
          <text class="stat-label">{{ item.label }}</text>
        </view>
      </u-grid-item>
    </u-grid>

    <!-- 各平台数据概览 - 使用 uview-plus u-list -->
    <view class="card">
      <text class="card-title">平台数据概览</text>
      <u-list @scrolltolower="loadMore">
        <u-list-item v-for="p in platforms" :key="p.name">
          <view class="platform-item" @click="goPlatformData(p)">
            <view class="platform-left">
              <u-avatar :text="p.icon" size="48" bgColor="#e8f0fe" color="#2c5282"></u-avatar>
              <text class="platform-name">{{ p.name }}</text>
            </view>
            <view class="platform-right">
              <text class="platform-count">{{ p.count }} 条</text>
              <view class="platform-bar">
                <view class="bar-fill" :style="{ width: p.percent + '%' }"></view>
              </view>
            </view>
          </view>
        </u-list-item>
      </u-list>
    </view>

    <!-- 最近爬取任务 - 使用 uview-plus u-tag 状态标签 -->
    <view class="card">
      <text class="card-title">最近采集任务</text>
      <view class="task-list">
        <view class="task-item" v-for="t in tasks" :key="t.id" @click="goTask(t.id)">
          <view class="task-left">
            <text class="task-name">{{ t.task_name }}</text>
            <text class="task-time">{{ t.cron_expr }}</text>
          </view>
          <u-tag
            :text="statusMap[t.status] || t.status"
            :type="statusTypeMap[t.status] || 'info'"
            size="mini"
            shape="circle"
          ></u-tag>
        </view>
      </view>
    </view>

    <!-- 舆情预警 - 使用 uview-plus u-notice-bar -->
    <u-notice-bar v-if="negativeCount > 0" text="发现负面舆情，建议及时处理" type="error" :scrollable="false">
      <template #right>
        <view class="notice-action" @click="goSentiment">
          <text class="notice-text">发现 {{ negativeCount }} 条负面舆情，建议及时处理</text>
          <text class="notice-arrow">></text>
        </view>
      </template>
    </u-notice-bar>
  </view>
</template>

<script>
/**
 * 首页 - 数据概览
 * AI生成：展示核心指标和平台数据概览
 * 人工修改：集成 uview-plus 组件库（u-grid/u-list/u-avatar/u-tag/u-notice-bar），完善API对接
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
        { name: "微博", icon: "W", count: 0, percent: 0 },
      ],
      tasks: [],
      negativeCount: 0,
      statusMap: { pending: "待执行", running: "运行中", success: "成功", failed: "失败" },
      statusTypeMap: { pending: "info", running: "primary", success: "success", failed: "error" },
    }
  },
  onShow() {
    if (this._loading) return
    if (this._lastLoad && Date.now() - this._lastLoad < 60000) return
    this.loadData()
  },
  methods: {
    async loadData() {
      if (this._loading) return
      this._loading = true
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
          this.platforms.forEach((p) => {
            p.percent = total > 0 ? Math.round((p.count / total) * 100) : 0
          })
          this.stats[0].value = String(total)
          this.stats[1].value = String(this.platforms.filter((p) => p.count > 0).length)
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
      } finally {
        this._loading = false
        this._lastLoad = Date.now()
      }
    },
    getPlatformName(key) {
      const map = { douyin: "抖音", xiaohongshu: "小红书", tmall: "天猫", jd: "京东", weibo: "微博" }
      return map[key] || key
    },
    goSentiment() {
      uni.navigateTo({ url: "/pages/sentiment/sentiment?filter=negative" })
    },
    onStatClick(index) {
      if (index === 0 || index === 1 || index === 2) {
        uni.switchTab({ url: "/pages/crawler/crawler" })
      } else if (index === 3) {
        uni.navigateTo({ url: "/pages/sentiment/sentiment" })
      }
    },
    goPlatformData(p) {
      uni.navigateTo({ url: `/pages/platform-data/platform-data?name=${encodeURIComponent(p.name)}&icon=${p.icon}` })
    },
    goTask(id) {
      uni.navigateTo({ url: `/pages/task/task?id=${id}` })
    },
    loadMore() {
      // 列表滚动到底部时的处理
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
.stat-card {
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
.notice-action {
  display: flex;
  align-items: center;
  padding: 8rpx 16rpx;
}
.notice-text { color: #c53030; font-size: 26rpx; }
.notice-arrow { color: #c53030; font-size: 28rpx; margin-left: 8rpx; }
</style>
