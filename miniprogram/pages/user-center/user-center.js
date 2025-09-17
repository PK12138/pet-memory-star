// pages/user-center/user-center.js
const app = getApp()

Page({
  data: {
    userInfo: null,
    userLevel: 0,
    levelInfo: {},
    stats: {
      memorialCount: 0,
      photoCount: 0,
      totalViews: 0,
      aiUsage: 0
    },
    permissions: {
      canCreateMemorial: false,
      canUploadPhoto: false,
      canUseAI: false,
      canExportData: false
    }
  },

  onLoad() {
    console.log('个人中心页加载')
    this.loadUserData()
  },

  onShow() {
    console.log('个人中心页显示')
    this.loadUserData()
  },

  onPullDownRefresh() {
    console.log('下拉刷新')
    this.loadUserData().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  // 加载用户数据
  async loadUserData() {
    try {
      const userInfo = app.globalData.userInfo
      const sessionToken = app.globalData.sessionToken
      
      if (!userInfo || !sessionToken) {
        wx.showToast({
          title: '请先登录',
          icon: 'none'
        })
        setTimeout(() => {
          wx.navigateTo({
            url: '/pages/login/login'
          })
        }, 1500)
        return
      }
      
      this.setData({
        userInfo: userInfo,
        userLevel: app.globalData.userLevel || 0
      })
      
      // 并行加载所有数据
      await Promise.all([
        this.loadLevelInfo(),
        this.loadStats(),
        this.loadPermissions()
      ])
      
    } catch (error) {
      console.error('加载用户数据失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  // 加载等级信息
  async loadLevelInfo() {
    try {
      const res = await app.request({
        url: '/api/user/level-info'
      })
      
      if (res.success) {
        this.setData({
          levelInfo: res.level_info
        })
      }
    } catch (error) {
      console.error('加载等级信息失败:', error)
    }
  },

  // 加载统计数据
  async loadStats() {
    try {
      const res = await app.request({
        url: '/api/user/dashboard'
      })
      
      if (res.success) {
        this.setData({
          stats: {
            memorialCount: res.data.memorial_count || 0,
            photoCount: res.data.total_photos || 0,
            totalViews: res.data.total_views || 0,
            aiUsage: res.data.ai_usage || 0
          }
        })
      }
    } catch (error) {
      console.error('加载统计数据失败:', error)
    }
  },

  // 加载权限信息
  async loadPermissions() {
    try {
      const res = await app.request({
        url: '/api/user/permissions'
      })
      
      if (res.success) {
        this.setData({
          permissions: {
            canCreateMemorial: res.permissions.can_create_memorial || false,
            canUploadPhoto: res.permissions.can_upload_photo || false,
            canUseAI: res.permissions.can_use_ai || false,
            canExportData: res.permissions.can_export_data || false
          }
        })
      }
    } catch (error) {
      console.error('加载权限信息失败:', error)
    }
  },

  // 跳转到纪念馆列表
  goToMemorials() {
    wx.navigateTo({
      url: '/pages/memorials/memorials'
    })
  },

  // 跳转到照片管理
  goToPhotoManager() {
    wx.navigateTo({
      url: '/pages/photo-manager/photo-manager'
    })
  },

  // 跳转到订单管理
  goToOrders() {
    wx.navigateTo({
      url: '/pages/orders/orders'
    })
  },

  // 跳转到充值页面
  goToPayment() {
    wx.navigateTo({
      url: '/pages/payment/payment'
    })
  },

  // 退出登录
  logout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await app.request({
              url: '/api/auth/logout',
              method: 'POST'
            })
          } catch (error) {
            console.error('退出登录请求失败:', error)
          } finally {
            // 清除本地存储
            app.logout()
            wx.showToast({
              title: '已退出登录',
              icon: 'success'
            })
            setTimeout(() => {
              wx.switchTab({
                url: '/pages/index/index'
              })
            }, 1500)
          }
        }
      }
    })
  }
})