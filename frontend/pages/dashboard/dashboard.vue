<template>
  <view class="container">
    <view class="card">
      <text class="card-title">营销战情室</text>
      <text class="desc">实时数据可视化大屏</text>
    </view>

    <!-- 图表1: 柱状图 - 各平台数据量对比 -->
    <view class="card chart-card">
      <text class="card-title">各平台数据量对比</text>
      <EcCanvas canvasId="barChart" :width="340" :height="260" :ec="barEc" />
    </view>

    <!-- 图表2: 饼图 - 舆情情感分布 -->
    <view class="card chart-card">
      <text class="card-title">舆情情感分布</text>
      <EcCanvas canvasId="pieChart" :width="340" :height="280" :ec="pieEc" />
      <view class="sentiment-summary">
        <text class="summary-text">共 {{ sentimentInfo.total }} 条舆情，正面占比 {{ sentimentInfo.percent }}%</text>
      </view>
    </view>

    <!-- 图表3: 折线图 - 关键词情感趋势 -->
    <view class="card chart-card">
      <text class="card-title">关键词情感分布</text>
      <EcCanvas canvasId="lineChart" :width="340" :height="280" :ec="lineEc" />
    </view>

    <!-- 图表4: 柱状图 - 平台互动量 -->
    <view class="card chart-card">
      <text class="card-title">各平台互动量</text>
      <EcCanvas canvasId="barChart2" :width="340" :height="260" :ec="engagementEc" />
    </view>
  </view>
</template>

<script>
/**
 * 营销战情室 - 数据可视化
 * 使用 echarts-for-weixin (ec-canvas) 适配方案
 * 图表类型：柱状图(bar)、饼图(pie)、折线图(line) — 共3种
 */
