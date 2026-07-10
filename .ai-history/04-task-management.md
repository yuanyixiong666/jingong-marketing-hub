# AI 协作日志 04：采集任务暂停/停止功能

- **日期**：2026-07-11
- **AI 工具**：QoderWork（Qoder AI 编程助手）
- **提交记录**：`2dbd5f5` feat: 采集任务增加暂停/停止功能，完善任务状态管理

## 任务目标

为采集任务管理增加暂停和停止功能，使用户可以在任务运行过程中进行控制，完善任务状态机。

## 需求背景

初始版本中，采集任务只能"执行"（从 pending → running），但没有暂停和停止机制。用户在微信开发者工具中预览时发现缺少这些控制按钮，决定补充。

## AI 完成的工作

### 后端接口

在 `routers/crawl_task.py` 新增两个端点：

**暂停接口** `POST /api/tasks/{task_id}/pause`：
- 校验任务存在性
- 校验当前状态必须为 `running`
- 将状态更新为 `paused`
- 返回"任务已暂停"

**停止接口** `POST /api/tasks/{task_id}/stop`：
- 校验任务存在性
- 将状态重置为 `pending`（无论当前是 running 还是 paused）
- 返回"任务已停止"

**执行接口** `POST /api/tasks/{task_id}/run` 增加状态校验：
- 如果任务已经是 `running` 状态，返回 400 错误"任务正在运行中"

### 前端交互

在 `pages/crawler/crawler.vue` 实现动态按钮渲染：

```
任务状态 → 显示按钮
running  → [暂停(黄色)] [停止(红色)]
paused   → [继续(蓝色)] [停止(红色)]
pending/failed/success → [执行(蓝色)]
```

- 新增 `handlePause()` 方法：调用 `pauseTask` API，成功后延迟刷新列表
- 新增 `handleStop()` 方法：调用 `stopTask` API，成功后延迟刷新列表
- 新增 `paused` 状态映射：黄色标签
- 新增按钮样式：`.pause-btn`（黄色）、`.stop-btn`（红色）

### API 定义

在 `utils/api.js` 新增：
```javascript
export const pauseTask = (id) => post(`/api/tasks/${id}/pause`)
export const stopTask = (id) => post(`/api/tasks/${id}/stop`)
```

## 任务状态机

完整的状态流转：

```
pending ──执行──→ running
running ──暂停──→ paused
running ──停止──→ pending
paused  ──继续──→ running（复用 run 接口）
paused  ──停止──→ pending
```

## 人工审查与修改

本阶段代码由 AI 一次性生成，人工审查后直接通过，未做额外修改。

## 关键决策

1. **停止 = 重置为 pending**：而非引入新的 `stopped` 状态，保持状态机简洁
2. **继续 = 复用 run 接口**：paused 状态的任务调用 run 接口即可恢复，不需要单独的 continue 端点
3. **前端条件渲染**：用 `v-if` 根据任务状态动态显示按钮，而非禁用不可用的按钮

## 经验总结

这是一个典型的"小功能快速迭代"场景。从需求提出到代码完成（后端 + 前端 + API 定义）约 5 分钟。AI 在处理这种模式化的 CRUD + 状态管理任务时效率非常高，人工只需要确认状态机设计是否合理即可。
