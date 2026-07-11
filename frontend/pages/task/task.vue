<template>
  <view class="container">
    <view class="card" v-if="task.id">
      <text class="card-title">{{ task.task_name }}</text>
      <view class="detail-row">
        <text class="detail-label">任务类型</text>
        <text class="detail-value">{{ task.task_type }}</text>
      </view>
      <view class="detail-row">
        <text class="detail-label">调度周期</text>
        <text class="detail-value">{{ task.cron_expr || '手动触发' }}</text>
      </view>
      <view class="detail-row">
        <text class="detail-label">当前状态</text>
        <text class="status-badge" :class="task.status">{{ statusMap[task.status] || task.status }}</text>
      </view>
      <view class="detail-row">
        <text class="detail-label">上次执行</text>
        <text class="detail-value">{{ formatTime(task.last_run_at) }}</text>
      </view>
    </view>

    <view class="card" v-if="task.result_summary">
      <text class="card-title">执行结果</text>
      <text class="result-text">{{ task.result_summary }}</text>
    </view>

    <view class="card" v-if="task.error_message">
      <text class="card-title">错误信息</text>
      <text class="error-text">{{ task.error_message }}</text>
    </view>

    <view class="card">
      <button class="run-btn" @click="handleRun" v-if="task.status !== 'running'">手动执行</button>
      <button class="pause-btn" @click="handlePause" v-if="task.status === 'running'">暂停任务</button>
      <button class="stop-btn" @click="handleStop" v-if="task.status === 'running' || task.status === 'paused'">停止任务</button>
    </view>
  </view>
</template>

<script>
import { getTasks, runTask, pauseTask, stopTask } from "@/utils/api"

export default {
  data() {
    return {
      task: {},
      statusMap: { pending: "待执行", running: "运行中", paused: "已暂停", success: "成功", failed: "失败" },
    }
  },
  async onLoad(options) {
    const id = options.id
    if (!id) return
    try {
      const res = await getTasks()
      if (res.code === 200 && res.data) {
        this.task = res.data.find((t) => t.id === Number(id)) || {}
      }
    } catch (e) {
      console.log("加载失败", e)
    }
  },
  methods: {
    formatTime(t) {
      if (!t) return "未执行"
      return new Date(t).toLocaleString()
    },
    async handleRun() {
      uni.showLoading({ title: "执行中..." })
      try {
        await runTask(this.task.id)
        uni.showToast({ title: "已触发", icon: "success" })
        setTimeout(() => this.refresh(), 1000)
      } catch (e) {
        uni.showToast({ title: "执行失败", icon: "none" })
      }
    },
    async handlePause() {
      try {
        await pauseTask(this.task.id)
        uni.showToast({ title: "已暂停", icon: "success" })
        setTimeout(() => this.refresh(), 500)
      } catch (e) {
        uni.showToast({ title: "暂停失败", icon: "none" })
      }
    },
    async handleStop() {
      try {
        await stopTask(this.task.id)
        uni.showToast({ title: "已停止", icon: "success" })
        setTimeout(() => this.refresh(), 500)
      } catch (e) {
        uni.showToast({ title: "停止失败", icon: "none" })
      }
    },
    async refresh() {
      try {
        const res = await getTasks()
        if (res.code === 200 && res.data) {
          this.task = res.data.find((t) => t.id === this.task.id) || this.task
        }
      } catch (e) {}
    },
  },
}
</script>

<style scoped>
.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}
.detail-row:last-child { border-bottom: none; }
.detail-label { color: #999; font-size: 26rpx; }
.detail-value { color: #333; font-size: 26rpx; }
.status-badge {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
}
.status-badge.pending { background: #f0f0f0; color: #999; }
.status-badge.success { background: #c6f6d5; color: #38a169; }
.status-badge.running { background: #bee3f8; color: #3182ce; }
.status-badge.paused { background: #fefcbf; color: #b7791f; }
.status-badge.failed { background: #fed7d7; color: #e53e3e; }
.result-text { display: block; font-size: 26rpx; color: #333; line-height: 1.6; }
.error-text { display: block; font-size: 26rpx; color: #e53e3e; line-height: 1.6; }
.run-btn {
  background: #2c5282;
  color: #fff;
  font-size: 28rpx;
  border-radius: 12rpx;
  height: 80rpx;
  line-height: 80rpx;
}
.pause-btn {
  background: #d69e2e;
  color: #fff;
  font-size: 28rpx;
  border-radius: 12rpx;
  height: 80rpx;
  line-height: 80rpx;
}
.stop-btn {
  background: #e53e3e;
  color: #fff;
  font-size: 28rpx;
  border-radius: 12rpx;
  height: 80rpx;
  line-height: 80rpx;
  margin-top: 16rpx;
}
</style>
