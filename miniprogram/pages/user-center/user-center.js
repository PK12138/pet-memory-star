// pages/user-center/user-center.js
const app = getApp()

Page({
  data: {
    userInfo: null,
    levelInfo: {}
  },

  onLoad() {
    console.log('个人中心页加载')
    this.loadUserData()
  },

  onShow() {
    console.log('个人中心页显示')
    this.loadUserData()
  },

  // 加载用户数据
  async loadUserData() {
    try {
      const userInfo = app.globalData.userInfo
      if (userInfo) {
        this.setData({
          userInfo: userInfo
        })
        
        // 加载用户等级信息
        await this.loadLevelInfo()
      } else {
        // 未登录，跳转到登录页
        wx.navigateTo({
          url: '/pages/login/login'
        })
      }
    } catch (error) {
      console.error('加载用户数据失败:', error)
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

  // 跳转到纪念馆列表
  goToMemorials() {
    wx.switchTab({
      url: '/pages/memorials/memorials'
    })
  },

  // 跳转到照片管理
  goToPhotoManager() {
    wx.switchTab({
      url: '/pages/photo-manager/photo-manager'
    })
  },

  // 跳转到充值页面
  goToPayment() {
    wx.navigateTo({
      url: '/pages/payment/payment'
    })
  },

  // 跳转到订单管理
  goToOrders() {
    wx.navigateTo({
      url: '/pages/orders/orders'
    })
  },

  // 退出登录
  logout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          app.logout()
          wx.switchTab({
            url: '/pages/index/index'
          })
          app.showSuccess('已退出登录')
        }
      }
    })
  }
})
