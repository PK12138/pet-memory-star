// utils/api.js
// API请求工具类

const app = getApp()
const config = require('../config/config')

class ApiService {
  constructor() {
    this.baseUrl = config.baseUrl
  }

  // 通用请求方法
  async request(options) {
    const { url, method = 'GET', data = {}, header = {} } = options
    
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.baseUrl}${url}`,
        method: method,
        data: data,
        header: {
          'Content-Type': 'application/json',
          'X-Session-Token': app.globalData.sessionToken,
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

  // 照片相关API
  async getPhotos() {
    return this.request({
      url: '/api/user/photos'
    })
  }

  async uploadPhotos(files) {
    return new Promise((resolve, reject) => {
      const uploadPromises = files.map(file => {
        return new Promise((resolveFile, rejectFile) => {
          wx.uploadFile({
            url: `${this.baseUrl}/api/photos/upload`,
            filePath: file,
            name: 'photos',
            formData: {
              session_token: app.globalData.sessionToken
            },
            success: (res) => {
              try {
                const data = JSON.parse(res.data)
                resolveFile(data)
              } catch (error) {
                rejectFile(error)
              }
            },
            fail: rejectFile
          })
        })
      })

      Promise.all(uploadPromises)
        .then(resolve)
        .catch(reject)
    })
  }

  async deletePhoto(photoId) {
    return this.request({
      url: `/api/photos/delete/${photoId}`,
      method: 'DELETE'
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

  async getOrders() {
    return this.request({
      url: '/api/user/orders'
    })
  }

  // 权限相关API
  async checkPermission(permission) {
    return this.request({
      url: `/api/user/permissions/${permission}`
    })
  }

  // 文件上传
  async uploadFile(filePath, name = 'file', formData = {}) {
    return new Promise((resolve, reject) => {
      wx.uploadFile({
        url: `${this.baseUrl}/api/upload`,
        filePath: filePath,
        name: name,
        formData: {
          ...formData,
          session_token: app.globalData.sessionToken
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
}

// 创建单例
const apiService = new ApiService()

module.exports = apiService
