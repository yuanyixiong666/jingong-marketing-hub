<template>
  <view class="container">
    <view class="card">
      <text class="card-title">营销战情室</text>
      <text class="desc">实时数据可视化大屏</text>
    </view>

    <!-- 平台数据占比 - 简易饼图效果 -->
    <view class="card chart-card">
      <text class="card-title">各平台数据占比</text>
      <view class="bar-chart">
        <view class="bar-row" v-for="p in platformData" :key="p.name">
          <text class="bar-label">{{ p.name }}</text>
          <view class="bar-track">
            <view class="bar-fill" :style="{ width: p.percent + '%', background: p.color }"></view>
          </view>
          <text class="bar-value">{{ p.count }} ({{ p.percent }}%)</text>
        </view>
      </view>
    </view>

    <!-- 舆情情感分布 -->
    <view class="card chart-card">
      <text class="card-title">舆情情感分布</text>
      <view class="sentiment-chart">
        <view class="sentiment-bar" v-for="s in sentimentData" :key="s.label">
          <view class="sentiment-fill" :style="{ width: s.percent + '%', background: s.color }"></view>
          <text class="sentiment-label">{{ s.label }}</text>
          <text class="sentiment-value">{{ s.count }} ({{ s.percent }}%)</text>
        </view>
      </view>
      <view class="sentiment-summary">
        <text class="summary-text">共 {{ totalSentiment }} 条舆情，正面占比 {{ positivePercent }}%</text>
      </view>
    </view>

    <!-- 竞品关键词热度 -->
    <view class="card chart-card">
      <text class="card-title">舆情关键词热度</text>
      <view class="keyword-list">
        <view class="keyword-row" v-for="k in keywordData" :key="k.keyword">
          <text class="keyword-name">{{ k.keyword }}</text>
          <view class="keyword-bars">
            <view class="mini-bar positive" :style="{ width: k.positivePct + '%' }">
              <text class="mini-label">{{ k.positive }}</text>
            </view>
            <view class="mini-bar neutral" :style="{ width: k.neutralPct + '%' }">
              <text class="mini-label">{{ k.neutral }}</text>
            </view>
            <view class="mini-bar negative" :style="{ width: k.negativePct + '%' }">
              <text class="mini-label">{{ k.negative }}</text>
            </view>
          </view>
          <text class="keyword-total">{{ k.total }}条</text>
        </view>
      </view>
      <view class="legend">
        <text class="legend-item positive">正面</text>
        <text class="legend-item neutral">中性</text>
        <text class="legend-item negative">负面</text>
      </view>
    </view>

    <!-- 平台互动量 -->
    <view class="card chart-card">
      <text class="card-title">各平台互动量</text>
      <view class="bar-chart">
        <view class="bar-row" v-for="p in engagementData" :key="p.name">
          <text class="bar-label">{{ p.name }}</text>
          <view class="bar-track">
            <view class="bar-fill" :style="{ width: p.percent + '%', background: p.color }"></view>
          </view>
          <text class="bar-value">{{ formatNum(p.likes) }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
/**
 * 营销战情室 - 数据可视化
 * AI生成：CSS实现数据可视化图表
 * 人工修改：对接真实API数据
 */
import { getPlatformStats, getSentimentStats } from "@/utils/api"

const COLORS = ["#3182ce", "#38a169", "#d69e2e", "#e53e3e"]

export default {
  data() {
    return {
      platformData: [],
      sentimentData: [],
      keywordData: [],
      engagementData: [],
      totalSentiment: 0,
      positivePercent: 0,
    }
  },
  onShow() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const [statsRes, sentRes] = await Promise.all([
          getPlatformStats(),
          getSentimentStats(),
        ])

        // 平台数据占比
        if (statsRes.code === 200 && statsRes.data) {
          const total = statsRes.data.reduce((s, i) => s + i.total, 0)
          const nameMap = { douyin: "抖音", xiaohongshu: "小红书", tmall: "天猫", jd: "京东" }
          this.platformData = statsRes.data.map((item, idx) => ({
            name: nameMap[item.platform] || item.platform,
            count: item.total,
            percent: total > 0 ? Math.round((item.total / total) * 100) : 0,
            color: COLORS[idx % COLORS.length],
            likes: item.total_likes || 0,
          }))

          // 互动量
          const maxLikes = Math.max(...this.platformData.map(p => p.likes), 1)
          this.engagementData = this.platformData.map(p => ({
            ...p,
            percent: Math.round((p.likes / maxLikes) * 100),
          }))
        }

        // 舆情数据
        if (sentRes.code === 200 && sentRes.data) {
          const dist = sentRes.data.distribution || {}
          const totalS = (dist.positive || 0) + (dist.neutral || 0) + (dist.negative || 0)
          this.totalSentiment = totalS
          this.positivePercent = totalS > 0 ? Math.round(((dist.positive || 0) / totalS) * 100) : 0

          this.sentimentData = [
            { label: "正面", count: dist.positive || 0, color: "#38a169", percent: totalS > 0 ? Math.round(((dist.positive || 0) / totalS) * 100) : 0 },
            { label: "中性", count: dist.neutral || 0, color: "#d69e2e", percent: totalS > 0 ? Math.round(((dist.neutral || 0) / totalS) * 100) : 0 },
            { label: "负面", count: dist.negative || 0, color: "#e53e3e", percent: totalS > 0 ? Math.round(((dist.negative || 0) / totalS) * 100) : 0 },
          ]

          // 关键词热度
          const byKeyword = sentRes.data.by_keyword || []
          this.keywordData = byKeyword.map(k => {
            const maxPct = Math.max(k.positive || 0, k.neutral || 0, k.negative || 0, 1)
            return {
              keyword: k.keyword,
              total: k.total,
              positive: k.positive || 0,
              negative: k.negative || 0,
              neutral: k.neutral || 0,
              positivePct: Math.round(((k.positive || 0) / maxPct) * 100),
              neutralPct: Math.round(((k.neutral || 0) / maxPct) * 100),
              negativePct: Math.round(((k.negative || 0) / maxPct) * 100),
            }
          })
        }
      } catch (e) {
        console.log("数据加载失败", e)
      }
    },
    formatNum(n) {
      if (n >= 10000) return (n / 10000).toFixed(1) + "w"
      if (n >= 1000) return (n / 1000).toFixed(1) + "k"
      return String(n)
    },
  },
}
</script>

