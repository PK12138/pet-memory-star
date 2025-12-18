// utils/wechat.js
// 微信API工具类

const config = require('../config/config')

class WechatAPI {
  constructor() {
    this.appId = config.appId
    this.baseUrl = config.wechatApiUrl
  }

  // 重要：小程序端不应获取 access_token（需要 AppSecret）。
  // 如需 access_token，请在服务端实现并通过后端接口代理。

  // 获取用户信息（需要用户授权）
  getUserInfo() {
    return new Promise((resolve, reject) => {
      wx.getUserProfile({
        desc: '用于完善用户资料',
        success: (res) => {
          resolve(res.userInfo)
        },
        fail: (error) => {
          reject(error)
        }
      })
    })
  }

  // 获取用户位置信息
  getLocation() {
    return new Promise((resolve, reject) => {
      wx.getLocation({
        type: 'wgs84',
        success: (res) => {
          resolve({
            latitude: res.latitude,
            longitude: res.longitude,
            speed: res.speed,
            accuracy: res.accuracy
          })
        },
        fail: (error) => {
          reject(error)
        }
      })
    })
  }

  // 选择图片
  chooseImage(options = {}) {
    const defaultOptions = {
      count: 1,
      sizeType: ['original', 'compressed'],
      sourceType: ['album', 'camera']
    }
    
    return new Promise((resolve, reject) => {
      wx.chooseImage({
        ...defaultOptions,
        ...options,
        success: resolve,
        fail: reject
      })
    })
  }

  // 选择视频
  chooseVideo(options = {}) {
    const defaultOptions = {
      sourceType: ['album', 'camera'],
      maxDuration: 60,
      camera: 'back'
    }
    
    return new Promise((resolve, reject) => {
      wx.chooseVideo({
        ...defaultOptions,
        ...options,
        success: resolve,
        fail: reject
      })
    })
  }

  // 预览图片
  previewImage(urls, current) {
    wx.previewImage({
      urls: urls,
      current: current || urls[0]
    })
  }

  // 保存图片到相册
  saveImageToPhotosAlbum(filePath) {
    return new Promise((resolve, reject) => {
      wx.saveImageToPhotosAlbum({
        filePath: filePath,
        success: resolve,
        fail: reject
      })
    })
  }

  // 分享到微信
  shareToWeChat(title, path, imageUrl) {
    return {
      title: title,
      path: path,
      imageUrl: imageUrl
    }
  }

  // 分享到朋友圈
  shareToMoments(title, path, imageUrl) {
    return {
      title: title,
      path: path,
      imageUrl: imageUrl
    }
  }

  // 设置剪贴板
  setClipboardData(data) {
    return new Promise((resolve, reject) => {
      wx.setClipboardData({
        data: data,
        success: resolve,
        fail: reject
      })
    })
  }

  // 获取剪贴板数据
  getClipboardData() {
    return new Promise((resolve, reject) => {
      wx.getClipboardData({
        success: resolve,
        fail: reject
      })
    })
  }

  // 显示模态对话框
  showModal(title, content) {
    return new Promise((resolve) => {
      wx.showModal({
        title: title,
        content: content,
        success: (res) => {
          resolve(res.confirm)
        }
      })
    })
  }

  // 显示操作菜单
  showActionSheet(itemList) {
    return new Promise((resolve, reject) => {
      wx.showActionSheet({
        itemList: itemList,
        success: resolve,
        fail: reject
      })
    })
  }

  // 显示加载提示
  showLoading(title = '加载中...') {
    wx.showLoading({
      title: title,
      mask: true
    })
  }

  // 隐藏加载提示
  hideLoading() {
    wx.hideLoading()
  }

  // 显示成功提示
  showSuccess(title) {
    wx.showToast({
      title: title,
      icon: 'success',
      duration: 2000
    })
  }

  // 显示错误提示
  showError(title) {
    wx.showToast({
      title: title,
      icon: 'none',
      duration: 2000
    })
  }

  // 显示普通提示
  showToast(title, icon = 'none') {
    wx.showToast({
      title: title,
      icon: icon,
      duration: 2000
    })
  }

  // 获取系统信息
  getSystemInfo() {
    return new Promise((resolve, reject) => {
      wx.getSystemInfo({
        success: resolve,
        fail: reject
      })
    })
  }

  // 获取网络状态
  getNetworkType() {
    return new Promise((resolve, reject) => {
      wx.getNetworkType({
        success: resolve,
        fail: reject
      })
    })
  }

  // 监听网络状态变化
  onNetworkStatusChange(callback) {
    wx.onNetworkStatusChange(callback)
  }

  // 监听页面显示
  onShow(callback) {
    wx.onShow(callback)
  }

  // 监听页面隐藏
  onHide(callback) {
    wx.onHide(callback)
  }

  // 监听页面错误
  onError(callback) {
    wx.onError(callback)
  }
}

// 创建单例
const wechatAPI = new WechatAPI()

module.exports = wechatAPI
