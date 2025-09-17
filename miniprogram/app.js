// app.js
const config = require('./config/config')

App({
  globalData: {
    userInfo: null,
    sessionToken: null,
    baseUrl: config.baseUrl,
    appId: config.appId,
    appSecret: config.appSecret,
    userLevel: 0,
    permissions: {}
  },

  onLaunch() {
    console.log('爪迹星小程序启动')
    
    // 检查登录状态
    this.checkLoginStatus()
    
    // 获取系统信息
    this.getSystemInfo()
  },

  onShow() {
    console.log('爪迹星小程序显示')
  },

  onHide() {
    console.log('爪迹星小程序隐藏')
  },

  onError(error) {
    console.error('小程序错误:', error)
  },

  // 检查登录状态
  checkLoginStatus() {
    const sessionToken = wx.getStorageSync('session_token')
    if (sessionToken) {
      this.globalData.sessionToken = sessionToken
      this.getUserInfo()
    }
  },

  // 获取用户信息
  getUserInfo() {
    if (!this.globalData.sessionToken) return

    wx.request({
      url: `${this.globalData.baseUrl}/api/user/info`,
      method: 'GET',
      header: {
        'X-Session-Token': this.globalData.sessionToken
      },
      success: (res) => {
        if (res.data.success) {
          this.globalData.userInfo = res.data.user
          this.globalData.userLevel = res.data.user.user_level || 0
          this.globalData.permissions = res.data.permissions || {}
        }
      },
      fail: (error) => {
        console.error('获取用户信息失败:', error)
        this.logout()
      }
    })
  },

  // 登录
  login(sessionToken, userInfo) {
    this.globalData.sessionToken = sessionToken
    this.globalData.userInfo = userInfo
    wx.setStorageSync('session_token', sessionToken)
    this.getUserInfo()
  },

  // 登出
  logout() {
    this.globalData.sessionToken = null
    this.globalData.userInfo = null
    this.globalData.userLevel = 0
    this.globalData.permissions = {}
    wx.removeStorageSync('session_token')
  },

  // 获取系统信息
  getSystemInfo() {
    wx.getSystemInfo({
      success: (res) => {
        this.globalData.systemInfo = res
        console.log('系统信息:', res)
      }
    })
  },

  // 显示加载提示
  showLoading(title = '加载中...') {
    wx.showLoading({
      title: title,
      mask: true
    })
  },

  // 隐藏加载提示
  hideLoading() {
    wx.hideLoading()
  },

  // 显示成功提示
  showSuccess(title) {
    wx.showToast({
      title: title,
      icon: 'success',
      duration: 2000
    })
  },

  // 显示错误提示
  showError(title) {
    wx.showToast({
      title: title,
      icon: 'none',
      duration: 2000
    })
  },

  // 显示确认对话框
  showConfirm(title, content) {
    return new Promise((resolve) => {
      wx.showModal({
        title: title,
        content: content,
        success: (res) => {
          resolve(res.confirm)
        }
      })
    })
  },

  // 网络请求封装
  request(options) {
    const { url, method = 'GET', data = {}, header = {} } = options
    
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.globalData.baseUrl}${url}`,
        method: method,
        data: data,
        header: {
          'Content-Type': 'application/json',
          'X-Session-Token': this.globalData.sessionToken,
          ...header
        },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else {
            reject(new Error(`请求失败: ${res.statusCode}`))
          }
        },
        fail: (error) => {
          reject(error)
        }
      })
    })
  },

  // 上传文件
  uploadFile(filePath, name = 'file', formData = {}) {
    return new Promise((resolve, reject) => {
      wx.uploadFile({
        url: `${this.globalData.baseUrl}/api/upload`,
        filePath: filePath,
        name: name,
        formData: {
          ...formData,
          session_token: this.globalData.sessionToken
        },
        success: (res) => {
          try {
            const data = JSON.parse(res.data)
            resolve(data)
          } catch (error) {
            reject(error)
          }
        },
        fail: reject
      })
    })
  }
})
