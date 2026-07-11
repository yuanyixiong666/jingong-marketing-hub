<template>
  <view class="container">
    <view class="card" v-if="competitor.id">
      <text class="card-title">{{ competitor.brand_name }}</text>
      <view class="detail-row">
        <text class="detail-label">监控关键词</text>
        <view class="tag-list">
          <text class="tag" v-for="kw in keywords" :key="kw">{{ kw }}</text>
        </view>
      </view>
      <view class="detail-row" v-if="competitor.description">
        <text class="detail-label">品牌描述</text>
        <text class="detail-value">{{ competitor.description }}</text>
      </view>
      <view class="detail-row">
        <text class="detail-label">状态</text>
        <text class="detail-value" :class="competitor.is_active ? 'active' : 'inactive'">
          {{ competitor.is_active ? '监控中' : '已停用' }}
        </text>
      </view>
    </view>

    <view class="card">
      <text class="card-title">价格追踪</text>
      <view class="price-list" v-if="prices.length > 0">
        <view class="price-item" v-for="p in prices" :key="p.id">
          <view class="price-left">
            <text class="price-product">{{ p.product_name || '未知商品' }}</text>
            <text class="price-meta">{{ p.platform }} | {{ formatTime(p.crawled_at) }}</text>
          </view>
          <view class="price-right">
            <text class="price-now">{{ p.price }}元</text>
            <text class="price-was" v-if="p.original_price">原价{{ p.original_price }}元</text>
          </view>
        </view>
      </view>
      <view class="empty" v-else>
        <text class="empty-text">暂无价格数据</text>
      </view>
    </view>
  </view>
</template>

<script>
import { getCompetitors, getCompetitorPrices } from "@/utils/api"

export default {
  data() {
    return {
      competitor: {},
      prices: [],
    }
  },
  computed: {
    keywords() {
      return (this.competitor.keywords || "").split(",").filter(Boolean)
    },
  },
  async onLoad(options) {
    const id = options.id
    if (!id) return
    try {
      const [compRes, priceRes] = await Promise.all([
        getCompetitors(),
        getCompetitorPrices(id),
      ])
      if (compRes.code === 200) {
        this.competitor = compRes.data.find((c) => c.id === Number(id)) || {}
      }
      if (priceRes.code === 200) {
        this.prices = priceRes.data || []
      }
    } catch (e) {
      console.log("加载失败", e)
    }
  },
  methods: {
    formatTime(t) {
      if (!t) return "-"
      return new Date(t).toLocaleDateString()
    },
  },
}
</script>

<style scoped>
.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}
.detail-row:last-child { border-bottom: none; }
.detail-label { color: #999; font-size: 26rpx; flex-shrink: 0; }
.detail-value { color: #333; font-size: 26rpx; text-align: right; flex: 1; margin-left: 20rpx; }
.detail-value.active { color: #38a169; }
.detail-value.inactive { color: #999; }
.tag-list { display: flex; flex-wrap: wrap; gap: 8rpx; justify-content: flex-end; }
.tag {
  font-size: 22rpx;
  padding: 4rpx 12rpx;
  background: #e8f0fe;
  color: #2c5282;
  border-radius: 6rpx;
}
.price-list { display: flex; flex-direction: column; }
.price-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}
.price-item:last-child { border-bottom: none; }
.price-left { flex: 1; }
.price-product { display: block; font-size: 26rpx; color: #333; }
.price-meta { display: block; font-size: 22rpx; color: #999; margin-top: 6rpx; }
.price-right { text-align: right; }
.price-now { display: block; font-size: 32rpx; font-weight: 600; color: #e53e3e; }
.price-was { display: block; font-size: 22rpx; color: #999; text-decoration: line-through; margin-top: 4rpx; }
.empty { text-align: center; padding: 40rpx 0; }
.empty-text { color: #999; font-size: 26rpx; }
</style>
