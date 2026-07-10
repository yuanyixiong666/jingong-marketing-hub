<template>
  <view class="container">
    <view class="card">
      <text class="card-title">智能报告</text>
      <text class="desc">AI自动生成数据分析报告</text>
    </view>

    <!-- 报告生成按钮 -->
    <view class="card">
      <view class="report-actions">
        <button class="gen-btn" @click="generateDaily">生成日报</button>
        <button class="gen-btn secondary" @click="generateWeekly">生成周报</button>
      </view>
    </view>

    <!-- 报告内容展示 -->
    <view class="card" v-if="reportContent">
      <text class="card-title">报告内容</text>
      <view class="report-content">
        <text>{{ reportContent }}</text>
      </view>
    </view>

    <!-- 历史报告 -->
    <view class="card">
      <text class="card-title">历史报告</text>
      <text class="empty-text">暂无历史报告</text>
    </view>
  </view>
</template>

<script>
/**
 * 智能报告页面
 * AI生成：调用AI接口生成日报/周报
 */
import { generateReport } from "@/utils/api"

export default {
  data() {
    return {
      reportContent: "",
    }
  },
  methods: {
    async generateDaily() {
      uni.showLoading({ title: "AI生成中..." })
      try {
        const res = await generateReport({ type: "daily" })
        this.reportContent = res.data || "报告生成失败"
      } catch (e) {
        this.reportContent = "生成失败，请检查后端服务"
      } finally {
        uni.hideLoading()
      }
    },
    async generateWeekly() {
      uni.showLoading({ title: "AI生成中..." })
      try {
        const res = await generateReport({ type: "weekly" })
        this.reportContent = res.data || "报告生成失败"
      } catch (e) {
        this.reportContent = "生成失败，请检查后端服务"
      } finally {
        uni.hideLoading()
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
.report-content {
  padding: 20rpx;
  background: #f8fafc;
  border-radius: 12rpx;
  line-height: 1.8;
  font-size: 28rpx;
  color: #333;
}
.empty-text { color: #ccc; text-align: center; padding: 40rpx 0; }
</style>
