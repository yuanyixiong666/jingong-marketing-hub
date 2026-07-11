/**
 * ECharts 图表组件 - 封装 echarts-for-weixin 适配层
 * AI生成：ECharts 微信小程序渲染组件
 * 人工修改：支持 bar/pie/line 三种图表类型，适配 uni-app canvas
 *
 * 依赖：echarts + echarts-for-weixin 适配方案
 * 图表类型：柱状图(bar)、饼图(pie)、折线图(line)
 */
<template>
  <view class="echarts-container">
    <canvas
      :id="canvasId"
      :canvas-id="canvasId"
      :style="{ width: canvasWidth + 'px', height: canvasHeight + 'px' }"
      @touchstart="touchStart"
      @touchmove="touchMove"
      @touchend="touchEnd"
    />
  </view>
</template>

<script>
/**
 * echarts-for-weixin 适配组件
 * 支持三种图表类型：bar(柱状图)、pie(饼图)、line(折线图)
 */
import * as echarts from 'echarts/core'
import { BarChart, PieChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([
  BarChart, PieChart, LineChart,
  TitleComponent, TooltipComponent, GridComponent, LegendComponent,
  CanvasRenderer,
])

export default {
  name: 'EChartsCanvas',
  props: {
    canvasId: { type: String, default: 'echarts-canvas' },
    width: { type: [Number, String], default: 375 },
    height: { type: [Number, String], default: 300 },
    chartType: { type: String, default: 'bar' },  // bar | pie | line
    chartData: { type: Object, default: () => ({}) },
  },
  data() {
    return {
      chart: null,
      canvasWidth: 0,
      canvasHeight: 0,
    }
  },
  mounted() {
    const sysInfo = uni.getSystemInfoSync()
    const ratio = sysInfo.pixelRatio || 2
    this.canvasWidth = Number(this.width)
    this.canvasHeight = Number(this.height)
    this.$nextTick(() => {
      this.initChart(ratio)
    })
  },
  watch: {
    chartData: {
      deep: true,
      handler() {
        this.updateChart()
      },
    },
    chartType() {
      this.updateChart()
    },
  },
  methods: {
    initChart(ratio) {
      const query = uni.createSelectorQuery().in(this)
      query
        .select(`#${this.canvasId}`)
        .fields({ node: true, size: true })
        .exec((res) => {
          if (!res[0] || !res[0].node) {
            // 降级：非 H5 环境使用传统方式
            this.initChartLegacy(ratio)
            return
          }
          const canvas = res[0].node
          const ctx = canvas.getContext('2d')
          canvas.width = res[0].width * ratio
          canvas.height = res[0].height * ratio
          ctx.scale(ratio, ratio)

          this.chart = echarts.init(canvas, null, {
            width: res[0].width,
            height: res[0].height,
            devicePixelRatio: ratio,
          })
          this.chart.setContext(ctx)
          this.updateChart()
        })
    },
    initChartLegacy(ratio) {
      // 传统 canvas 初始化（兼容微信小程序）
      const query = uni.createSelectorQuery().in(this)
      query
        .select(`#${this.canvasId}`)
        .boundingClientRect((rect) => {
          if (!rect) return
          this.chart = echarts.init({
            width: rect.width * ratio,
            height: rect.height * ratio,
            devicePixelRatio: ratio,
          })
          this.updateChart()
        })
        .exec()
    },
    updateChart() {
      if (!this.chart) return
      const option = this.getChartOption()
      this.chart.setOption(option, true)
    },
    getChartOption() {
      const { chartType, chartData } = this
      const title = chartData.title || ''
      const categories = chartData.categories || []
      const series = chartData.series || []
      const colors = chartData.colors || ['#3182ce', '#38a169', '#d69e2e', '#e53e3e', '#805ad5']

      if (chartType === 'bar') {
        return {
          title: { text: title, textStyle: { fontSize: 14, color: '#333' } },
          tooltip: { trigger: 'axis' },
          grid: { left: 40, right: 20, top: 40, bottom: 30 },
          xAxis: { type: 'category', data: categories, axisLabel: { fontSize: 11 } },
          yAxis: { type: 'value', axisLabel: { fontSize: 11 } },
          series: series.map((s, i) => ({
            name: s.name || '',
            type: 'bar',
            data: s.data || [],
            itemStyle: { color: colors[i % colors.length] },
          })),
        }
      }

      if (chartType === 'pie') {
        return {
          title: { text: title, textStyle: { fontSize: 14, color: '#333' }, left: 'center' },
          tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
          legend: { bottom: 0, textStyle: { fontSize: 11 } },
          series: [{
            type: 'pie',
            radius: ['35%', '60%'],
            data: (chartData.pieData || []).map((item, i) => ({
              name: item.name,
              value: item.value,
              itemStyle: { color: colors[i % colors.length] },
            })),
            emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.3)' } },
          }],
        }
      }

      if (chartType === 'line') {
        return {
          title: { text: title, textStyle: { fontSize: 14, color: '#333' } },
          tooltip: { trigger: 'axis' },
          grid: { left: 40, right: 20, top: 40, bottom: 30 },
          xAxis: { type: 'category', data: categories, axisLabel: { fontSize: 11 } },
          yAxis: { type: 'value', axisLabel: { fontSize: 11 } },
          series: series.map((s, i) => ({
            name: s.name || '',
            type: 'line',
            smooth: true,
            data: s.data || [],
            itemStyle: { color: colors[i % colors.length] },
            areaStyle: { opacity: 0.15 },
          })),
        }
      }

      return {}
    },
    touchStart(e) { this.chart && this.chart.dispatchAction({ type: 'showTip' }) },
    touchMove() {},
    touchEnd() {},
  },
  beforeDestroy() {
    if (this.chart) {
      this.chart.dispose()
      this.chart = null
    }
  },
}
</script>

<style scoped>
.echarts-container {
  width: 100%;
  display: flex;
  justify-content: center;
}
</style>
