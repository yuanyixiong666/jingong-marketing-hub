/**
 * ChartCanvas 组件 - 微信小程序原生 Canvas 2D 绘图
 * 替代 EChartsCanvas，解决 ECharts 在微信小程序中的兼容性问题
 * 支持：柱状图(bar)、饼图(pie)、折线图(line)
 */
<template>
  <view class="chart-container" :style="{ width: canvasWidth + 'px', height: canvasHeight + 'px' }">
    <canvas
      :canvas-id="canvasId"
      :id="canvasId"
      :style="{ width: canvasWidth + 'px', height: canvasHeight + 'px' }"
    />
  </view>
</template>

<script>
export default {
  name: 'ChartCanvas',
  props: {
    canvasId: { type: String, default: 'chart-canvas' },
    width: { type: [Number, String], default: 340 },
    height: { type: [Number, String], default: 260 },
    chartType: { type: String, default: 'bar' },
    chartData: { type: Object, default: () => ({}) },
  },
  data() {
    return {
      canvasWidth: 0,
      canvasHeight: 0,
      ctx: null,
      dpr: 1,
    }
  },
  mounted() {
    this.canvasWidth = Number(this.width)
    this.canvasHeight = Number(this.height)
    const sysInfo = uni.getSystemInfoSync()
    this.dpr = sysInfo.pixelRatio || 1
    // 延迟确保 canvas 渲染完成
    setTimeout(() => {
      this.initCanvas()
    }, 200)
  },
  watch: {
    chartData: {
      deep: true,
      handler(newVal) {
        if (newVal && Object.keys(newVal).length > 0) {
          this.drawChart()
        }
      },
    },
  },
  methods: {
    initCanvas() {
      this.ctx = uni.createCanvasContext(this.canvasId, this)
      this.drawChart()
    },
    drawChart() {
      if (!this.ctx) return
      const { chartType } = this
      if (chartType === 'bar') this.drawBarChart()
      else if (chartType === 'pie') this.drawPieChart()
      else if (chartType === 'line') this.drawLineChart()
      this.ctx.draw()
    },

    // ============ 柱状图 ============
    drawBarChart() {
      const ctx = this.ctx
      const w = this.canvasWidth
      const h = this.canvasHeight
      const { chartData } = this
      const categories = chartData.categories || []
      const series = chartData.series || []
      const colors = chartData.colors || ['#3182ce', '#38a169', '#d69e2e', '#e53e3e', '#805ad5']

      // 清空画布
      ctx.clearRect(0, 0, w, h)
      ctx.setFillStyle('#ffffff')
      ctx.fillRect(0, 0, w, h)

      if (categories.length === 0) return

      const padding = { top: 20, right: 20, bottom: 40, left: 45 }
      const chartW = w - padding.left - padding.right
      const chartH = h - padding.top - padding.bottom

      // 计算最大值
      let maxVal = 0
      series.forEach(s => {
        s.data.forEach(v => { if (v > maxVal) maxVal = v })
      })
      if (maxVal === 0) maxVal = 1

      // 画 Y 轴网格线和标签
      ctx.setStrokeStyle('#e2e8f0')
      ctx.setLineWidth(0.5)
      ctx.setFontSize(10)
      ctx.setFillStyle('#718096')
      ctx.setTextAlign('right')
      ctx.setTextBaseline('middle')
      const ySteps = 4
      for (let i = 0; i <= ySteps; i++) {
        const y = padding.top + chartH - (chartH * i / ySteps)
        const val = Math.round(maxVal * i / ySteps)
        ctx.beginPath()
        ctx.moveTo(padding.left, y)
        ctx.lineTo(w - padding.right, y)
        ctx.stroke()
        ctx.fillText(val.toString(), padding.left - 5, y)
      }

      // 画柱状图
      const groupWidth = chartW / categories.length
      const barCount = series.length
      const barWidth = Math.min(groupWidth * 0.6 / barCount, 30)
      const barGap = 2

      categories.forEach((cat, ci) => {
        const groupX = padding.left + ci * groupWidth + groupWidth / 2

        series.forEach((s, si) => {
          const val = s.data[ci] || 0
          const barH = (val / maxVal) * chartH
          const barX = groupX - (barCount * barWidth + (barCount - 1) * barGap) / 2 + si * (barWidth + barGap)
          const barY = padding.top + chartH - barH

          // 画柱子（圆角）
          ctx.setFillStyle(colors[si % colors.length])
          this.roundRect(ctx, barX, barY, barWidth, barH, 3)
          ctx.fill()
        })

        // X 轴标签
        ctx.setFillStyle('#4a5568')
        ctx.setFontSize(10)
        ctx.setTextAlign('center')
        ctx.setTextBaseline('top')
        ctx.fillText(cat, groupX, padding.top + chartH + 8)
      })
    },

    // ============ 饼图 ============
    drawPieChart() {
      const ctx = this.ctx
      const w = this.canvasWidth
      const h = this.canvasHeight
      const { chartData } = this
      const pieData = chartData.pieData || []
      const colors = chartData.colors || ['#3182ce', '#38a169', '#d69e2e', '#e53e3e', '#805ad5']

      ctx.clearRect(0, 0, w, h)
      ctx.setFillStyle('#ffffff')
      ctx.fillRect(0, 0, w, h)

      if (pieData.length === 0) return

      const total = pieData.reduce((sum, item) => sum + item.value, 0)
      if (total === 0) return

      const cx = w / 2
      const cy = h / 2 - 15
      const outerR = Math.min(w, h) * 0.32
      const innerR = outerR * 0.55

      let startAngle = -Math.PI / 2

      pieData.forEach((item, i) => {
        const sliceAngle = (item.value / total) * 2 * Math.PI
        const endAngle = startAngle + sliceAngle

        // 画扇形
        ctx.beginPath()
        ctx.arc(cx, cy, outerR, startAngle, endAngle)
        ctx.arc(cx, cy, innerR, endAngle, startAngle, true)
        ctx.closePath()
        ctx.setFillStyle(colors[i % colors.length])
        ctx.fill()

        // 画标签线
        const midAngle = startAngle + sliceAngle / 2
        const labelR = outerR + 12
        const lx = cx + Math.cos(midAngle) * labelR
        const ly = cy + Math.sin(midAngle) * labelR
        const percent = Math.round((item.value / total) * 100)

        ctx.setFillStyle('#4a5568')
        ctx.setFontSize(10)
        ctx.setTextAlign(midAngle > Math.PI / 2 && midAngle < Math.PI * 1.5 ? 'right' : 'left')
        ctx.setTextBaseline('middle')
        ctx.fillText(item.name + ' ' + percent + '%', lx, ly)

        startAngle = endAngle
      })

      // 中心文字
      ctx.setFillStyle('#2d3748')
      ctx.setFontSize(14)
      ctx.setTextAlign('center')
      ctx.setTextBaseline('middle')
      ctx.fillText('共 ' + total + ' 条', cx, cy)
    },

    // ============ 折线图 ============
    drawLineChart() {
      const ctx = this.ctx
      const w = this.canvasWidth
      const h = this.canvasHeight
      const { chartData } = this
      const categories = chartData.categories || []
      const series = chartData.series || []
      const colors = chartData.colors || ['#3182ce', '#38a169', '#d69e2e', '#e53e3e', '#805ad5']

      ctx.clearRect(0, 0, w, h)
      ctx.setFillStyle('#ffffff')
      ctx.fillRect(0, 0, w, h)

      if (categories.length === 0) return

      const padding = { top: 20, right: 20, bottom: 40, left: 45 }
      const chartW = w - padding.left - padding.right
      const chartH = h - padding.top - padding.bottom

      // 计算最大值
      let maxVal = 0
      series.forEach(s => {
        s.data.forEach(v => { if (v > maxVal) maxVal = v })
      })
      if (maxVal === 0) maxVal = 1

      // Y 轴网格
      ctx.setStrokeStyle('#e2e8f0')
      ctx.setLineWidth(0.5)
      ctx.setFontSize(10)
      ctx.setFillStyle('#718096')
      ctx.setTextAlign('right')
      ctx.setTextBaseline('middle')
      const ySteps = 4
      for (let i = 0; i <= ySteps; i++) {
        const y = padding.top + chartH - (chartH * i / ySteps)
        const val = Math.round(maxVal * i / ySteps)
        ctx.beginPath()
        ctx.moveTo(padding.left, y)
        ctx.lineTo(w - padding.right, y)
        ctx.stroke()
        ctx.fillText(val.toString(), padding.left - 5, y)
      }

      // X 轴标签
      ctx.setFillStyle('#4a5568')
      ctx.setFontSize(10)
      ctx.setTextAlign('center')
      ctx.setTextBaseline('top')
      categories.forEach((cat, i) => {
        const x = padding.left + (chartW / (categories.length - 1 || 1)) * i
        ctx.fillText(cat, x, padding.top + chartH + 8)
      })

      // 画折线
      series.forEach((s, si) => {
        const color = colors[si % colors.length]
        const points = s.data.map((val, i) => ({
          x: padding.left + (chartW / (categories.length - 1 || 1)) * i,
          y: padding.top + chartH - (val / maxVal) * chartH,
        }))

        // 画面积
        ctx.beginPath()
        ctx.moveTo(points[0].x, padding.top + chartH)
        points.forEach(p => ctx.lineTo(p.x, p.y))
        ctx.lineTo(points[points.length - 1].x, padding.top + chartH)
        ctx.closePath()
        ctx.setFillStyle(color + '22')
        ctx.fill()

        // 画线
        ctx.beginPath()
        ctx.setStrokeStyle(color)
        ctx.setLineWidth(2)
        points.forEach((p, i) => {
          if (i === 0) ctx.moveTo(p.x, p.y)
          else ctx.lineTo(p.x, p.y)
        })
        ctx.stroke()

        // 画数据点
        points.forEach(p => {
          ctx.beginPath()
          ctx.arc(p.x, p.y, 3, 0, Math.PI * 2)
          ctx.setFillStyle(color)
          ctx.fill()
          ctx.setFillStyle('#ffffff')
          ctx.beginPath()
          ctx.arc(p.x, p.y, 1.5, 0, Math.PI * 2)
          ctx.fill()
        })
      })

      // 图例
      const legendY = h - 12
      let legendX = w / 2 - (series.length * 50) / 2
      series.forEach((s, si) => {
        const color = colors[si % colors.length]
        ctx.setFillStyle(color)
        ctx.fillRect(legendX, legendY - 4, 12, 8)
        ctx.setFillStyle('#4a5568')
        ctx.setFontSize(9)
        ctx.setTextAlign('left')
        ctx.setTextBaseline('middle')
        ctx.fillText(s.name || '', legendX + 15, legendY)
        legendX += 55
      })
    },

    // 圆角矩形辅助方法
    roundRect(ctx, x, y, w, h, r) {
      if (h < r * 2) r = h / 2
      if (w < r * 2) r = w / 2
      ctx.beginPath()
      ctx.moveTo(x + r, y)
      ctx.lineTo(x + w - r, y)
      ctx.arc(x + w - r, y + r, r, -Math.PI / 2, 0)
      ctx.lineTo(x + w, y + h - r)
      ctx.arc(x + w - r, y + h - r, r, 0, Math.PI / 2)
      ctx.lineTo(x + r, y + h)
      ctx.arc(x + r, y + h - r, r, Math.PI / 2, Math.PI)
      ctx.lineTo(x, y + r)
      ctx.arc(x + r, y + r, r, Math.PI, -Math.PI / 2)
      ctx.closePath()
    },
  },
}
</script>

<style scoped>
.chart-container {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
