<template>
  <view class="container">
    <view class="card">
      <text class="card-title">数据采集中心</text>
    </view>

    <!-- 爬虫任务列表 -->
    <view class="card">
      <text class="card-title">采集任务</text>
      <view class="task-list">
        <view class="task-row" v-for="task in tasks" :key="task.id">
          <view class="task-info">
            <text class="task-name">{{ task.task_name }}</text>
            <text class="task-meta">{{ task.task_type }} | {{ task.cron_expr }}</text>
            <text class="task-time">上次: {{ formatTime(task.last_run_at) }}</text>
          </view>
          <view class="task-actions">
            <text class="task-badge" :class="task.status">{{ statusMap[task.status] || task.status }}</text>
            <button class="run-btn" size="mini" @click="handleRun(task.id)">执行</button>
          </view>
        </view>
      </view>
    </view>

    <!-- 竞品监控 -->
    <view class="card">
      <text class="card-title">竞品监控</text>
      <view class="competitor-list">
        <view class="competitor-row" v-for="c in competitors" :key="c.id">
          <view class="comp-info">
            <text class="brand-name">{{ c.brand_name }}</text>
            <text class="brand-desc">{{ c.description || "" }}</text>
          </view>
          <view class="comp-keywords">
            <text class="keyword-tag" v-for="kw in (c.keywords || '').split(',')" :key="kw">{{ kw }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 数据质量 -->
    <view class="card">
      <text class="card-title">数据质量概览</text>
      <view class="quality-grid">
        <view class="quality-item">
          <text class="quality-value">{{ totalData }}</text>
          <text class="quality-label">总数据量</text>
        </view>
        <view class="quality-item">
          <text class="quality-value">{{ platforms.length }}</text>
          <text class="quality-label">接入平台</text>
        </view>
        <view class="quality-item">
          <text class="quality-value">{{ tasks.length }}</text>
          <text class="quality-label">采集任务</text>
        </view>
        <view class="quality-item">
          <text class="quality-value">{{ competitors.length }}</text>
          <text class="quality-label">监控竞品</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
/**
 * 数据采集页面 - 任务管理和竞品监控
 * AI生成：任务列表展示和手动触发
 * 人工修改：完善数据展示和交互逻辑
 */
import { getTasks, runTask, getCompetitors, getPlatformStats } from "@/utils/api"

export default {
  data() {
    return {
      tasks: [],
      competitors: [],
      platforms: [],
      totalData: 0,
      statusMap: { pending: "待执行", running: "运行中", success: "成功", failed: "失败" },
    }
  },
  onShow() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const [tasksRes, compRes, statsRes] = await Promise.all([
          getTasks(),
          getCompetitors(),
          getPlatformStats(),
        ])
        if (tasksRes.code === 200) this.tasks = tasksRes.data || []
        if (compRes.code === 200) this.competitors = compRes.data || []
        if (statsRes.code === 200) {
          this.platforms = statsRes.data || []
          this.totalData = this.platforms.reduce((s, p) => s + p.total, 0)
        }
      } catch (e) {
        console.log("加载失败", e)
      }
    },
    async handleRun(taskId) {
      uni.showLoading({ title: "执行中..." })
      try {
        await runTask(taskId)
        uni.showToast({ title: "已触发", icon: "success" })
        setTimeout(() => this.loadData(), 1000)
      } catch (e) {
        uni.showToast({ title: "执行失败", icon: "none" })
      }
    },
    formatTime(t) {
      if (!t) return "未执行"
      return new Date(t).toLocaleString()
    },
  },
}
</script>

<style scoped>
.task-list { display: flex; flex-direction: column; }
.task-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}
.task-row:last-child { border-bottom: none; }
.task-info { flex: 1; }
.task-name { display: block; font-size: 30rpx; color: #333; font-weight: 500; }
.task-meta { display: block; font-size: 22rpx; color: #999; margin-top: 4rpx; }
.task-time { display: block; font-size: 24rpx; color: #999; margin-top: 6rpx; }
.task-actions { display: flex; align-items: center; gap: 12rpx; }
.task-badge {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
}
.task-badge.pending { background: #f0f0f0; color: #999; }
.task-badge.success { background: #c6f6d5; color: #38a169; }
.task-badge.running { background: #bee3f8; color: #3182ce; }
.task-badge.failed { background: #fed7d7; color: #e53e3e; }
.run-btn {
  background: #2c5282;
  color: #fff;
  font-size: 24rpx;
  border-radius: 8rpx;
  padding: 0 20rpx;
}
.competitor-list { display: flex; flex-direction: column; }
.competitor-row {
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}
.competitor-row:last-child { border-bottom: none; }
.comp-info { margin-bottom: 12rpx; }
.brand-name { display: block; font-weight: 600; color: #1e3a5f; font-size: 30rpx; }
.brand-desc { display: block; font-size: 24rpx; color: #666; margin-top: 4rpx; }
.comp-keywords { display: flex; flex-wrap: wrap; gap: 8rpx; }
.keyword-tag {
  font-size: 22rpx;
  padding: 4rpx 12rpx;
  background: #e8f0fe;
  color: #2c5282;
  border-radius: 6rpx;
}
.quality-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}
.quality-item {
  flex: 1;
  min-width: 45%;
  text-align: center;
  padding: 20rpx;
  background: #f8fafc;
  border-radius: 12rpx;
}
.quality-value { display: block; font-size: 40rpx; font-weight: 700; color: #2c5282; }
.quality-label { display: block; font-size: 24rpx; color: #999; margin-top: 8rpx; }
</style>
