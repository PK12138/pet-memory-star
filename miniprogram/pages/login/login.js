// pages/login/login.js
const app = getApp()

Page({
  data: {
    email: '',
    password: '',
    loading: false,
    successMessage: '',
    errorMessage: '',
    emailError: '',
    passwordError: ''
  },

  onLoad() {
    console.log('登录页加载')
  },

  // 邮箱输入
  onEmailInput(e) {
    this.setData({
      email: e.detail.value,
      emailError: ''
    })
  },

  // 密码输入
  onPasswordInput(e) {
    this.setData({
      password: e.detail.value,
      passwordError: ''
    })
  },

  // 清除错误信息
  clearErrors() {
    this.setData({
      emailError: '',
      passwordError: '',
      errorMessage: '',
      successMessage: ''
    })
  },

  // 显示错误信息
  showError(field, message) {
    const errorField = field + 'Error'
    this.setData({
      [errorField]: message
    })
  },

  // 显示全局错误信息
  showGlobalError(message) {
    this.setData({
      errorMessage: message
    })
  },

  // 显示成功信息
  showSuccess(message) {
    this.setData({
      successMessage: message
    })
  },

  // 设置加载状态
  setLoading(isLoading) {
    this.setData({
      loading: isLoading
    })
  },

  // 登录
  async login() {
    const { email, password } = this.data
    
    // 清除之前的错误信息
    this.clearErrors()
    
    // 验证输入
    if (!email) {
      this.showError('email', '请输入邮箱地址')
      return
    }
    
    if (!this.validateEmail(email)) {
      this.showError('email', '请输入有效的邮箱地址')
      return
    }
    
    if (!password) {
      this.showError('password', '请输入密码')
      return
    }
    
    if (password.length < 6) {
      this.showError('password', '密码长度不能少于6位')
      return
    }
    
    this.setLoading(true)
    
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
        this.showSuccess('登录成功！')
        
        // 保存用户信息到全局
        app.globalData.userInfo = res.user
        app.globalData.sessionToken = res.session_token
        app.globalData.userLevel = res.user_level || 0
        
        // 延迟跳转
        setTimeout(() => {
          wx.switchTab({
            url: '/pages/index/index'
          })
        }, 1500)
      } else {
        this.setLoading(false)
        this.showGlobalError(res.message || '登录失败，请检查邮箱和密码')
      }
    } catch (error) {
      console.error('登录失败:', error)
      this.setLoading(false)
      this.showGlobalError('网络错误，请稍后重试')
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
  },

  // 返回首页
  goToHome() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  }
})