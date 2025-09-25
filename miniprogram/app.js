// app.js
const config = require('./config/config')
const apiService = require('./utils/api')

App({
  globalData: {
    userInfo: null,
    sessionToken: null,
    baseUrl: config.baseUrl,
    appId: config.appId,
    appSecret: config.appSecret,
    userLevel: 0,
    permissions: {},
    systemInfo: null
  },

  onLaunch() {
    console.log('爪迹星小程序启动')
    
    // 检查登录状态
    this.checkLoginStatus()
    
    // 获取系统信息
    this.getSystemInfo()
    
    // 检查网络状态
    this.checkNetworkStatus()
  },

  onShow() {
    console.log('爪迹星小程序显示')
  },

  onHide() {
    console.log('爪迹星小程序隐藏')
  },

  onError(error) {
    console.error('小程序错误:', error)
    this.showError('程序出现错误，请重启应用')
  },

  // 检查登录状态
  checkLoginStatus() {
    const sessionToken = wx.getStorageSync('sessionToken')
    if (sessionToken) {
      this.globalData.sessionToken = sessionToken
      this.getUserInfo()
    }
  },

  // 获取用户信息
  async getUserInfo() {
    if (!this.globalData.sessionToken) return

    try {
      const res = await apiService.getUserInfo()
      if (res.success) {
        this.globalData.userInfo = res.user
        this.globalData.userLevel = res.user.user_level || 0
        this.globalData.permissions = res.permissions || {}
        wx.setStorageSync('userInfo', res.user)
      } else {
        this.logout()
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      this.logout()
    }
  },

  // 登录
  login(sessionToken, userInfo) {
    this.globalData.sessionToken = sessionToken
    this.globalData.userInfo = userInfo
    wx.setStorageSync('sessionToken', sessionToken)
    wx.setStorageSync('userInfo', userInfo)
    this.getUserInfo()
  },

  // 登出
  logout() {
    this.globalData.sessionToken = null
    this.globalData.userInfo = null
    this.globalData.userLevel = 0
    this.globalData.permissions = {}
    wx.removeStorageSync('sessionToken')
    wx.removeStorageSync('userInfo')
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

  // 检查网络状态
  checkNetworkStatus() {
    wx.getNetworkType({
      success: (res) => {
        console.log('网络类型:', res.networkType)
        if (res.networkType === 'none') {
          this.showError('网络连接失败，请检查网络设置')
        }
      },
      fail: (error) => {
        console.error('获取网络状态失败:', error)
      }
    })

    wx.onNetworkStatusChange((res) => {
      console.log('网络状态变化:', res)
      if (!res.isConnected) {
        this.showError('网络连接已断开')
      } else {
        this.showSuccess('网络已连接')
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
  async request(options) {
    const { url, method = 'GET', data = {}, header = {} } = options
    
    try {
      const res = await apiService.request(options)
      return res
    } catch (error) {
      console.error('API请求失败:', error)
      
      // 处理不同类型的错误
      const errorMessage = error.message || error.errMsg || '未知错误'
      
      if (errorMessage.includes('登录已过期')) {
        this.logout()
        wx.showModal({
          title: '登录已过期',
          content: '您的登录已过期，请重新登录',
          showCancel: false,
          success: () => {
            wx.reLaunch({
              url: '/pages/login/login'
            })
          }
        })
      } else if (errorMessage.includes('网络') || errorMessage.includes('timeout')) {
        this.showError('网络连接失败，请检查网络设置')
      } else if (errorMessage.includes('服务器')) {
        this.showError('服务器错误，请稍后重试')
      } else {
        this.showError('操作失败，请稍后重试')
      }
      
      throw error
    }
  },

  // 上传文件
  async uploadFile(filePath, name = 'file', formData = {}) {
    try {
      const res = await apiService.uploadFile(filePath, name, formData)
      return res
    } catch (error) {
      console.error('文件上传失败:', error)
      this.showError('文件上传失败，请重试')
      throw error
    }
  },

  // 检查权限
  async checkPermission(permission) {
    try {
      const res = await apiService.checkPermission(permission)
      return res.success && res.has_permission
    } catch (error) {
      console.error('权限检查失败:', error)
      return false
    }
  },

  // 获取用户等级信息
  async getUserLevelInfo() {
    try {
      const res = await apiService.getUserLevel()
      if (res.success) {
        this.globalData.userLevel = res.level_info.level
        this.globalData.permissions = res.permissions || {}
        return res.level_info
      }
    } catch (error) {
      console.error('获取用户等级失败:', error)
    }
    return null
  },

  // 格式化日期
  formatDate(date, format = 'YYYY-MM-DD') {
    const d = new Date(date)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    const hour = String(d.getHours()).padStart(2, '0')
    const minute = String(d.getMinutes()).padStart(2, '0')
    const second = String(d.getSeconds()).padStart(2, '0')

    return format
      .replace('YYYY', year)
      .replace('MM', month)
      .replace('DD', day)
      .replace('HH', hour)
      .replace('mm', minute)
      .replace('ss', second)
  },

  // 格式化文件大小
  formatFileSize(bytes) {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  },

  // 防抖函数
  debounce(func, wait) {
    let timeout
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout)
        func(...args)
      }
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
    }
  },

  // 节流函数
  throttle(func, limit) {
    let inThrottle
    return function executedFunction(...args) {
      if (!inThrottle) {
        func.apply(this, args)
        inThrottle = true
        setTimeout(() => inThrottle = false, limit)
      }
    }
  }
})