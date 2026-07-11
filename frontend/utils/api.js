/**
 * API接口定义
 * AI生成：集中管理所有后端接口调用
 * 人工修改：添加归因分析接口
 */
import { get, post } from "./request"

// 平台数据
export const getPlatformData = (params) => get("/api/platform-data", params)
export const getPlatformStats = () => get("/api/platform-data/stats")

// 竞品监控
export const getCompetitors = () => get("/api/competitors")
export const getCompetitorPrices = (id) => get(`/api/competitors/${id}/prices`)

// 任务调度
export const getTasks = () => get("/api/tasks")
export const runTask = (id) => post(`/api/tasks/${id}/run`)
export const pauseTask = (id) => post(`/api/tasks/${id}/pause`)
export const stopTask = (id) => post(`/api/tasks/${id}/stop`)

// 舆情数据
export const getSentimentList = (params) => get("/api/sentiment", params)
export const getSentimentStats = () => get("/api/sentiment/stats")

// 智能报告
export const generateReport = (data) => post("/api/report/generate", data)

// AI情感分析
export const analyzeSentiment = (data) => post("/api/report/analyze-sentiment", data)

// 归因分析
export const getAttributionScores = (days) => get("/api/attribution/scores", { days })
