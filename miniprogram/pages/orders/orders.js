// pages/orders/orders.js
const app = getApp()

Page({
  data: {
    orders: [],
    loading: true
  },

  onLoad() {
    console.log('订单管理页加载')
    this.loadOrders()
  },

  onShow() {
    console.log('订单管理页显示')
    this.loadOrders()
  },

  onPullDownRefresh() {
    console.log('下拉刷新')
    this.loadOrders().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  // 加载订单列表
  async loadOrders() {
    try {
      this.setData({ loading: true })
      
      const res = await app.request({
        url: '/api/user/orders'
      })
      
      if (res.success) {
        this.setData({
          orders: res.orders || []
        })
      } else {
        app.showError(res.message || '加载订单列表失败')
      }
    } catch (error) {
      console.error('加载订单列表失败:', error)
      app.showError('网络错误，请稍后重试')
    } finally {
      this.setData({ loading: false })
    }
  },

  // 跳转到充值页面
  goToPayment() {
    wx.navigateTo({
      url: '/pages/payment/payment'
    })
  }
})
