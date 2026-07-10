/**
 * 统一请求封装
 * AI生成：封装uni.request，统一处理错误和loading
 */
const BASE_URL = "http://localhost:8000"

const request = (options) => {
  return new Promise((resolve, reject) => {
    uni.showLoading({ title: "加载中..." })
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || "GET",
      data: options.data || {},
      header: {
        "Content-Type": "application/json",
        ...options.header,
      },
      success: (res) => {
        uni.hideLoading()
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          uni.showToast({ title: "请求失败", icon: "none" })
          reject(res)
        }
      },
      fail: (err) => {
        uni.hideLoading()
        uni.showToast({ title: "网络异常", icon: "none" })
        reject(err)
      },
    })
  })
}

export const get = (url, data) => request({ url, method: "GET", data })
export const post = (url, data) => request({ url, method: "POST", data })

export default request
