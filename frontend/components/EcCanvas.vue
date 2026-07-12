/**
 * EcCanvas - echarts-for-weixin 适配 uni-app Vue3 版本
 * 使用 legacy canvas API (uni.createCanvasContext) + WxCanvas 包装器
 * 避免 type="2d" canvas node 查询在 uni-app 中的兼容性问题
 */
<template>
  <view class="ec-canvas-wrapper" :style="{ width: canvasWidth + 'px', height: canvasHeight + 'px' }">
    <canvas
      :canvas-id="canvasId"
      :id="canvasId"
      class="ec-canvas"
      :style="{ width: canvasWidth + 'px', height: canvasHeight + 'px' }"
      @touchstart="onTouchStart"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
    />
  </view>
</template>

<script>
import * as echarts from 'echarts/core'
import { BarChart, PieChart, LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([BarChart, PieChart, LineChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer])

// 禁用 progressive 渲染，微信小程序 canvas 不支持 drawImage 传入 DOM 对象
if (echarts.registerPreprocessor) {
  echarts.registerPreprocessor(function(option) {
    if (option && option.series) {
      var seriesArr = Array.isArray(option.series) ? option.series : [option.series]
      seriesArr.forEach(function(s) { s.progressive = 0 })
    }
  })
}

// WxCanvas 包装器：将微信小程序 canvas context 适配为 ECharts 可用接口
class WxCanvas {
  constructor(ctx, canvasId, width, height) {
    this.ctx = ctx
    this.canvasId = canvasId
    this.chart = null
    this._width = width || 300
    this._height = height || 150
    this._initStyle(ctx)
    this._initEvent()
  }

  getContext(contextType) {
    if (contextType === '2d') return this.ctx
  }

  setChart(chart) {
    this.chart = chart
  }

  attachEvent() {}
  detachEvent() {}

  // ZRender 会调用 addEventListener/removeEventListener，微信小程序 canvas 不支持这些方法
  addEventListener() {}
  removeEventListener() {}

  // ZRender 通过 canvas.width / canvas.height 获取尺寸
  get width() { return this._width }
  set width(w) { this._width = w }
  get height() { return this._height }
  set height(h) { this._height = h }

  _initStyle(ctx) {
    const styles = ['fillStyle', 'strokeStyle', 'globalAlpha', 'textAlign', 'textBaseline', 'shadowColor', 'lineWidth', 'lineCap', 'lineJoin', 'miterLimit', 'fontSize']
    styles.forEach(style => {
      Object.defineProperty(ctx, style, {
        set(value) {
          if (style !== 'fillStyle' && style !== 'strokeStyle' || (value !== 'none' && value !== null)) {
            const methodName = 'set' + style.charAt(0).toUpperCase() + style.slice(1)
            if (typeof ctx[methodName] === 'function') {
              ctx[methodName](value)
            }
          }
        },
        get() {
          return ctx['_' + style]
        }
      })
    })
    // 径向渐变 -> 圆形渐变
    if (typeof ctx.createRadialGradient === 'undefined' && typeof ctx.createCircularGradient === 'function') {
      ctx.createRadialGradient = function() {
        return ctx.createCircularGradient.apply(ctx, arguments)
      }
    }
  }

  _initEvent() {
    this.event = {}
    const eventNames = [
      { wxName: 'touchStart', ecName: 'mousedown' },
      { wxName: 'touchMove', ecName: 'mousemove' },
      { wxName: 'touchEnd', ecName: 'mouseup' },
      { wxName: 'touchEnd', ecName: 'click' },
    ]
    eventNames.forEach(name => {
      this.event[name.wxName] = (e) => {
        if (!this.chart || !e.touches || e.touches.length === 0) return
        const touch = e.touches[0]
        this.chart.getZr().handler.dispatch(name.ecName, {
          zrX: touch.x,
          zrY: touch.y,
        })
      }
    })
  }
}

export default {
  name: 'EcCanvas',
  props: {
    canvasId: { type: String, default: 'ec-canvas' },
    width: { type: [Number, String], default: 340 },
    height: { type: [Number, String], default: 260 },
    ec: { type: Object, default: () => ({}) },
  },
  data() {
    return {
      canvasWidth: 0,
      canvasHeight: 0,
    }
  },
  created() {
    this.chart = null
    this.wxCanvas = null
  },
  mounted() {
    this.canvasWidth = Number(this.width)
    this.canvasHeight = Number(this.height)
    setTimeout(() => {
      this.init()
    }, 200)
  },
  methods: {
    init() {
      if (!this.ec || typeof this.ec.onInit !== 'function') {
        console.warn('[EcCanvas] 请传入 ec.onInit 函数')
        return
      }
      const w = this.canvasWidth
      const h = this.canvasHeight
      // 使用 legacy canvas API
      const ctx = uni.createCanvasContext(this.canvasId, this)
      this.wxCanvas = new WxCanvas(ctx, this.canvasId, w, h)

      // 获取 canvas 尺寸（用于精确传递尺寸给 ECharts）
      const query = uni.createSelectorQuery().in(this)
      query.select('.ec-canvas').boundingClientRect((res) => {
        if (res) {
          this.wxCanvas._width = res.width
          this.wxCanvas._height = res.height
          this._doInit(this.wxCanvas, res.width, res.height, 1)
        } else {
          this._doInit(this.wxCanvas, w, h, 1)
        }
      }).exec()
    },
    _doInit(wxCanvas, width, height, dpr) {
      try {
        this.chart = this.ec.onInit(wxCanvas, width, height, dpr)
        wxCanvas.setChart(this.chart)
        console.log('[EcCanvas] 图表初始化成功, id:', this.canvasId)
      } catch (e) {
        console.error('[EcCanvas] 初始化失败:', e.message)
      }
    },
    onTouchStart(e) {
      if (this.wxCanvas && this.wxCanvas.event.touchStart) {
        this.wxCanvas.event.touchStart(e)
      }
    },
    onTouchMove(e) {
      if (this.wxCanvas && this.wxCanvas.event.touchMove) {
        this.wxCanvas.event.touchMove(e)
      }
    },
    onTouchEnd(e) {
      if (this.wxCanvas && this.wxCanvas.event.touchEnd) {
        this.wxCanvas.event.touchEnd(e)
      }
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
.ec-canvas-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
