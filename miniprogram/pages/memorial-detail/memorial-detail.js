// pages/memorial-detail/memorial-detail.js
const app = getApp()

Page({
  data: {
    memorialId: null,
    memorialInfo: {}
  },

  onLoad(options) {
    console.log('纪念馆详情页加载', options)
    const { id } = options
    if (id) {
      this.setData({
        memorialId: id
      })
      this.loadMemorialDetail()
    } else {
      wx.showToast({
        title: '参数错误',
        icon: 'none'
      })
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    }
  },

  // 加载纪念馆详情
  async loadMemorialDetail() {
    wx.showLoading({
      title: '加载中...'
    })

    try {
      const res = await app.request({
        url: `/api/memorial/get/${this.data.memorialId}`
      })

      if (res.success) {
        this.setData({
          memorialInfo: res.memorial
        })
      } else {
        wx.showToast({
          title: res.message || '加载失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('加载纪念馆详情失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 预览照片
  previewPhoto(e) {
    const url = e.currentTarget.dataset.url
    const photos = this.data.memorialInfo.photos || []
    wx.previewImage({
      current: url,
      urls: photos
    })
  },

  // 编辑纪念馆
  editMemorial() {
    wx.navigateTo({
      url: `/pages/memorial-edit/memorial-edit?id=${this.data.memorialId}`
    })
  },

  // 分享纪念馆
  shareMemorial() {
    wx.showActionSheet({
      itemList: ['分享给朋友', '分享到朋友圈', '复制链接'],
      success: (res) => {
        switch (res.tapIndex) {
          case 0:
            this.shareToFriend()
            break
          case 1:
            this.shareToMoments()
            break
          case 2:
            this.copyLink()
            break
        }
      }
    })
  },

  // 分享给朋友
  shareToFriend() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })
  },

  // 分享到朋友圈
  shareToMoments() {
    wx.showToast({
      title: '请使用右上角分享',
      icon: 'none'
    })
  },

  // 复制链接
  copyLink() {
    const link = `${app.globalData.baseUrl}/memorial/${this.data.memorialId}`
    wx.setClipboardData({
      data: link,
      success: () => {
        wx.showToast({
          title: '链接已复制',
          icon: 'success'
        })
      }
    })
  },

  // 分享配置
  onShareAppMessage() {
    const { memorialInfo } = this.data
    return {
      title: `${memorialInfo.pet_name}的纪念馆`,
      desc: memorialInfo.description || '珍贵的回忆，永远的陪伴',
      path: `/pages/memorial-detail/memorial-detail?id=${this.data.memorialId}`,
      imageUrl: memorialInfo.photos && memorialInfo.photos.length > 0 ? memorialInfo.photos[0] : ''
    }
  },

  onShareTimeline() {
    const { memorialInfo } = this.data
    return {
      title: `${memorialInfo.pet_name}的纪念馆 - 爪迹星`,
      query: `id=${this.data.memorialId}`,
      imageUrl: memorialInfo.photos && memorialInfo.photos.length > 0 ? memorialInfo.photos[0] : ''
    }
  }
})