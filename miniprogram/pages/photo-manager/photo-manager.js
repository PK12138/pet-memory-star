// pages/photo-manager/photo-manager.js
const app = getApp()

Page({
  data: {
    photos: [],
    currentFilter: 'all',
    totalPhotos: 0,
    memorialPhotos: 0,
    recentPhotos: 0,
    selectMode: false,
    selectedCount: 0,
    allSelected: false,
    loading: false
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
    this.setData({
      loading: true
    })

    try {
      const res = await app.request({
        url: '/api/user/photos'
      })

      if (res.success) {
        const photos = res.photos || []
        this.setData({
          photos: photos.map(photo => ({
            ...photo,
            selected: false
          })),
          totalPhotos: photos.length,
          memorialPhotos: photos.filter(p => p.memorial_id).length,
          recentPhotos: photos.filter(p => {
            const uploadDate = new Date(p.upload_date)
            const weekAgo = new Date()
            weekAgo.setDate(weekAgo.getDate() - 7)
            return uploadDate > weekAgo
          }).length
        })
        
        this.filterPhotos()
      } else {
        wx.showToast({
          title: res.message || '加载失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('加载照片列表失败:', error)
      wx.showToast({
        title: '网络错误',
        icon: 'none'
      })
    } finally {
      this.setData({
        loading: false
      })
    }
  },

  // 筛选照片
  filterPhotos() {
    const { photos, currentFilter } = this.data
    let filteredPhotos = photos

    switch (currentFilter) {
      case 'memorial':
        filteredPhotos = photos.filter(p => p.memorial_id)
        break
      case 'recent':
        filteredPhotos = photos.filter(p => {
          const uploadDate = new Date(p.upload_date)
          const weekAgo = new Date()
          weekAgo.setDate(weekAgo.getDate() - 7)
          return uploadDate > weekAgo
        })
        break
      default:
        filteredPhotos = photos
    }

    this.setData({
      photos: filteredPhotos
    })
  },

  // 切换筛选器
  switchFilter(e) {
    const filter = e.currentTarget.dataset.filter
    this.setData({
      currentFilter: filter
    })
    this.filterPhotos()
  },

  // 选择照片
  choosePhotos() {
    wx.chooseImage({
      count: 9,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        this.uploadPhotos(res.tempFilePaths)
      },
      fail: (error) => {
        console.error('选择照片失败:', error)
        wx.showToast({
          title: '选择照片失败',
          icon: 'none'
        })
      }
    })
  },

  // 上传照片
  async uploadPhotos(filePaths) {
    wx.showLoading({
      title: '上传中...'
    })

    try {
      const uploadPromises = filePaths.map(filePath => this.uploadSinglePhoto(filePath))
      const results = await Promise.all(uploadPromises)
      
      const successCount = results.filter(r => r.success).length
      
      if (successCount > 0) {
        wx.showToast({
          title: `成功上传${successCount}张照片`,
          icon: 'success'
        })
        this.loadPhotos()
      } else {
        wx.showToast({
          title: '上传失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('上传照片失败:', error)
      wx.showToast({
        title: '上传失败',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 上传单张照片
  uploadSinglePhoto(filePath) {
    return new Promise((resolve) => {
      wx.uploadFile({
        url: `${app.globalData.baseUrl}/api/photos/upload`,
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
            resolve({ success: false, message: '上传失败' })
          }
        },
        fail: () => {
          resolve({ success: false, message: '上传失败' })
        }
      })
    })
  },

  // 预览照片
  previewPhoto(e) {
    const index = e.currentTarget.dataset.index
    const photos = this.data.photos
    const urls = photos.map(p => p.url)
    
    wx.previewImage({
      current: urls[index],
      urls: urls
    })
  },

  // 编辑照片
  editPhoto(e) {
    e.stopPropagation()
    const id = e.currentTarget.dataset.id
    // 这里可以跳转到照片编辑页面
    wx.showToast({
      title: '编辑功能开发中',
      icon: 'none'
    })
  },

  // 删除照片
  deletePhoto(e) {
    e.stopPropagation()
    const id = e.currentTarget.dataset.id
    const photo = this.data.photos.find(p => p.id === id)
    
    if (!photo) return

    wx.showModal({
      title: '确认删除',
      content: `确定要删除这张照片吗？此操作不可恢复。`,
      confirmText: '删除',
      confirmColor: '#e74c3c',
      success: async (res) => {
        if (res.confirm) {
          await this.performDelete(id)
        }
      }
    })
  },

  // 执行删除操作
  async performDelete(id) {
    wx.showLoading({
      title: '删除中...'
    })

    try {
      const res = await app.request({
        url: `/api/photos/delete/${id}`,
        method: 'DELETE'
      })

      if (res.success) {
        wx.showToast({
          title: '删除成功',
          icon: 'success'
        })
        
        // 从列表中移除
        const photos = this.data.photos.filter(p => p.id !== id)
        this.setData({
          photos
        })
      } else {
        wx.showToast({
          title: res.message || '删除失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('删除照片失败:', error)
      wx.showToast({
        title: '删除失败',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 进入选择模式
  enterSelectMode() {
    this.setData({
      selectMode: true
    })
  },

  // 退出选择模式
  exitSelectMode() {
    this.setData({
      selectMode: false,
      allSelected: false,
      selectedCount: 0,
      photos: this.data.photos.map(p => ({
        ...p,
        selected: false
      }))
    })
  },

  // 切换选择状态
  toggleSelect(e) {
    e.stopPropagation()
    const id = e.currentTarget.dataset.id
    const photos = this.data.photos.map(p => {
      if (p.id === id) {
        p.selected = !p.selected
      }
      return p
    })
    
    const selectedCount = photos.filter(p => p.selected).length
    const allSelected = selectedCount === photos.length

    this.setData({
      photos,
      selectedCount,
      allSelected
    })
  },

  // 全选/取消全选
  selectAll() {
    const { allSelected, photos } = this.data
    const newSelected = !allSelected
    
    this.setData({
      photos: photos.map(p => ({
        ...p,
        selected: newSelected
      })),
      allSelected: newSelected,
      selectedCount: newSelected ? photos.length : 0
    })
  },

  // 批量删除
  batchDelete() {
    const selectedPhotos = this.data.photos.filter(p => p.selected)
    
    if (selectedPhotos.length === 0) {
      wx.showToast({
        title: '请选择要删除的照片',
        icon: 'none'
      })
      return
    }

    wx.showModal({
      title: '确认删除',
      content: `确定要删除选中的${selectedPhotos.length}张照片吗？此操作不可恢复。`,
      confirmText: '删除',
      confirmColor: '#e74c3c',
      success: async (res) => {
        if (res.confirm) {
          await this.performBatchDelete(selectedPhotos)
        }
      }
    })
  },

  // 执行批量删除
  async performBatchDelete(selectedPhotos) {
    wx.showLoading({
      title: '删除中...'
    })

    try {
      const deletePromises = selectedPhotos.map(photo => 
        app.request({
          url: `/api/photos/delete/${photo.id}`,
          method: 'DELETE'
        })
      )
      
      await Promise.all(deletePromises)
      
      wx.showToast({
        title: '删除成功',
        icon: 'success'
      })
      
      this.exitSelectMode()
      this.loadPhotos()
    } catch (error) {
      console.error('批量删除失败:', error)
      wx.showToast({
        title: '删除失败',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 阻止事件冒泡
  stopPropagation() {
    // 空函数，用于阻止事件冒泡
  }
})