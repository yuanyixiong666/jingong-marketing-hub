/**
 * 统一请求封装
 * AI生成：封装uni.request，统一处理错误和loading
 * 人工修改：API地址集中配置，增加请求计数器避免loading闪烁，增加超时
 */
const BASE_URL = "http://localhost:8001"  // 后端API地址，部署时修改此处即可

let requestCount = 0

const request = (options) => {
  return new Promise((resolve, reject) => {
    const silent = options.silent === true
    if (!silent) {
      if (requestCount === 0) {
        uni.showLoading({ title: "加载中..." })
      }
      requestCount++
    }
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || "GET",
      data: options.data || {},
      timeout: 30000,
      header: {
        "Content-Type": "application/json",
        ...options.header,
      },
      success: (res) => {
        if (!silent) {
          requestCount--
          if (requestCount <= 0) { requestCount = 0 }
        }
        if (res.statusCode === 200) {
          if (!silent && requestCount === 0) uni.hideLoading()
          resolve(res.data)
        } else {
          if (!silent && requestCount === 0) uni.hideLoading()
          uni.showToast({ title: "请求失败", icon: "none" })
          reject(res)
        }
      },
      fail: (err) => {
        if (!silent) {
          requestCount--
          if (requestCount <= 0) { requestCount = 0 }
        }
        if (!silent && requestCount === 0) uni.hideLoading()
        uni.showToast({ title: "网络异常", icon: "none" })
        reject(err)
      },
    })
  })
}

export const get = (url, data, silent) => request({ url, method: "GET", data, silent })
export const post = (url, data, silent) => request({ url, method: "POST", data, silent })

export default request
