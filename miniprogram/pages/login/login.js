// pages/login/login.js
const app = getApp()

Page({
  data: {
    loading: false,
    successMessage: '',
    errorMessage: ''
  },

  onLoad() {
    console.log('🚀 微信登录页加载')
    
    // 检查是否已登录
    const sessionToken = app.globalData.sessionToken
    if (sessionToken) {
      console.log('✅ 已登录，直接跳转首页')
      wx.reLaunch({
        url: '/pages/index/index'
      })
    }
  },

  // 微信登录
  async wxLogin() {
    console.log('🔑 开始微信登录流程')
    
    this.setData({
      loading: true,
      errorMessage: '',
      successMessage: ''
    })
    
    try {
      // 1. 调用 wx.login 获取 code
      const loginRes = await new Promise((resolve, reject) => {
        wx.login({
          success: resolve,
          fail: reject
        })
      })
      
      const code = loginRes.code
      console.log('📱 获取到微信code:', code)
      
      if (!code) {
        throw new Error('获取微信登录凭证失败')
      }
      
      // 2. 发送 code 到后端换取 session
      console.log('🌐 发送code到后端')
      const res = await app.request({
        url: '/api/auth/wx-login',
        method: 'POST',
        data: { code }
      })
      
      console.log('📥 后端响应:', res)
      
      if (res.success) {
        // 3. 保存 token 和用户信息
        console.log('✅ 登录成功')
        this.setData({
          successMessage: '登录成功！',
          loading: false
        })
        
        // 保存到全局
        app.login(res.session_token, res.user)
        
        // 短暂延迟后跳转
        setTimeout(() => {
          console.log('⏭️ 跳转到首页')
          wx.reLaunch({
            url: '/pages/index/index',
            success: () => {
              console.log('✅ 跳转成功')
            },
            fail: (err) => {
              console.error('❌ 跳转失败:', err)
            }
          })
        }, 800)
      } else {
        this.setData({
          loading: false,
          errorMessage: res.message || '登录失败，请重试'
        })
      }
    } catch (error) {
      console.error('❌ 微信登录失败:', error)
      this.setData({
        loading: false,
        errorMessage: error.message || '登录失败，请检查网络后重试'
      })
      
      // 显示错误提示
      wx.showToast({
        title: '登录失败',
        icon: 'none',
        duration: 2000
      })
    }
  },

  // 查看隐私政策
  viewPrivacy() {
    wx.showModal({
      title: '隐私政策',
      content: '我们承诺保护您的个人信息安全。您的微信信息仅用于登录验证，不会用于其他用途。',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 查看服务条款
  viewTerms() {
    wx.showModal({
      title: '服务条款',
      content: '使用本小程序即表示您同意遵守我们的服务条款。我们致力于为您提供优质的纪念服务。',
      showCancel: false,
      confirmText: '知道了'
    })
  },

  // 返回首页
  goToHome() {
    wx.reLaunch({
      url: '/pages/index/index'
    })
  }
})