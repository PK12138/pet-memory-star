// pages/memorials/memorials.js
const app = getApp()

Page({
  data: {
    memorials: [],
    loading: false
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
    this.setData({
      loading: true
    })

    try {
      const res = await app.request({
        url: '/api/user/memorials'
      })

      if (res.success) {
        this.setData({
          memorials: res.memorials || []
        })
      } else {
        wx.showToast({
          title: res.message || '加载失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('加载纪念馆列表失败:', error)
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