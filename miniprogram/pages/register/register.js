// pages/register/register.js
const app = getApp()

Page({
  data: {
    email: '',
    password: '',
    confirmPassword: '',
    loading: false,
    successMessage: '',
    errorMessage: '',
    emailError: '',
    passwordError: '',
    confirmPasswordError: ''
  },

  onLoad() {
    console.log('注册页加载')
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
      passwordError: '',
      confirmPasswordError: ''
    })
  },

  // 确认密码输入
  onConfirmPasswordInput(e) {
    this.setData({
      confirmPassword: e.detail.value,
      confirmPasswordError: ''
    })
  },

  // 清除错误信息
  clearErrors() {
    this.setData({
      emailError: '',
      passwordError: '',
      confirmPasswordError: '',
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

  // 注册
  async register() {
    const { email, password, confirmPassword } = this.data
    
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
    
    if (!confirmPassword) {
      this.showError('confirmPassword', '请确认密码')
      return
    }
    
    if (password !== confirmPassword) {
      this.showError('confirmPassword', '两次输入的密码不一致')
      return
    }
    
    this.setLoading(true)
    
    try {
      const res = await app.request({
        url: '/api/auth/register',
        method: 'POST',
        data: {
          email: email,
          password: password
        }
      })
      
      if (res.success) {
        // 注册成功
        this.showSuccess('注册成功！请检查邮箱验证邮件')
        
        // 延迟跳转到登录页
        setTimeout(() => {
          wx.navigateTo({
            url: '/pages/login/login'
          })
        }, 2000)
      } else {
        this.setLoading(false)
        this.showGlobalError(res.message || '注册失败，请稍后重试')
      }
    } catch (error) {
      console.error('注册失败:', error)
      this.setLoading(false)
      this.showGlobalError('网络错误，请稍后重试')
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
  },

  // 返回首页
  goToHome() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  }
})