<style scoped>
.desc { color: #666; font-size: 26rpx; display: block; margin-top: 8rpx; }
.chart-card { margin-top: 20rpx; }

/* 横向柱状图 */
.bar-chart { margin-top: 16rpx; }
.bar-row {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}
.bar-label {
  width: 100rpx;
  font-size: 24rpx;
  color: #666;
}
.bar-track {
  flex: 1;
  height: 32rpx;
  background: #f0f0f0;
  border-radius: 16rpx;
  overflow: hidden;
  margin: 0 16rpx;
}
.bar-fill {
  height: 100%;
  border-radius: 16rpx;
  transition: width 0.5s;
}
.bar-value {
  width: 140rpx;
  font-size: 24rpx;
  color: #333;
  text-align: right;
}

/* 情感分布 */
.sentiment-chart { margin-top: 16rpx; }
.sentiment-bar {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
  height: 48rpx;
}
.sentiment-fill {
  height: 100%;
  border-radius: 8rpx;
  min-width: 40rpx;
  display: flex;
  align-items: center;
  padding-left: 12rpx;
}
.sentiment-label {
  width: 80rpx;
  font-size: 24rpx;
  color: #666;
}
.sentiment-value {
  margin-left: 16rpx;
  font-size: 24rpx;
  color: #333;
}
.sentiment-summary {
  margin-top: 16rpx;
  padding: 12rpx;
  background: #f8fafc;
  border-radius: 8rpx;
}
.summary-text { font-size: 24rpx; color: #666; }

/* 关键词热度 */
.keyword-list { margin-top: 16rpx; }
.keyword-row {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}
.keyword-name {
  width: 140rpx;
  font-size: 24rpx;
  color: #333;
  font-weight: 500;
}
.keyword-bars {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}
.mini-bar {
  height: 24rpx;
  border-radius: 4rpx;
  display: flex;
  align-items: center;
  padding-left: 8rpx;
  min-width: 30rpx;
}
.mini-bar.positive { background: #c6f6d5; }
.mini-bar.neutral { background: #fefcbf; }
.mini-bar.negative { background: #fed7d7; }
.mini-label { font-size: 18rpx; color: #333; }
.keyword-total {
  width: 80rpx;
  font-size: 22rpx;
  color: #999;
  text-align: right;
}
.legend {
  display: flex;
  gap: 24rpx;
  margin-top: 12rpx;
  justify-content: center;
}
.legend-item {
  font-size: 22rpx;
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
}
.legend-item.positive { background: #c6f6d5; color: #38a169; }
.legend-item.neutral { background: #fefcbf; color: #d69e2e; }
.legend-item.negative { background: #fed7d7; color: #e53e3e; }
</style>
