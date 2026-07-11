<template>
  <view class="container">
    <!-- 情感分布概览 -->
    <view class="card">
      <text class="card-title">舆情概览</text>
      <view class="sentiment-grid">
        <view class="sentiment-item positive">
          <text class="sentiment-count">{{ distribution.positive || 0 }}</text>
          <text class="sentiment-label">正面</text>
        </view>
        <view class="sentiment-item neutral">
          <text class="sentiment-count">{{ distribution.neutral || 0 }}</text>
          <text class="sentiment-label">中性</text>
        </view>
        <view class="sentiment-item negative">
          <text class="sentiment-count">{{ distribution.negative || 0 }}</text>
          <text class="sentiment-label">负面</text>
        </view>
      </view>
    </view>

    <!-- 筛选 -->
    <view class="card filter-card">
      <view class="filter-tabs">
        <text class="filter-tab" :class="{ active: currentFilter === '' }" @click="switchFilter('')">全部</text>
        <text class="filter-tab" :class="{ active: currentFilter === 'negative' }" @click="switchFilter('negative')">负面</text>
        <text class="filter-tab" :class="{ active: currentFilter === 'positive' }" @click="switchFilter('positive')">正面</text>
        <text class="filter-tab" :class="{ active: currentFilter === 'neutral' }" @click="switchFilter('neutral')">中性</text>
      </view>
    </view>

    <!-- 舆情列表 -->
    <view class="card">
      <text class="card-title">舆情明细</text>
      <view class="item-list" v-if="items.length > 0">
        <view class="item-row" v-for="item in items" :key="item.id">
          <view class="item-left">
            <text class="item-title">{{ item.title || item.content || '无标题' }}</text>
            <view class="item-meta">
              <text class="item-platform">{{ item.platform || '-' }}</text>
              <text class="item-keyword">{{ item.keyword || '-' }}</text>
            </view>
          </view>
          <text class="item-badge" :class="item.sentiment">{{ sentimentLabel(item.sentiment) }}</text>
        </view>
      </view>
      <view class="empty" v-else>
        <text class="empty-text">暂无舆情数据</text>
      </view>
    </view>
  </view>
</template>

<script>
import { getSentimentList, getSentimentStats } from "@/utils/api"

export default {
  data() {
    return {
      items: [],
      distribution: {},
      currentFilter: "",
    }
  },
  async onLoad(options) {
    if (options.filter) {
      this.currentFilter = options.filter
    }
    await this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const params = {}
        if (this.currentFilter) params.sentiment = this.currentFilter
        const [listRes, statsRes] = await Promise.all([
          getSentimentList(params),
          getSentimentStats(),
        ])
        if (listRes.code === 200) {
          this.items = listRes.data || []
        }
        if (statsRes.code === 200 && statsRes.data) {
          this.distribution = statsRes.data.distribution || {}
        }
      } catch (e) {
        console.log("加载失败", e)
      }
    },
    switchFilter(filter) {
      this.currentFilter = filter
      this.loadData()
    },
    sentimentLabel(s) {
      const map = { positive: "正面", negative: "负面", neutral: "中性" }
      return map[s] || s || "未知"
    },
  },
}
</script>

<style scoped>
.sentiment-grid {
  display: flex;
  gap: 16rpx;
}
.sentiment-item {
  flex: 1;
  text-align: center;
  padding: 24rpx 0;
  border-radius: 12rpx;
}
.sentiment-item.positive { background: #f0fff4; }
.sentiment-item.neutral { background: #f7fafc; }
.sentiment-item.negative { background: #fff5f5; }
.sentiment-count {
  display: block;
  font-size: 40rpx;
  font-weight: 700;
}
.sentiment-item.positive .sentiment-count { color: #38a169; }
.sentiment-item.neutral .sentiment-count { color: #718096; }
.sentiment-item.negative .sentiment-count { color: #e53e3e; }
.sentiment-label {
  display: block;
  font-size: 24rpx;
  color: #999;
  margin-top: 8rpx;
}
.filter-card { padding: 16rpx 24rpx; }
.filter-tabs {
  display: flex;
  gap: 16rpx;
}
.filter-tab {
  font-size: 26rpx;
  padding: 10rpx 28rpx;
  border-radius: 24rpx;
  background: #f0f0f0;
  color: #666;
}
.filter-tab.active {
  background: #2c5282;
  color: #fff;
}
.item-list { display: flex; flex-direction: column; }
.item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}
.item-row:last-child { border-bottom: none; }
.item-left { flex: 1; margin-right: 16rpx; }
.item-title {
  display: block;
  font-size: 28rpx;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 400rpx;
}
.item-meta {
  display: flex;
  gap: 12rpx;
  margin-top: 8rpx;
}
.item-platform, .item-keyword {
  font-size: 22rpx;
  color: #999;
}
.item-keyword {
  padding: 2rpx 10rpx;
  background: #e8f0fe;
  color: #2c5282;
  border-radius: 6rpx;
}
.item-badge {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
  flex-shrink: 0;
}
.item-badge.positive { background: #c6f6d5; color: #38a169; }
.item-badge.negative { background: #fed7d7; color: #e53e3e; }
.item-badge.neutral { background: #f0f0f0; color: #718096; }
.empty { text-align: center; padding: 40rpx 0; }
.empty-text { color: #999; font-size: 26rpx; }
</style>
