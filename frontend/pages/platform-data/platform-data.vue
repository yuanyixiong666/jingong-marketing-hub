<template>
  <view class="container">
    <!-- 平台概览 -->
    <view class="card">
      <view class="platform-header">
        <u-avatar :text="platformIcon" size="64" bgColor="#e8f0fe" color="#2c5282"></u-avatar>
        <view class="platform-info">
          <text class="platform-title">{{ platformName }}</text>
          <text class="platform-sub">共 {{ total }} 条采集数据</text>
        </view>
      </view>
    </view>

    <!-- 数据列表 -->
    <view class="card" v-if="dataList.length > 0">
      <text class="card-title">数据明细</text>
      <view class="data-list">
        <view class="data-item" v-for="item in dataList" :key="item.id">
          <view class="data-top">
            <text class="data-title">{{ item.title || '无标题' }}</text>
            <text class="data-type" v-if="item.content_type">{{ contentTypeMap[item.content_type] || item.content_type }}</text>
          </view>
          <view class="data-metrics">
            <text class="metric" v-if="item.price != null">¥{{ item.price }}</text>
            <text class="metric" v-if="item.sales_volume != null">销量 {{ item.sales_volume }}</text>
            <text class="metric">{{ item.likes }} 赞</text>
            <text class="metric">{{ item.comments_count }} 评论</text>
          </view>
          <text class="data-time">{{ formatTime(item.crawled_at) }}</text>
        </view>
      </view>
      <view class="load-more" v-if="hasMore" @click="loadMore">
        <text class="load-more-text">加载更多</text>
      </view>
      <view class="no-more" v-else>
        <text class="no-more-text">已加载全部数据</text>
      </view>
    </view>

    <view class="card empty-card" v-else-if="!loading">
      <text class="empty-text">暂无 {{ platformName }} 平台数据</text>
    </view>
  </view>
</template>

<script>
import { getPlatformData } from "@/utils/api"

export default {
  data() {
    return {
      platformName: "",
      platformKey: "",
      platformIcon: "",
      dataList: [],
      total: 0,
      page: 1,
      pageSize: 20,
      hasMore: false,
      loading: false,
      contentTypeMap: {
        product: "商品",
        review: "评价",
        post: "帖子",
        hot_list: "热榜",
      },
      nameToKey: {
        "抖音": "douyin",
        "小红书": "xiaohongshu",
        "天猫": "tmall",
        "京东": "jd",
        "微博": "weibo",
      },
      keyToIcon: {
        douyin: "D",
        xiaohongshu: "X",
        tmall: "T",
        jd: "J",
        weibo: "W",
      },
    }
  },
  async onLoad(options) {
    this.platformName = decodeURIComponent(options.name || "未知平台")
    this.platformIcon = options.icon || "P"
    this.platformKey = this.nameToKey[this.platformName] || this.platformName
    await this.fetchData()
  },
  methods: {
    async fetchData() {
      if (this.loading) return
      this.loading = true
      try {
        const res = await getPlatformData({
          platform: this.platformKey,
          page: this.page,
          page_size: this.pageSize,
        })
        if (res.code === 200) {
          this.dataList = res.data || []
          this.total = res.total || 0
          this.hasMore = this.page * this.pageSize < this.total
        }
      } catch (e) {
        console.log("加载平台数据失败", e)
      } finally {
        this.loading = false
      }
    },
    async loadMore() {
      if (!this.hasMore || this.loading) return
      this.page++
      try {
        this.loading = true
        const res = await getPlatformData({
          platform: this.platformKey,
          page: this.page,
          page_size: this.pageSize,
        })
        if (res.code === 200) {
          this.dataList = this.dataList.concat(res.data || [])
          this.hasMore = this.page * this.pageSize < this.total
        }
      } catch (e) {
        console.log("加载更多失败", e)
        this.page--
      } finally {
        this.loading = false
      }
    },
    formatTime(t) {
      if (!t) return "未知时间"
      const d = new Date(t)
      const m = String(d.getMonth() + 1).padStart(2, "0")
      const day = String(d.getDate()).padStart(2, "0")
      const h = String(d.getHours()).padStart(2, "0")
      const min = String(d.getMinutes()).padStart(2, "0")
      return `${m}-${day} ${h}:${min}`
    },
  },
}
</script>

<style scoped>
.platform-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
}
.platform-info { flex: 1; }
.platform-title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: #1e3a5f;
}
.platform-sub {
  display: block;
  font-size: 26rpx;
  color: #999;
  margin-top: 6rpx;
}
.data-list { display: flex; flex-direction: column; }
.data-item {
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}
.data-item:last-child { border-bottom: none; }
.data-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12rpx;
}
.data-title {
  flex: 1;
  font-size: 28rpx;
  color: #333;
  line-height: 1.4;
}
.data-type {
  font-size: 22rpx;
  padding: 4rpx 12rpx;
  background: #e8f0fe;
  color: #2c5282;
  border-radius: 6rpx;
  flex-shrink: 0;
  margin-left: 12rpx;
}
.data-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 8rpx;
}
.metric {
  font-size: 24rpx;
  color: #666;
}
.data-time {
  font-size: 22rpx;
  color: #bbb;
}
.load-more {
  text-align: center;
  padding: 24rpx 0;
}
.load-more-text {
  color: #3182ce;
  font-size: 26rpx;
}
.no-more {
  text-align: center;
  padding: 24rpx 0;
}
.no-more-text {
  color: #ccc;
  font-size: 24rpx;
}
.empty-card { text-align: center; padding: 60rpx 0; }
.empty-text { color: #999; font-size: 28rpx; }
</style>
