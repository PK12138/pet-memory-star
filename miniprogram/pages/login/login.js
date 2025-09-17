// pages/login/login.js
const app = getApp()

Page({
  data: {
    email: '',
    password: '',
    loading: false
  },

  onLoad() {
    console.log('登录页加载')
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

  // 登录
  async login() {
    const { email, password } = this.data
    
    // 验证输入
    if (!email) {
      app.showError('请输入邮箱地址')
      return
    }
    
    if (!password) {
      app.showError('请输入密码')
      return
    }
    
    if (!this.validateEmail(email)) {
      app.showError('请输入有效的邮箱地址')
      return
    }
    
    this.setData({ loading: true })
    app.showLoading('登录中...')
    
    try {
      const res = await app.request({
        url: '/api/auth/login',
        method: 'POST',
        data: {
          email: email,
          password: password
        }
      })
      
      if (res.success) {
        // 登录成功
        app.login(res.session_token, res.user_info)
        
        app.hideLoading()
        app.showSuccess('登录成功')
        
        // 跳转到首页
        setTimeout(() => {
          wx.switchTab({
            url: '/pages/index/index'
          })
        }, 1500)
      } else {
        app.hideLoading()
        app.showError(res.message || '登录失败')
      }
    } catch (error) {
      console.error('登录失败:', error)
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

  // 跳转到注册页
  goToRegister() {
    wx.navigateTo({
      url: '/pages/register/register'
    })
  },

  // 跳转到忘记密码页
  goToForgotPassword() {
    wx.navigateTo({
      url: '/pages/forgot-password/forgot-password'
    })
  }
})
