<template>
  <view class="container">
    <view class="card">
      <text class="card-title">营销战情室</text>
      <text class="desc">实时GMV、平台流量占比、竞品价格带、舆情趋势</text>
    </view>

    <!-- 图表区域（ECharts占位） -->
    <view class="card chart-card">
      <text class="card-title">各平台数据占比</text>
      <view id="pieChart" class="chart-container">
        <text class="chart-placeholder">ECharts 饼图（待接入）</text>
      </view>
    </view>

    <view class="card chart-card">
      <text class="card-title">舆情情感趋势</text>
      <view id="lineChart" class="chart-container">
        <text class="chart-placeholder">ECharts 折线图（待接入）</text>
      </view>
    </view>

    <view class="card chart-card">
      <text class="card-title">竞品价格带分布</text>
      <view id="barChart" class="chart-container">
        <text class="chart-placeholder">ECharts 柱状图（待接入）</text>
      </view>
    </view>
  </view>
</template>

<script>
/**
 * 营销战情室 - 数据可视化大屏
 * AI生成：图表容器和布局，ECharts-for-weixin待接入
 */
export default {
  data() {
    return {}
  },
  onReady() {
    // TODO: 初始化ECharts图表
    // import * as echarts from "echarts-for-weixin"
  },
}
</script>

<style scoped>
.desc { color: #666; font-size: 26rpx; }
.chart-card { margin-top: 20rpx; }
.chart-container {
  height: 400rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border-radius: 12rpx;
  margin-top: 16rpx;
}
.chart-placeholder { color: #aaa; font-size: 28rpx; }
</style>
