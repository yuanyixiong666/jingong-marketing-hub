<template>
  <view class="container">
    <view class="card">
      <text class="card-title">智能报告</text>
      <text class="desc">AI大模型自动生成数据分析报告（通义千问）</text>
    </view>

    <!-- 报告生成按钮 -->
    <view class="card">
      <view class="report-actions">
        <button class="gen-btn" :disabled="loading" @click="generateDaily">
          {{ loading && reportType === 'daily' ? "AI生成中..." : "生成日报" }}
        </button>
        <button class="gen-btn secondary" :disabled="loading" @click="generateWeekly">
          {{ loading && reportType === 'weekly' ? "AI生成中..." : "生成周报" }}
        </button>
      </view>
      <view v-if="loading" class="loading-tip">
        <view class="loading-dot"></view>
        <text class="loading-text">AI正在分析数据并生成报告，请稍候...</text>
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

    <!-- AI情感分析 -->
    <view class="card">
      <text class="card-title">AI情感分析</text>
      <text class="desc">输入文本，AI自动分析情感倾向</text>
      <view class="ai-input-wrap">
        <textarea class="ai-input" v-model="analyzeText" placeholder="输入要分析的文本内容..." :maxlength="500" />
        <view class="ai-keyword-row">
          <text class="ai-keyword-label">关联关键词：</text>
          <input class="ai-keyword-input" v-model="analyzeKeyword" placeholder="如：零添加酱油" />
        </view>
        <button class="analyze-btn" :disabled="aiAnalyzing || !analyzeText" @click="doAnalyze">
          {{ aiAnalyzing ? "AI分析中..." : "开始分析" }}
        </button>
      </view>
      <!-- AI分析结果 -->
      <view v-if="aiResult" class="ai-result">
        <view class="ai-result-header">
          <view class="sentiment-tag" :class="'sentiment-' + (aiResult.sentiment || 'neutral')">
            <text>{{ sentimentLabel(aiResult.sentiment) }}</text>
          </view>
          <text class="ai-score">置信度: {{ Math.round((aiResult.score || 0) * 100) }}%</text>
        </view>
        <text class="ai-summary">{{ aiResult.summary }}</text>
        <view v-if="aiResult.keywords && aiResult.keywords.length" class="ai-keywords">
          <text v-for="(kw, idx) in aiResult.keywords" :key="idx" class="ai-kw-tag">{{ kw }}</text>
        </view>
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
 * AI生成：调用通义千问LLM生成日报/周报 + AI情感分析
 * 人工修改：完善报告展示、添加AI情感分析交互
 */
import { generateReport, getPlatformStats, getSentimentStats, getCompetitors, analyzeSentiment } from "@/utils/api"

