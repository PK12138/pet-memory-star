// pages/memorials/memorials.js
const app = getApp()

Page({
  data: {
    memorials: [],
    loading: true
  },

  onLoad() {
    console.log('纪念馆列表页加载')
    this.loadMemorials()
  },

  onShow() {
    console.log('纪念馆列表页显示')
    this.loadMemorials()
  },

  onPullDownRefresh() {
    console.log('下拉刷新')
    this.loadMemorials().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  // 加载纪念馆列表
  async loadMemorials() {
    try {
      this.setData({ loading: true })
      
      const res = await app.request({
        url: '/api/user/memorials'
      })
      
      if (res.success) {
        this.setData({
          memorials: res.memorials || []
        })
      } else {
        app.showError(res.message || '加载纪念馆列表失败')
      }
    } catch (error) {
      console.error('加载纪念馆列表失败:', error)
      app.showError('网络错误，请稍后重试')
    } finally {
      this.setData({ loading: false })
    }
  },

  // 跳转到纪念馆详情
  goToMemorialDetail(e) {
    const memorialId = e.currentTarget.dataset.memorialId
    wx.navigateTo({
      url: `/pages/memorial-detail/memorial-detail?id=${memorialId}`
    })
  },

  // 编辑纪念馆
  editMemorial(e) {
    e.stopPropagation()
    const memorialId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/memorial-edit/memorial-edit?id=${memorialId}`
    })
  },

  // 分享纪念馆
  shareMemorial(e) {
    e.stopPropagation()
    const memorialId = e.currentTarget.dataset.id
    
    wx.showActionSheet({
      itemList: ['分享到微信', '分享到朋友圈', '复制链接'],
      success: (res) => {
        switch (res.tapIndex) {
          case 0:
            this.shareToWeChat(memorialId)
            break
          case 1:
            this.shareToMoments(memorialId)
            break
          case 2:
            this.copyLink(memorialId)
            break
        }
      }
    })
  },

  // 分享到微信
  shareToWeChat(memorialId) {
    const shareUrl = `${app.globalData.baseUrl}/memorial/${memorialId}`
    wx.setClipboardData({
      data: shareUrl,
      success: () => {
        app.showSuccess('链接已复制，可以分享给好友')
      }
    })
  },

  // 分享到朋友圈
  shareToMoments(memorialId) {
    const shareUrl = `${app.globalData.baseUrl}/memorial/${memorialId}`
    wx.setClipboardData({
      data: shareUrl,
      success: () => {
        app.showSuccess('链接已复制，可以分享到朋友圈')
      }
    })
  },

  // 复制链接
  copyLink(memorialId) {
    const shareUrl = `${app.globalData.baseUrl}/memorial/${memorialId}`
    wx.setClipboardData({
      data: shareUrl,
      success: () => {
        app.showSuccess('链接已复制到剪贴板')
      }
    })
  },

  // 删除纪念馆
  deleteMemorial(e) {
    e.stopPropagation()
    const memorialId = e.currentTarget.dataset.id
    
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这个纪念馆吗？删除后将无法恢复。',
      success: async (res) => {
        if (res.confirm) {
          await this.confirmDelete(memorialId)
        }
      }
    })
  },

  // 确认删除
  async confirmDelete(memorialId) {
    try {
      app.showLoading('删除中...')
      
      const res = await app.request({
        url: `/api/memorial/delete/${memorialId}`,
        method: 'DELETE'
      })
      
      if (res.success) {
        app.hideLoading()
        app.showSuccess('纪念馆删除成功')
        this.loadMemorials() // 重新加载列表
      } else {
        app.hideLoading()
        app.showError(res.message || '删除失败')
      }
    } catch (error) {
      console.error('删除纪念馆失败:', error)
      app.hideLoading()
      app.showError('网络错误，请稍后重试')
    }
  },

  // 查看照片
  viewPhoto(e) {
    const photo = e.currentTarget.dataset.photo
    wx.previewImage({
      urls: [photo],
      current: photo
    })
  },

  // 跳转到创建纪念馆
  goToCreateMemorial() {
    wx.navigateTo({
      url: '/pages/personality-test/personality-test'
    })
  },

  // 阻止事件冒泡
  stopPropagation() {
    // 空函数，用于阻止事件冒泡
  }
})
