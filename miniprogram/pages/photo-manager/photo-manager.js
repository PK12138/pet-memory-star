// pages/photo-manager/photo-manager.js
const app = getApp()

Page({
  data: {
    photos: [],
    loading: true
  },

  onLoad() {
    console.log('照片管理页加载')
    this.loadPhotos()
  },

  onShow() {
    console.log('照片管理页显示')
    this.loadPhotos()
  },

  onPullDownRefresh() {
    console.log('下拉刷新')
    this.loadPhotos().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  // 加载照片列表
  async loadPhotos() {
    try {
      this.setData({ loading: true })
      
      const res = await app.request({
        url: '/api/user/photos'
      })
      
      if (res.success) {
        this.setData({
          photos: res.photos || []
        })
      } else {
        app.showError(res.message || '加载照片列表失败')
      }
    } catch (error) {
      console.error('加载照片列表失败:', error)
      app.showError('网络错误，请稍后重试')
    } finally {
      this.setData({ loading: false })
    }
  },

  // 上传照片
  uploadPhotos() {
    wx.chooseImage({
      count: 9,
      sizeType: ['original', 'compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        this.uploadFiles(res.tempFilePaths)
      }
    })
  },

  // 上传文件
  async uploadFiles(filePaths) {
    try {
      app.showLoading('上传中...')
      
      const uploadPromises = filePaths.map(filePath => {
        return new Promise((resolve, reject) => {
          wx.uploadFile({
            url: `${app.globalData.baseUrl}/api/photos/upload`,
            filePath: filePath,
            name: 'photos',
            formData: {
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
      })

      const results = await Promise.all(uploadPromises)
      
      app.hideLoading()
      app.showSuccess('上传成功')
      
      // 重新加载照片列表
      this.loadPhotos()
    } catch (error) {
      console.error('上传失败:', error)
      app.hideLoading()
      app.showError('上传失败，请稍后重试')
    }
  },

  // 查看照片
  viewPhoto(e) {
    const photo = e.currentTarget.dataset.photo
    const urls = this.data.photos.map(p => p.url)
    wx.previewImage({
      urls: urls,
      current: photo.url
    })
  },

  // 删除照片
  deletePhoto(e) {
    e.stopPropagation()
    const photoId = e.currentTarget.dataset.id
    
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这张照片吗？',
      success: async (res) => {
        if (res.confirm) {
          await this.confirmDelete(photoId)
        }
      }
    })
  },

  // 确认删除
  async confirmDelete(photoId) {
    try {
      app.showLoading('删除中...')
      
      const res = await app.request({
        url: `/api/photos/delete/${photoId}`,
        method: 'DELETE'
      })
      
      if (res.success) {
        app.hideLoading()
        app.showSuccess('照片删除成功')
        this.loadPhotos() // 重新加载列表
      } else {
        app.hideLoading()
        app.showError(res.message || '删除失败')
      }
    } catch (error) {
      console.error('删除照片失败:', error)
      app.hideLoading()
      app.showError('网络错误，请稍后重试')
    }
  },

  // 阻止事件冒泡
  stopPropagation() {
    // 空函数，用于阻止事件冒泡
  }
})