import { getPlatformStats, getSentimentStats } from "@/utils/api"
import EcCanvas from "@/components/EcCanvas.vue"
import * as echarts from 'echarts/core'
import { BarChart, PieChart, LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([BarChart, PieChart, LineChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer])

const COLORS = ["#3182ce", "#38a169", "#d69e2e", "#e53e3e", "#805ad5"]

export default {
  components: { EcCanvas },
  data() {
    return {
      barEc: { onInit: null },
      pieEc: { onInit: null },
      lineEc: { onInit: null },
      engagementEc: { onInit: null },
      barChartData: { categories: [], series: [] },
      pieChartData: { pieData: [] },
      lineChartData: { categories: [], series: [] },
      engagementChartData: { categories: [], series: [] },
      sentimentInfo: { total: 0, percent: 0 },
      _loading: false,
      _lastLoad: 0,
    }
  },
  created() {
    this.charts = {}
    this.barEc.onInit = this.initBarChart.bind(this)
    this.pieEc.onInit = this.initPieChart.bind(this)
    this.lineEc.onInit = this.initLineChart.bind(this)
    this.engagementEc.onInit = this.initEngagementChart.bind(this)
  },
  onLoad() {
    this.loadData()
  },
  onShow() {
    if (Date.now() - this._lastLoad > 60000) this.loadData()
  },
  methods: {
    // ---- ECharts 初始化回调（由 EcCanvas 调用）----
    initBarChart(canvas, width, height, dpr) {
      const chart = echarts.init(canvas, null, { width, height, devicePixelRatio: dpr })
      this.charts.bar = chart
      if (this.barChartData.categories.length > 0) this._updateBarChart()
      return chart
    },
    initPieChart(canvas, width, height, dpr) {
      const chart = echarts.init(canvas, null, { width, height, devicePixelRatio: dpr })
      this.charts.pie = chart
      if (this.pieChartData.pieData.length > 0) this._updatePieChart()
      return chart
    },
    initLineChart(canvas, width, height, dpr) {
      const chart = echarts.init(canvas, null, { width, height, devicePixelRatio: dpr })
      this.charts.line = chart
      if (this.lineChartData.categories.length > 0) this._updateLineChart()
      return chart
    },
    initEngagementChart(canvas, width, height, dpr) {
      const chart = echarts.init(canvas, null, { width, height, devicePixelRatio: dpr })
      this.charts.engagement = chart
      if (this.engagementChartData.categories.length > 0) this._updateEngagementChart()
      return chart
    },

    // ---- 图表更新方法 ----
    _updateBarChart() {
      if (!this.charts.bar) return
      this.charts.bar.setOption({
        title: { text: '', textStyle: { fontSize: 14, color: '#333' } },
        tooltip: { trigger: 'axis' },
        grid: { left: 40, right: 20, top: 40, bottom: 30 },
        xAxis: { type: 'category', data: this.barChartData.categories, axisLabel: { fontSize: 11 } },
        yAxis: { type: 'value', axisLabel: { fontSize: 11 } },
        series: this.barChartData.series.map((s, i) => ({
          name: s.name || '',
          type: 'bar',
          data: s.data || [],
          itemStyle: { color: COLORS[i % COLORS.length] },
        })),
      }, true)
    },
    _updatePieChart() {
      if (!this.charts.pie) return
      this.charts.pie.setOption({
        title: { text: '', textStyle: { fontSize: 14, color: '#333' }, left: 'center' },
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        legend: { bottom: 0, textStyle: { fontSize: 11 } },
        series: [{
          type: 'pie',
          radius: ['35%', '60%'],
          data: this.pieChartData.pieData.map((item, i) => ({
            name: item.name,
            value: item.value,
            itemStyle: { color: COLORS[i % COLORS.length] },
          })),
          emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.3)' } },
        }],
      }, true)
    },
    _updateLineChart() {
      if (!this.charts.line) return
      this.charts.line.setOption({
        title: { text: '', textStyle: { fontSize: 14, color: '#333' } },
        tooltip: { trigger: 'axis' },
        grid: { left: 40, right: 20, top: 40, bottom: 30 },
        xAxis: { type: 'category', data: this.lineChartData.categories, axisLabel: { fontSize: 11 } },
        yAxis: { type: 'value', axisLabel: { fontSize: 11 } },
        series: this.lineChartData.series.map((s, i) => ({
          name: s.name || '',
          type: 'line',
          smooth: true,
          data: s.data || [],
          itemStyle: { color: COLORS[i % COLORS.length] },
          areaStyle: { opacity: 0.15 },
        })),
      }, true)
    },
    _updateEngagementChart() {
      if (!this.charts.engagement) return
      this.charts.engagement.setOption({
        title: { text: '', textStyle: { fontSize: 14, color: '#333' } },
        tooltip: {
          trigger: 'axis',
          formatter: function(params) {
            var p = params[0]
            var val = p.value
            var formatted = val >= 10000 ? (val / 10000).toFixed(1) + '万' : val
            return p.name + '<br/>' + p.seriesName + ': ' + formatted
          }
        },
        grid: { left: 50, right: 20, top: 40, bottom: 30 },
        xAxis: { type: 'category', data: this.engagementChartData.categories, axisLabel: { fontSize: 11 } },
        yAxis: {
          type: 'value',
          axisLabel: {
            fontSize: 11,
            formatter: function(value) {
              return value >= 10000 ? (value / 10000).toFixed(0) + '万' : value
            }
          }
        },
        series: this.engagementChartData.series.map((s, i) => ({
          name: s.name || '',
          type: 'bar',
          data: s.data || [],
          itemStyle: { color: COLORS[i % COLORS.length] },
        })),
      }, true)
    },

    // ---- 数据加载 ----
    async loadData() {
      if (this._loading) return
      this._loading = true
      try {
        const [statsRes, sentRes] = await Promise.all([getPlatformStats(), getSentimentStats()])
        if (statsRes.code === 200 && statsRes.data) {
          const nameMap = { douyin: "抖音", xiaohongshu: "小红书", tmall: "天猫", jd: "京东", weibo: "微博" }
          const categories = statsRes.data.map(item => nameMap[item.platform] || item.platform)
          const values = statsRes.data.map(item => item.total)
          this.barChartData = { categories, series: [{ name: "数据量", data: values }] }
          this._updateBarChart()

          const likesData = statsRes.data.map(item => item.total_likes || 0)
          this.engagementChartData = { categories, series: [{ name: "互动量", data: likesData }] }
          this._updateEngagementChart()
        }

        if (sentRes.code === 200 && sentRes.data) {
          const dist = sentRes.data.distribution || {}
          const totalS = (dist.positive || 0) + (dist.neutral || 0) + (dist.negative || 0)
          const percentS = totalS > 0 ? Math.round(((dist.positive || 0) / totalS) * 100) : 0
          this.sentimentInfo = { total: totalS, percent: percentS }
          this.pieChartData = {
            pieData: [
              { name: "正面", value: dist.positive || 0 },
              { name: "中性", value: dist.neutral || 0 },
              { name: "负面", value: dist.negative || 0 },
            ],
          }
          this._updatePieChart()

          const byKeyword = sentRes.data.by_keyword || []
          this.lineChartData = {
            categories: byKeyword.map(k => k.keyword),
            series: [
              { name: "正面", data: byKeyword.map(k => k.positive || 0) },
              { name: "中性", data: byKeyword.map(k => k.neutral || 0) },
              { name: "负面", data: byKeyword.map(k => k.negative || 0) },
            ],
          }
          this._updateLineChart()
        }
      } catch (e) {
        console.log("数据加载失败", e)
      } finally {
        this._loading = false
        this._lastLoad = Date.now()
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
