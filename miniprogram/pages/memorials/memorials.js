// pages/memorials/memorials.js
const app = getApp()

Page({
  data: {
    memorials: [],
    loading: false
  },

  onLoad() {
    console.log('纪念馆列表页加载')
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
    // 检查登录状态
    if (!app.globalData.sessionToken) {
      console.warn('用户未登录，跳转到登录页')
      wx.redirectTo({
        url: '/pages/login/login'
      })
      return
    }

    this.setData({
      loading: true
    })

    try {
      console.log('开始加载纪念馆列表，Token:', app.globalData.sessionToken)
      const res = await app.request({
        url: '/api/user/memorials'
      })

      if (res.success) {
        console.log('获取到纪念馆列表:', res.memorials)
        
        // 将照片相对路径转换为完整URL
        const memorials = (res.memorials || []).map(memorial => {
          if (memorial.photos && Array.isArray(memorial.photos)) {
            memorial.photos = memorial.photos.map(photo => {
              // 如果是相对路径，拼接完整URL
              if (photo && photo.startsWith('/')) {
                return `${app.globalData.baseUrl}${photo}`
              }
              return photo
            })
          }
          return memorial
        })
        
        this.setData({
          memorials: memorials
        })
      } else {
        console.warn('加载纪念馆列表失败:', res.message)
        if (res.message && res.message.includes('未登录')) {
          wx.redirectTo({
            url: '/pages/login/login'
          })
        } else {
          wx.showModal({
            title: '加载失败',
            content: '是否重试？',
            success: (modalRes) => {
              if (modalRes.confirm) {
                this.loadMemorials()
              }
            }
          })
        }
      }
    } catch (error) {
      console.error('加载纪念馆列表失败:', error)
      if (error.statusCode === 401) {
        wx.redirectTo({
          url: '/pages/login/login'
        })
      } else {
        wx.showModal({
          title: '网络错误',
          content: '是否重试？',
          success: (modalRes) => {
            if (modalRes.confirm) {
              this.loadMemorials()
            }
          }
        })
      }
    } finally {
      this.setData({
        loading: false
      })
    }
  },

  // 跳转到纪念馆详情
  goToMemorialDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/memorial-detail/memorial-detail?id=${id}`
    })
  },

  // 编辑纪念馆
  editMemorial(e) {
    e.stopPropagation()
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/memorial-edit/memorial-edit?id=${id}`
    })
  },

  // 删除纪念馆
  deleteMemorial(e) {
    e.stopPropagation()
    const id = e.currentTarget.dataset.id
    const memorial = this.data.memorials.find(m => m.id === id)
    
    if (!memorial) return

    wx.showModal({
      title: '确认删除',
      content: `确定要删除"${memorial.pet_name}"的纪念馆吗？此操作不可恢复。`,
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
        url: `/api/memorial/delete/${id}`,
        method: 'DELETE'
      })

      if (res.success) {
        wx.showToast({
          title: '删除成功',
          icon: 'success'
        })
        
        // 从列表中移除
        const memorials = this.data.memorials.filter(m => m.id !== id)
        this.setData({
          memorials
        })
      } else {
        wx.showToast({
          title: res.message || '删除失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('删除纪念馆失败:', error)
      wx.showToast({
        title: '删除失败',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
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