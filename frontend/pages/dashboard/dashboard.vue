<template>
  <view class="container">
    <view class="card">
      <text class="card-title">营销战情室</text>
      <text class="desc">实时数据可视化大屏</text>
    </view>

    <!-- 图表1: 柱状图 - 各平台数据量对比 -->
    <view class="card chart-card">
      <text class="card-title">各平台数据量对比</text>
      <EChartsCanvas
        canvasId="barChart"
        :width="340"
        :height="260"
        chartType="bar"
        :chartData="barChartData"
      />
    </view>

    <!-- 图表2: 饼图 - 舆情情感分布 -->
    <view class="card chart-card">
      <text class="card-title">舆情情感分布</text>
      <EChartsCanvas
        canvasId="pieChart"
        :width="340"
        :height="280"
        chartType="pie"
        :chartData="pieChartData"
      />
      <view class="sentiment-summary">
        <text class="summary-text">共 {{ totalSentiment }} 条舆情，正面占比 {{ positivePercent }}%</text>
      </view>
    </view>

    <!-- 图表3: 折线图 - 关键词情感趋势 -->
    <view class="card chart-card">
      <text class="card-title">关键词情感分布</text>
      <EChartsCanvas
        canvasId="lineChart"
        :width="340"
        :height="280"
        chartType="line"
        :chartData="lineChartData"
      />
    </view>

    <!-- 图表4: 柱状图 - 平台互动量 -->
    <view class="card chart-card">
      <text class="card-title">各平台互动量</text>
      <EChartsCanvas
        canvasId="barChart2"
        :width="340"
        :height="260"
        chartType="bar"
        :chartData="engagementChartData"
      />
    </view>
  </view>
</template>

<script>
/**
 * 营销战情室 - 数据可视化
 * AI生成：ECharts 图表渲染组件集成
 * 人工修改：对接真实API数据，使用 echarts-for-weixin 适配方案
 * 图表类型：柱状图(bar)、饼图(pie)、折线图(line) — 共3种
 */
import { getPlatformStats, getSentimentStats } from "@/utils/api"
import EChartsCanvas from "@/components/EChartsCanvas.vue"

const COLORS = ["#3182ce", "#38a169", "#d69e2e", "#e53e3e", "#805ad5"]

export default {
  components: { EChartsCanvas },
  data() {
    return {
      barChartData: { title: "", categories: [], series: [] },
      pieChartData: { title: "", pieData: [] },
      lineChartData: { title: "", categories: [], series: [] },
      engagementChartData: { title: "", categories: [], series: [] },
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

        // 柱状图：各平台数据量
        if (statsRes.code === 200 && statsRes.data) {
          const nameMap = { douyin: "抖音", xiaohongshu: "小红书", tmall: "天猫", jd: "京东", weibo: "微博" }
          const categories = statsRes.data.map(item => nameMap[item.platform] || item.platform)
          const values = statsRes.data.map(item => item.total)
          this.barChartData = {
            title: "",
            categories,
            series: [{ name: "数据量", data: values }],
          }

          // 互动量柱状图
          const likesData = statsRes.data.map(item => item.total_likes || 0)
          this.engagementChartData = {
            title: "",
            categories,
            series: [{ name: "互动量", data: likesData }],
          }
        }

        // 饼图：舆情情感分布
        if (sentRes.code === 200 && sentRes.data) {
          const dist = sentRes.data.distribution || {}
          const totalS = (dist.positive || 0) + (dist.neutral || 0) + (dist.negative || 0)
          this.totalSentiment = totalS
          this.positivePercent = totalS > 0 ? Math.round(((dist.positive || 0) / totalS) * 100) : 0

          this.pieChartData = {
            title: "",
            pieData: [
              { name: "正面", value: dist.positive || 0 },
              { name: "中性", value: dist.neutral || 0 },
              { name: "负面", value: dist.negative || 0 },
            ],
          }

          // 折线图：关键词情感分布
          const byKeyword = sentRes.data.by_keyword || []
          const kwCategories = byKeyword.map(k => k.keyword)
          this.lineChartData = {
            title: "",
            categories: kwCategories,
            series: [
              { name: "正面", data: byKeyword.map(k => k.positive || 0) },
              { name: "中性", data: byKeyword.map(k => k.neutral || 0) },
              { name: "负面", data: byKeyword.map(k => k.negative || 0) },
            ],
          }
        }
      } catch (e) {
        console.log("数据加载失败", e)
      }
    },
  },
}
</script>

<style scoped>
.desc { color: #666; font-size: 26rpx; display: block; margin-top: 8rpx; }
.chart-card { margin-top: 20rpx; }
.sentiment-summary {
  margin-top: 8rpx;
  padding: 12rpx;
  background: #f8fafc;
  border-radius: 8rpx;
}
.summary-text { font-size: 24rpx; color: #666; }
</style>
