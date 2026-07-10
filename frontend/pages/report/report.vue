<template>
  <view class="container">
    <view class="card">
      <text class="card-title">智能报告</text>
      <text class="desc">AI自动生成数据分析报告</text>
    </view>

    <!-- 报告生成按钮 -->
    <view class="card">
      <view class="report-actions">
        <button class="gen-btn" :disabled="loading" @click="generateDaily">
          {{ loading ? "生成中..." : "生成日报" }}
        </button>
        <button class="gen-btn secondary" :disabled="loading" @click="generateWeekly">
          {{ loading ? "生成中..." : "生成周报" }}
        </button>
      </view>
    </view>

    <!-- 报告内容展示 -->
    <view class="card" v-if="reportContent">
      <text class="card-title">{{ reportTitle }}</text>
      <view class="report-content">
        <text>{{ reportContent }}</text>
      </view>
      <view class="report-footer">
        <text class="footer-text">生成时间: {{ generateTime }}</text>
      </view>
    </view>

    <!-- 数据摘要 -->
    <view class="card">
      <text class="card-title">数据摘要</text>
      <view class="summary-grid">
        <view class="summary-item">
          <text class="summary-value">{{ summary.totalData }}</text>
          <text class="summary-label">总数据量</text>
        </view>
        <view class="summary-item">
          <text class="summary-value">{{ summary.totalSentiment }}</text>
          <text class="summary-label">舆情条数</text>
        </view>
        <view class="summary-item">
          <text class="summary-value">{{ summary.competitors }}</text>
          <text class="summary-label">监控竞品</text>
        </view>
        <view class="summary-item">
          <text class="summary-value">{{ summary.positiveRate }}%</text>
          <text class="summary-label">正面舆情率</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
/**
 * 智能报告页面
 * AI生成：调用AI接口生成日报/周报
 * 人工修改：完善报告展示和数据摘要
 */
import { generateReport, getPlatformStats, getSentimentStats, getCompetitors } from "@/utils/api"

export default {
  data() {
    return {
      reportContent: "",
      reportTitle: "",
      generateTime: "",
      loading: false,
      summary: {
        totalData: 0,
        totalSentiment: 0,
        competitors: 0,
        positiveRate: 0,
      },
    }
  },
  onShow() {
    this.loadSummary()
  },
  methods: {
    async loadSummary() {
      try {
        const [statsRes, sentRes, compRes] = await Promise.all([
          getPlatformStats(),
          getSentimentStats(),
          getCompetitors(),
        ])
        if (statsRes.code === 200) {
          this.summary.totalData = (statsRes.data || []).reduce((s, p) => s + p.total, 0)
        }
        if (sentRes.code === 200 && sentRes.data) {
          const dist = sentRes.data.distribution || {}
          const total = (dist.positive || 0) + (dist.neutral || 0) + (dist.negative || 0)
          this.summary.totalSentiment = total
          this.summary.positiveRate = total > 0 ? Math.round(((dist.positive || 0) / total) * 100) : 0
        }
        if (compRes.code === 200) {
          this.summary.competitors = (compRes.data || []).length
        }
      } catch (e) {
        console.log("摘要加载失败", e)
      }
    },
    async generateDaily() {
      this.loading = true
      try {
        const res = await generateReport({ type: "daily" })
        if (res.code === 200) {
          this.reportContent = res.data
          this.reportTitle = "金宫味业数字营销日报"
          this.generateTime = new Date().toLocaleString()
        }
      } catch (e) {
        uni.showToast({ title: "生成失败", icon: "none" })
      } finally {
        this.loading = false
      }
    },
    async generateWeekly() {
      this.loading = true
      try {
        const res = await generateReport({ type: "weekly" })
        if (res.code === 200) {
          this.reportContent = res.data
          this.reportTitle = "金宫味业数字营销周报"
          this.generateTime = new Date().toLocaleString()
        }
      } catch (e) {
        uni.showToast({ title: "生成失败", icon: "none" })
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.desc { color: #666; font-size: 26rpx; display: block; margin-top: 8rpx; }
.report-actions { display: flex; gap: 20rpx; }
.gen-btn {
  flex: 1;
  background: #1e3a5f;
  color: #fff;
  border-radius: 12rpx;
  font-size: 30rpx;
  padding: 20rpx 0;
}
.gen-btn.secondary { background: #fff; color: #1e3a5f; border: 2rpx solid #1e3a5f; }
.gen-btn[disabled] { opacity: 0.6; }
.report-content {
  padding: 24rpx;
  background: #f8fafc;
  border-radius: 12rpx;
  line-height: 1.8;
  font-size: 26rpx;
  color: #333;
  white-space: pre-wrap;
  max-height: 600rpx;
  overflow-y: auto;
}
.report-footer {
  margin-top: 16rpx;
  padding-top: 16rpx;
  border-top: 1rpx solid #f0f0f0;
}
.footer-text { font-size: 22rpx; color: #999; }
.summary-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}
.summary-item {
  flex: 1;
  min-width: 45%;
  text-align: center;
  padding: 24rpx;
  background: #f8fafc;
  border-radius: 12rpx;
}
.summary-value { display: block; font-size: 40rpx; font-weight: 700; color: #2c5282; }
.summary-label { display: block; font-size: 24rpx; color: #999; margin-top: 8rpx; }
</style>
