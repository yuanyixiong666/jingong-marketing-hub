/**
 * ECharts 图表组件 - 微信小程序适配版 v4
 * 修复：切回 echarts/core + CanvasRenderer（完整包依赖 DOM API）
 * 使用 getCurrentInstance() 获取 Vue3 组件代理，解决 .in(this) 作用域问题
 */
<template>
  <view class="echarts-container" :style="{ width: canvasWidth + 'px', height: canvasHeight + 'px' }">
    <canvas
      :id="canvasId"
      :canvas-id="canvasId"
      type="2d"
      :style="{ width: canvasWidth + 'px', height: canvasHeight + 'px' }"
    />
  </view>
</template>

<script>
import { getCurrentInstance } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart, PieChart, LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([BarChart, PieChart, LineChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer])

export default {
  name: 'EChartsCanvas',
  props: {
    canvasId: { type: String, default: 'echarts-canvas' },
    width: { type: [Number, String], default: 340 },
    height: { type: [Number, String], default: 260 },
    chartType: { type: String, default: 'bar' },
    chartData: { type: Object, default: () => ({}) },
  },
  data() {
    return {
      chart: null,
      canvasWidth: 0,
      canvasHeight: 0,
      inited: false,
      retryCount: 0,
    }
  },
  mounted() {
    this.canvasWidth = Number(this.width)
    this.canvasHeight = Number(this.height)
    this.retryCount = 0
    this._tryInit()
  },
  watch: {
    chartData: {
      deep: true,
      handler(newVal) {
        if (this.inited && newVal && Object.keys(newVal).length > 0) {
          this.updateChart()
        }
      },
    },
  },
  methods: {
    _tryInit() {
      if (this.retryCount > 8) {
        console.error('[EChartsCanvas] 超过最大重试次数, canvasId:', this.canvasId)
        return
      }
      const delay = 100 + this.retryCount * 150
      setTimeout(() => {
        this._queryCanvas()
      }, delay)
    },
    _queryCanvas() {
      const canvasId = this.canvasId
      const w = this.canvasWidth
      const h = this.canvasHeight
      const dpr = uni.getSystemInfoSync().pixelRatio || 2

      // 关键修复：在 Vue3 Options API 中用 getCurrentInstance() 获取组件代理
      // .in(this) 中的 this 是 Vue 实例，不是小程序组件实例
      const vm = getCurrentInstance()
      const query = uni.createSelectorQuery().in(vm ? vm.proxy : this)

      query.select('#' + canvasId).fields({ node: true, size: true }).exec((res) => {
        if (!res || !res[0] || !res[0].node) {
          console.log('[EChartsCanvas] canvas 未就绪, 重试中... canvasId:', canvasId, 'retry:', this.retryCount)
          this.retryCount++
          this._tryInit()
          return
        }
        const canvas = res[0].node
        canvas.width = w * dpr
        canvas.height = h * dpr
        try {
          this.chart = echarts.init(canvas, null, {
            width: w,
            height: h,
            devicePixelRatio: dpr,
          })
          this.inited = true
          console.log('[EChartsCanvas] 图表初始化成功, type:', this.chartType, 'id:', canvasId)
          this.updateChart()
        } catch (e) {
          console.error('[EChartsCanvas] echarts.init 失败:', e.message)
          this.retryCount++
          this._tryInit()
        }
      })
    },
    updateChart() {
      if (!this.chart) return
      this.chart.setOption(this.getChartOption(), true)
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
  },
  beforeUnmount() {
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
  align-items: center;
}
</style>
