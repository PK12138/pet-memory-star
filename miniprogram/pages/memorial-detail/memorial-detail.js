// pages/memorial-detail/memorial-detail.js
const app = getApp()

Page({
  data: {
    memorialId: null,
    memorialInfo: {},
    messages: [],
    newMessage: {
      name: '',
      content: ''
    },
    submitting: false
  },

  onLoad(options) {
    console.log('纪念馆详情页加载', options)
    const { id } = options
    if (id) {
      this.setData({
        memorialId: id
      })
      this.loadMemorialDetail()
      this.loadMessages()
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
  },

  // 加载留言列表
  async loadMessages() {
    try {
      const res = await app.request({
        url: `/api/messages/${this.data.memorialId}`
      })

      if (res.success) {
        this.setData({
          messages: res.messages || []
        })
        console.log('留言加载成功:', res.messages)
      }
    } catch (error) {
      console.error('加载留言失败:', error)
      // 不显示错误提示，避免影响用户体验
    }
  },

  // 昵称输入
  onNameInput(e) {
    this.setData({
      'newMessage.name': e.detail.value
    })
  },

  // 留言内容输入
  onMessageInput(e) {
    this.setData({
      'newMessage.content': e.detail.value
    })
  },

  // 提交留言
  async submitMessage() {
    const { memorialId, newMessage } = this.data

    if (!newMessage.name || !newMessage.name.trim()) {
      wx.showToast({
        title: '请输入昵称',
        icon: 'none'
      })
      return
    }

    if (!newMessage.content || !newMessage.content.trim()) {
      wx.showToast({
        title: '请输入留言内容',
        icon: 'none'
      })
      return
    }

    this.setData({ submitting: true })

    try {
      const res = await app.request({
        url: '/api/message',
        method: 'POST',
        data: {
          memorial_id: memorialId,
          visitor_name: newMessage.name.trim(),
          message: newMessage.content.trim()
        }
      })

      if (res.success) {
        wx.showToast({
          title: '留言成功',
          icon: 'success'
        })

        // 清空输入
        this.setData({
          newMessage: {
            name: '',
            content: ''
          }
        })

        // 重新加载留言列表
        await this.loadMessages()
      } else {
        wx.showToast({
          title: res.message || '留言失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('提交留言失败:', error)
      wx.showToast({
        title: error.message || '留言失败',
        icon: 'none'
      })
    } finally {
      this.setData({ submitting: false })
    }
  }
})