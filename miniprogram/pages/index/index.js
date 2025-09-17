// pages/index/index.js
const app = getApp()

Page({
  data: {
    userInfo: null,
    userLevel: 0,
    levelInfo: {},
    stats: {
      memorialCount: 0,
      photoCount: 0,
      totalViews: 0
    }
  },

  onLoad() {
    console.log('首页加载')
    this.checkAuthStatus()
  },

  onShow() {
    console.log('首页显示')
    this.checkAuthStatus()
  },

  onPullDownRefresh() {
    console.log('下拉刷新')
    this.checkAuthStatus().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  // 检查用户登录状态
  async checkAuthStatus() {
    try {
      const userInfo = app.globalData.userInfo
      const sessionToken = app.globalData.sessionToken
      
      if (userInfo && sessionToken) {
        this.setData({
          userInfo: userInfo,
          userLevel: app.globalData.userLevel || 0
        })
        
        // 加载用户等级信息
        await this.loadLevelInfo()
        
        // 加载统计数据
        await this.loadStats()
      } else {
        this.setData({
          userInfo: null,
          userLevel: 0,
          levelInfo: {},
          stats: {
            memorialCount: 0,
            photoCount: 0,
            totalViews: 0
          }
        })
      }
    } catch (error) {
      console.error('检查登录状态失败:', error)
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
            totalViews: res.data.total_views || 0
          }
        })
      }
    } catch (error) {
      console.error('加载统计数据失败:', error)
    }
  },

  // 开始创建纪念馆
  startCreateMemorial() {
    const sessionToken = app.globalData.sessionToken
    
    if (!sessionToken) {
      // 未登录，跳转到登录页面
      wx.navigateTo({
        url: '/pages/login/login'
      })
      return
    }
    
    // 已登录，跳转到性格测试页面
    wx.navigateTo({
      url: '/pages/personality-test/personality-test'
    })
  },

  // 跳转到登录页
  goToLogin() {
    wx.navigateTo({
      url: '/pages/login/login'
    })
  },

  // 跳转到注册页
  goToRegister() {
    wx.navigateTo({
      url: '/pages/register/register'
    })
  },

  // 跳转到纪念馆列表
  goToMemorials() {
    wx.navigateTo({
      url: '/pages/memorials/memorials'
    })
  },

  // 跳转到个人中心
  goToUserCenter() {
    wx.navigateTo({
      url: '/pages/user-center/user-center'
    })
  },

  // 跳转到照片管理
  goToPhotoManager() {
    wx.navigateTo({
      url: '/pages/photo-manager/photo-manager'
    })
  },

  // 跳转到性格测试
  goToPersonalityTest() {
    wx.navigateTo({
      url: '/pages/personality-test/personality-test'
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
            this.setData({
              userInfo: null,
              userLevel: 0,
              levelInfo: {},
              stats: {
                memorialCount: 0,
                photoCount: 0,
                totalViews: 0
              }
            })
            app.showSuccess('已退出登录')
          }
        }
      }
    })
  }
})