export default {
  data() {
    return {
      reportContent: "",
      reportTitle: "",
      generateTime: "",
      loading: false,
      reportType: "",
      summary: {
        totalData: 0,
        totalSentiment: 0,
        competitors: 0,
        positiveRate: 0,
      },
      // AI情感分析
      analyzeText: "",
      analyzeKeyword: "",
      aiAnalyzing: false,
      aiResult: null,
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
      this.reportType = "daily"
      try {
        const res = await generateReport({ type: "daily" })
        if (res.code === 200) {
          this.reportContent = res.data
          this.reportTitle = "金宫味业数字营销日报"
          this.generateTime = new Date().toLocaleString()
        } else {
          uni.showToast({ title: res.message || "生成失败", icon: "none" })
        }
      } catch (e) {
        uni.showToast({ title: "生成失败", icon: "none" })
      } finally {
        this.loading = false
      }
    },
    async generateWeekly() {
      this.loading = true
      this.reportType = "weekly"
      try {
        const res = await generateReport({ type: "weekly" })
        if (res.code === 200) {
          this.reportContent = res.data
          this.reportTitle = "金宫味业数字营销周报"
          this.generateTime = new Date().toLocaleString()
        } else {
          uni.showToast({ title: res.message || "生成失败", icon: "none" })
        }
      } catch (e) {
        uni.showToast({ title: "生成失败", icon: "none" })
      } finally {
        this.loading = false
      }
    },
    async doAnalyze() {
      if (!this.analyzeText.trim()) return
      this.aiAnalyzing = true
      this.aiResult = null
      try {
        const res = await analyzeSentiment({
          text: this.analyzeText,
          keyword: this.analyzeKeyword,
        })
        if (res.code === 200 && res.data) {
          this.aiResult = res.data
        } else {
          uni.showToast({ title: res.message || "分析失败", icon: "none" })
        }
      } catch (e) {
        uni.showToast({ title: "AI分析失败", icon: "none" })
      } finally {
        this.aiAnalyzing = false
      }
    },
    sentimentLabel(s) {
      const map = { positive: "正面", negative: "负面", neutral: "中性" }
      return map[s] || "未知"
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

/* 加载动画 */
.loading-tip { display: flex; align-items: center; gap: 12rpx; margin-top: 20rpx; justify-content: center; }
.loading-dot {
  width: 16rpx; height: 16rpx; border-radius: 50%;
  background: #1e3a5f;
  animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse { 0%,100% { opacity: 0.3; transform: scale(0.8); } 50% { opacity: 1; transform: scale(1.2); } }
.loading-text { font-size: 24rpx; color: #888; }

.report-content {
  padding: 24rpx;
  background: #f8fafc;
  border-radius: 12rpx;
  line-height: 1.8;
  font-size: 26rpx;
  color: #333;
  white-space: pre-wrap;
  max-height: 800rpx;
  overflow-y: auto;
}
.report-footer {
  margin-top: 16rpx;
  padding-top: 16rpx;
  border-top: 1rpx solid #f0f0f0;
}
.footer-text { font-size: 22rpx; color: #999; }

/* AI情感分析 */
.ai-input-wrap { margin-top: 20rpx; }
.ai-input {
  width: 100%;
  height: 180rpx;
  padding: 20rpx;
  background: #f8fafc;
  border-radius: 12rpx;
  font-size: 28rpx;
  border: 2rpx solid #e2e8f0;
  box-sizing: border-box;
}
.ai-keyword-row { display: flex; align-items: center; margin-top: 16rpx; gap: 12rpx; }
.ai-keyword-label { font-size: 26rpx; color: #666; white-space: nowrap; }
.ai-keyword-input {
  flex: 1;
  padding: 12rpx 20rpx;
  background: #f8fafc;
  border-radius: 8rpx;
  font-size: 26rpx;
  border: 2rpx solid #e2e8f0;
}
.analyze-btn {
  margin-top: 20rpx;
  background: #2c5282;
  color: #fff;
  border-radius: 12rpx;
  font-size: 28rpx;
  padding: 18rpx 0;
}
.analyze-btn[disabled] { opacity: 0.5; }

/* AI分析结果 */
.ai-result {
  margin-top: 24rpx;
  padding: 24rpx;
  background: #f0f7ff;
  border-radius: 12rpx;
  border-left: 6rpx solid #2c5282;
}
.ai-result-header { display: flex; align-items: center; gap: 20rpx; margin-bottom: 16rpx; }
.sentiment-tag {
  padding: 6rpx 20rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
  color: #fff;
}
.sentiment-positive { background: #38a169; }
.sentiment-negative { background: #e53e3e; }
.sentiment-neutral { background: #a0aec0; }
.ai-score { font-size: 26rpx; color: #555; }
.ai-summary { font-size: 28rpx; color: #333; line-height: 1.6; display: block; }
.ai-keywords { display: flex; flex-wrap: wrap; gap: 12rpx; margin-top: 16rpx; }
.ai-kw-tag {
  padding: 6rpx 16rpx;
  background: #e2e8f0;
  border-radius: 16rpx;
  font-size: 22rpx;
  color: #555;
}

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
