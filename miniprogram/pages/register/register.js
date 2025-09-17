// pages/register/register.js
const app = getApp()

Page({
  data: {
    email: '',
    password: '',
    confirmPassword: '',
    loading: false
  },

  onLoad() {
    console.log('注册页加载')
  },

  // 邮箱输入
  onEmailInput(e) {
    this.setData({
      email: e.detail.value
    })
  },

  // 密码输入
  onPasswordInput(e) {
    this.setData({
      password: e.detail.value
    })
  },

  // 确认密码输入
  onConfirmPasswordInput(e) {
    this.setData({
      confirmPassword: e.detail.value
    })
  },

  // 注册
  async register() {
    const { email, password, confirmPassword } = this.data
    
    // 验证输入
    if (!email) {
      app.showError('请输入邮箱地址')
      return
    }
    
    if (!password) {
      app.showError('请输入密码')
      return
    }
    
    if (!confirmPassword) {
      app.showError('请确认密码')
      return
    }
    
    if (password !== confirmPassword) {
      app.showError('两次输入的密码不一致')
      return
    }
    
    if (!this.validateEmail(email)) {
      app.showError('请输入有效的邮箱地址')
      return
    }
    
    this.setData({ loading: true })
    app.showLoading('注册中...')
    
    try {
      const res = await app.request({
        url: '/api/auth/register',
        method: 'POST',
        data: {
          email: email,
          password: password,
          confirm_password: confirmPassword
        }
      })
      
      if (res.success) {
        // 注册成功
        app.hideLoading()
        app.showSuccess('注册成功')
        
        // 跳转到登录页
        setTimeout(() => {
          wx.navigateTo({
            url: '/pages/login/login'
          })
        }, 1500)
      } else {
        app.hideLoading()
        app.showError(res.message || '注册失败')
      }
    } catch (error) {
      console.error('注册失败:', error)
      app.hideLoading()
      app.showError('网络错误，请稍后重试')
    } finally {
      this.setData({ loading: false })
    }
  },

  // 验证邮箱格式
  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  },

  // 跳转到登录页
  goToLogin() {
    wx.navigateTo({
      url: '/pages/login/login'
    })
  }
})
