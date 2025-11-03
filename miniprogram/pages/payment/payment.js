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
      console.log('🔹 创建支付订单:', {
        plan_id: selectedPlan,
        payment_method: selectedPayment
      })
      
      const res = await app.request({
        url: '/api/payment/create',
        method: 'POST',
        data: {
          plan_id: selectedPlan,
          payment_method: selectedPayment
        }
      })
      
      console.log('📦 后端返回:', res)
      
      if (res.success) {
        app.hideLoading()
        
        if (selectedPayment === 'wechat') {
          // 微信支付
          console.log('💰 调用微信支付:', res.payment_data)
          this.handleWeChatPay(res.payment_data, res.order_id)
        } else if (selectedPayment === 'alipay') {
          // 支付宝支付
          this.handleAlipay(res.payment_data)
        }
      } else {
        app.hideLoading()
        console.error('❌ 创建订单失败:', res.message)
        app.showError(res.message || '创建订单失败')
      }
    } catch (error) {
      console.error('❌ 创建支付失败:', error)
      app.hideLoading()
      app.showError('网络错误，请稍后重试')
    } finally {
      this.setData({ loading: false })
    }
  },

  // 处理微信支付
  handleWeChatPay(paymentData, orderId) {
    if (!paymentData) {
      app.showError('支付参数错误')
      return
    }
    
    console.log('🔑 微信支付参数:', paymentData)
    
    wx.requestPayment({
      timeStamp: paymentData.timeStamp,
      nonceStr: paymentData.nonceStr,
      package: paymentData.package,
      signType: paymentData.signType,
      paySign: paymentData.paySign,
      success: (res) => {
        console.log('✅ 支付成功:', res)
        app.showSuccess('支付成功')
        
        // 延时跳转，让用户看到成功提示
        setTimeout(() => {
          wx.navigateTo({
            url: '/pages/orders/orders'
          })
        }, 1500)
      },
      fail: (error) => {
        console.error('❌ 支付失败:', error)
        
        if (error.errMsg.indexOf('cancel') > -1) {
          app.showToast('支付已取消')
        } else {
          app.showError('支付失败: ' + error.errMsg)
        }
        
        // 可以查询订单状态
        if (orderId) {
          this.checkPaymentStatus(orderId)
        }
      }
    })
  },
  
  // 查询支付状态
  async checkPaymentStatus(orderId) {
    try {
      const res = await app.request({
        url: `/api/payment/status/${orderId}`
      })
      
      if (res.success && res.order) {
        console.log('📊 订单状态:', res.order)
        // 可以根据订单状态做进一步处理
      }
    } catch (error) {
      console.error('查询订单状态失败:', error)
    }
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
