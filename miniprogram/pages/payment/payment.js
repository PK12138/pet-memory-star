// pages/payment/payment.js
const app = getApp()

Page({
  data: {
    plans: [],
    paymentMethods: [
      { id: 'wechat', name: '微信支付', icon: '💚' },
      { id: 'alipay', name: '支付宝', icon: '💙' }
    ],
    selectedPlan: null,
    selectedPayment: null,
    loading: false
  },

  onLoad() {
    console.log('充值页面加载')
    this.loadPlans()
  },

  // 加载套餐列表
  async loadPlans() {
    try {
      const res = await app.request({
        url: '/api/payment/plans'
      })
      
      if (res.success) {
        this.setData({
          plans: res.plans || []
        })
      } else {
        app.showError(res.message || '加载套餐失败')
      }
    } catch (error) {
      console.error('加载套餐失败:', error)
      app.showError('网络错误，请稍后重试')
    }
  },

  // 选择套餐
  selectPlan(e) {
    const planId = e.currentTarget.dataset.planId
    this.setData({
      selectedPlan: planId
    })
  },

  // 选择支付方式
  selectPayment(e) {
    const paymentId = e.currentTarget.dataset.paymentId
    this.setData({
      selectedPayment: paymentId
    })
  },

  // 创建支付
  async createPayment() {
    const { selectedPlan, selectedPayment } = this.data
    
    if (!selectedPlan) {
      app.showError('请选择套餐')
      return
    }
    
    if (!selectedPayment) {
      app.showError('请选择支付方式')
      return
    }
    
    this.setData({ loading: true })
    app.showLoading('创建订单中...')
    
    try {
      const res = await app.request({
        url: '/api/payment/create',
        method: 'POST',
        data: {
          plan_id: selectedPlan,
          payment_method: selectedPayment
        }
      })
      
      if (res.success) {
        app.hideLoading()
        
        if (selectedPayment === 'wechat') {
          // 微信支付
          this.handleWeChatPay(res.payment_data)
        } else if (selectedPayment === 'alipay') {
          // 支付宝支付
          this.handleAlipay(res.payment_data)
        }
      } else {
        app.hideLoading()
        app.showError(res.message || '创建订单失败')
      }
    } catch (error) {
      console.error('创建支付失败:', error)
      app.hideLoading()
      app.showError('网络错误，请稍后重试')
    } finally {
      this.setData({ loading: false })
    }
  },

  // 处理微信支付
  handleWeChatPay(paymentData) {
    wx.requestPayment({
      timeStamp: paymentData.timeStamp,
      nonceStr: paymentData.nonceStr,
      package: paymentData.package,
      signType: paymentData.signType,
      paySign: paymentData.paySign,
      success: (res) => {
        app.showSuccess('支付成功')
        // 跳转到订单页面
        wx.navigateTo({
          url: '/pages/orders/orders'
        })
      },
      fail: (error) => {
        console.error('支付失败:', error)
        app.showError('支付失败')
      }
    })
  },

  // 处理支付宝支付
  handleAlipay(paymentData) {
    // 支付宝支付处理
    app.showSuccess('支付成功')
    wx.navigateTo({
      url: '/pages/orders/orders'
    })
  }
})
