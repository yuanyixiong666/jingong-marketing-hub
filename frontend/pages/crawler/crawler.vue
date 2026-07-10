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
            <text class="task-name">{{ task.name }}</text>
            <text class="task-time">上次: {{ task.lastRun || "未执行" }}</text>
          </view>
          <view class="task-actions">
            <text class="task-badge" :class="task.status">{{ task.statusText }}</text>
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
          <text class="brand-name">{{ c.brand_name }}</text>
          <text class="brand-keywords">{{ c.keywords }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
/**
 * 数据采集页面 - 任务管理和竞品监控
 * AI生成：任务列表展示和手动触发
 */
import { getTasks, runTask, getCompetitors } from "@/utils/api"

export default {
  data() {
    return {
      tasks: [],
      competitors: [],
    }
  },
  onShow() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const [tasksRes, compRes] = await Promise.all([getTasks(), getCompetitors()])
        if (tasksRes.code === 200) {
          this.tasks = tasksRes.data.map((t) => ({
            ...t,
            statusText: { pending: "待执行", running: "运行中", success: "成功", failed: "失败" }[t.status] || t.status,
            lastRun: t.last_run_at ? new Date(t.last_run_at).toLocaleString() : "未执行",
          }))
        }
        if (compRes.code === 200) this.competitors = compRes.data
      } catch (e) {
        console.log("加载失败", e)
      }
    },
    async handleRun(taskId) {
      uni.showLoading({ title: "执行中..." })
      try {
        await runTask(taskId)
        uni.showToast({ title: "已触发", icon: "success" })
        this.loadData()
      } catch (e) {
        uni.showToast({ title: "执行失败", icon: "none" })
      }
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
.task-info { flex: 1; }
.task-name { display: block; font-size: 30rpx; color: #333; font-weight: 500; }
.task-time { display: block; font-size: 24rpx; color: #999; margin-top: 6rpx; }
.task-actions { display: flex; align-items: center; gap: 12rpx; }
.task-badge {
  font-size: 22rpx;
  padding: 4rpx 12rpx;
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
}
.competitor-list { display: flex; flex-direction: column; }
.competitor-row { padding: 16rpx 0; border-bottom: 1rpx solid #f0f0f0; }
.brand-name { display: block; font-weight: 600; color: #1e3a5f; }
.brand-keywords { display: block; font-size: 24rpx; color: #666; margin-top: 6rpx; }
</style>
