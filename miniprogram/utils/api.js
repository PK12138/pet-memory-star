// utils/api.js
// API请求工具类
// 配置版本：v2.0 - 更新时间：2024-10-20 23:30

// 远程服务器配置
const config = {
  baseUrl: 'https://www.pettrailstar.cn'  // ✅ 远程生产服务器
  // baseUrl: 'https://42.193.230.145'  // HTTPS 443端口（需要配置SSL证书）
  // baseUrl: 'https://pettrailstar.cn'  // 域名HTTPS（备案后使用）
}

// 输出配置用于调试
console.log('🌐 API Service 配置 [v2.0]:', config.baseUrl)

class ApiService {
  constructor() {
    this.baseUrl = config.baseUrl
  }

  // 获取app实例
  getApp() {
    return getApp()
  }

  // 通用请求方法
  async request(options, retryCount = 0) {
    // 为不同的API设置不同的超时时间
    let defaultTimeout = 15000 // 默认15秒
    if (options.url === '/api/memorial/create') {
      defaultTimeout = 30000 // 创建纪念馆30秒
    }

    const { 
      url, 
      method = 'GET', 
      data = {}, 
      header = {}, 
      timeout = defaultTimeout, 
      maxRetries = 3  // 增加到3次重试
    } = options
    const app = this.getApp()
    
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.baseUrl}${url}`,
        method: method,
        data: data,
        timeout: timeout,
        header: {
          'Content-Type': 'application/json',
          'x-session-token': app.globalData.sessionToken || '',
          ...header
        },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else if (res.statusCode === 401) {
            // 未授权，返回401错误
            reject({
              statusCode: 401,
              message: '登录已过期'
            })
          } else {
            // 其他错误，返回错误信息但不影响登录状态
            reject({
              statusCode: res.statusCode,
              message: `请求失败: ${res.statusCode}`
            })
          }
        },
        fail: (error) => {
          console.error('API请求失败:', error)
          
          // 如果是网络错误且还有重试次数，则重试
          if (retryCount < maxRetries && (error.errMsg.includes('timeout') || error.errMsg.includes('fail'))) {
            const delay = Math.min(1000 * Math.pow(2, retryCount), 10000) // 指数退避，最大10秒
            console.log(`请求失败，${delay/1000}秒后重试 (${retryCount + 1}/${maxRetries})`)
            
            // 如果是创建纪念馆，显示加载提示
            if (options.url === '/api/memorial/create') {
              wx.showLoading({
                title: '正在重试...',
                mask: true
              })
            }
            
            setTimeout(() => {
              if (options.url === '/api/memorial/create') {
                wx.hideLoading()
              }
              this.request(options, retryCount + 1).then(resolve).catch(reject)
            }, delay)
          } else {
            if (options.url === '/api/memorial/create') {
              wx.hideLoading()
            }
            reject(error)
          }
        }
      })
    })
  }

  // 用户相关API
  async login(email, password) {
    return this.request({
      url: '/api/auth/login',
      method: 'POST',
      data: { email, password }
    })
  }

  async register(email, password, confirmPassword) {
    return this.request({
      url: '/api/auth/register',
      method: 'POST',
      data: { email, password, confirm_password: confirmPassword }
    })
  }

  async logout() {
    return this.request({
      url: '/api/auth/logout',
      method: 'POST'
    })
  }

  async forgotPassword(email) {
    return this.request({
      url: '/api/auth/forgot-password',
      method: 'POST',
      data: { email }
    })
  }

  async resetPassword(token, newPassword) {
    return this.request({
      url: '/api/auth/reset-password',
      method: 'POST',
      data: { token, new_password: newPassword }
    })
  }

  async getUserInfo() {
    return this.request({
      url: '/api/user/info'
    })
  }

  async getUserLevel() {
    return this.request({
      url: '/api/user/level-info'
    })
  }

  async getUserDashboard() {
    return this.request({
      url: '/api/user/dashboard'
    })
  }

  async updateUserInfo(data) {
    return this.request({
      url: '/api/user/update',
      method: 'PUT',
      data: data
    })
  }

  // 纪念馆相关API
  async getMemorials() {
    return this.request({
      url: '/api/user/memorials'
    })
  }

  async getMemorialDetail(memorialId) {
    return this.request({
      url: `/api/memorial/get/${memorialId}`
    })
  }

  async createMemorial(data) {
    wx.showLoading({
      title: '正在创建...',
      mask: true
    })
    
    try {
      const result = await this.request({
        url: '/api/memorial/create',
        method: 'POST',
        data: data,
        timeout: 30000  // 30秒超时
      })
      wx.hideLoading()
      return result
    } catch (error) {
      wx.hideLoading()
      throw error
    }
  }

  async updateMemorial(memorialId, data) {
    return this.request({
      url: `/api/memorial/update/${memorialId}`,
      method: 'PUT',
      data: data
    })
  }

  async deleteMemorial(memorialId) {
    return this.request({
      url: `/api/memorial/delete/${memorialId}`,
      method: 'DELETE'
    })
  }

  async uploadMemorialPhotos(memorialId, photos) {
    return this.request({
      url: `/api/memorial/upload-photos/${memorialId}`,
      method: 'POST',
      data: { photos: photos }
    })
  }

  async deleteMemorialPhoto(memorialId, photoId) {
    return this.request({
      url: `/api/memorial/delete-photo/${memorialId}`,
      method: 'DELETE',
      data: { photo_id: photoId }
    })
  }

  // 照片相关API
  async getPhotos() {
    return this.request({
      url: '/api/user/photos'
    })
  }

  async uploadPhoto(filePath) {
    const app = this.getApp()
    return new Promise((resolve, reject) => {
      wx.uploadFile({
        url: `${this.baseUrl}/api/photos/upload`,
        filePath: filePath,
        name: 'photo',
        header: {
          'Authorization': `Bearer ${app.globalData.sessionToken}`
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

  async uploadPhotos(files) {
    const uploadPromises = files.map(file => this.uploadPhoto(file))
    return Promise.all(uploadPromises)
  }

  async deletePhoto(photoId) {
    return this.request({
      url: `/api/photos/delete/${photoId}`,
      method: 'DELETE'
    })
  }

  async batchDeletePhotos(photoIds) {
    return this.request({
      url: '/api/photos/batch-delete',
      method: 'POST',
      data: { photo_ids: photoIds }
    })
  }

  // 性格测试相关API
  async getPersonalityQuestions() {
    return this.request({
      url: '/api/personality/questions'
    })
  }

  async submitPersonalityTest(answers) {
    return this.request({
      url: '/api/personality/submit',
      method: 'POST',
      data: { answers: answers }
    })
  }

  async getPersonalityResult(testId) {
    return this.request({
      url: `/api/personality/result/${testId}`
    })
  }

  // 支付相关API
  async getPaymentPlans() {
    return this.request({
      url: '/api/payment/plans'
    })
  }

  async createPaymentOrder(planId, paymentMethod) {
    return this.request({
      url: '/api/payment/create',
      method: 'POST',
      data: { plan_id: planId, payment_method: paymentMethod }
    })
  }

  async getPaymentStatus(orderId) {
    return this.request({
      url: `/api/payment/status/${orderId}`
    })
  }

  async getOrders() {
    return this.request({
      url: '/api/user/orders'
    })
  }

  async getOrderDetail(orderId) {
    return this.request({
      url: `/api/user/orders/${orderId}`
    })
  }

  // 权限相关API
  async checkPermission(permission) {
    return this.request({
      url: `/api/user/permissions/${permission}`
    })
  }

  async getUserPermissions() {
    return this.request({
      url: '/api/user/permissions'
    })
  }

  // 统计相关API
  async getMemorialStats(memorialId) {
    return this.request({
      url: `/api/memorial/stats/${memorialId}`
    })
  }

  async getUserStats() {
    return this.request({
      url: '/api/user/stats'
    })
  }

  // 文件上传
  async uploadFile(filePath, name = 'file', formData = {}) {
    const app = this.getApp()
    return new Promise((resolve, reject) => {
      wx.uploadFile({
        url: `${this.baseUrl}/api/upload`,
        filePath: filePath,
        name: name,
        header: {
          'Authorization': `Bearer ${app.globalData.sessionToken}`
        },
        formData: formData,
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

  // 错误处理
  handleError(error) {
    console.error('API错误:', error)
    
    const errorMessage = error.message || error.errMsg || '未知错误'
    
    if (errorMessage.includes('登录已过期')) {
      return '登录已过期，请重新登录'
    } else if (errorMessage.includes('网络') || errorMessage.includes('timeout')) {
      return '网络连接失败，请检查网络设置'
    } else if (errorMessage.includes('服务器')) {
      return '服务器错误，请稍后重试'
    } else {
      return '操作失败，请稍后重试'
    }
  }
}

// 创建单例
const apiService = new ApiService()

module.exports = apiService