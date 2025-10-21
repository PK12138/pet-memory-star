// pages/test-api/test-api.js
const app = getApp()

Page({
  data: {
    baseUrl: '',
    healthResult: '',
    loginResult: ''
  },

  onLoad() {
    this.setData({
      baseUrl: app.globalData.baseUrl
    })
    console.log('测试页面加载，baseUrl:', app.globalData.baseUrl)
  },

  // 测试健康检查
  async testHealth() {
    console.log('开始测试健康检查...')
    this.setData({ healthResult: '请求中...' })
    
    try {
      const res = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.baseUrl}/api/health`,
          method: 'GET',
          timeout: 10000,
          success: (res) => {
            console.log('健康检查成功:', res)
            resolve(res)
          },
          fail: (err) => {
            console.error('健康检查失败:', err)
            reject(err)
          }
        })
      })
      
      this.setData({
        healthResult: `✅ 成功: ${JSON.stringify(res.data)}`
      })
    } catch (error) {
      this.setData({
        healthResult: `❌ 失败: ${error.errMsg || JSON.stringify(error)}`
      })
    }
  },

  // 测试登录接口
  async testLogin() {
    console.log('开始测试登录接口...')
    this.setData({ loginResult: '请求中...' })
    
    try {
      const res = await new Promise((resolve, reject) => {
        wx.request({
          url: `${app.globalData.baseUrl}/api/auth/login`,
          method: 'POST',
          timeout: 10000,
          header: {
            'Content-Type': 'application/json'
          },
          data: {
            email: '1208155205@qq.com',
            password: 'test123456'
          },
          success: (res) => {
            console.log('登录测试成功:', res)
            resolve(res)
          },
          fail: (err) => {
            console.error('登录测试失败:', err)
            reject(err)
          }
        })
      })
      
      this.setData({
        loginResult: `✅ 成功: ${JSON.stringify(res.data)}`
      })
    } catch (error) {
      this.setData({
        loginResult: `❌ 失败: ${error.errMsg || JSON.stringify(error)}`
      })
    }
  },

  clearCache() {
    wx.clearStorage({
      success: () => {
        wx.showToast({
          title: '缓存已清除',
          icon: 'success'
        })
      }
    })
  }
})

