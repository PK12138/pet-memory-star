// pages/forgot-password/forgot-password.js
const app = getApp()

Page({
  data: {
    step: 1, // 1: 输入邮箱, 2: 输入验证码和新密码
    email: '',
    code: '',
    newPassword: '',
    confirmPassword: '',
    sending: false,
    resetting: false,
    countdown: 0,
    timer: null
  },

  onLoad(options) {
    console.log('忘记密码页面加载')
  },

  onUnload() {
    // 清除倒计时
    if (this.data.timer) {
      clearInterval(this.data.timer)
    }
  },

  // 邮箱输入
  onEmailInput(e) {
    this.setData({
      email: e.detail.value.trim()
    })
  },

  // 验证码输入
  onCodeInput(e) {
    this.setData({
      code: e.detail.value.trim()
    })
    this.checkCanReset()
  },

  // 新密码输入
  onPasswordInput(e) {
    this.setData({
      newPassword: e.detail.value
    })
    this.checkCanReset()
  },

  // 确认密码输入
  onConfirmPasswordInput(e) {
    this.setData({
      confirmPassword: e.detail.value
    })
    this.checkCanReset()
  },

  // 检查是否可以重置密码
  checkCanReset() {
    const { code, newPassword, confirmPassword } = this.data
    const canReset = code.length === 6 && 
                     newPassword.length >= 6 && 
                     confirmPassword.length >= 6 &&
                     newPassword === confirmPassword
    this.setData({ canReset })
  },

  // 发送验证码
  async sendCode() {
    const { email } = this.data

    if (!email) {
      wx.showToast({
        title: '请输入邮箱',
        icon: 'none'
      })
      return
    }

    // 验证邮箱格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      wx.showToast({
        title: '邮箱格式不正确',
        icon: 'none'
      })
      return
    }

    this.setData({ sending: true })

    try {
      const res = await app.request({
        url: '/api/auth/send-verification-code',
        method: 'POST',
        data: { email }
      })

      if (res.success) {
        wx.showToast({
          title: '验证码已发送',
          icon: 'success'
        })

        // 切换到步骤2
        this.setData({
          step: 2,
          countdown: 60
        })

        // 开始倒计时
        this.startCountdown()
      } else {
        wx.showToast({
          title: res.message || '发送失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('发送验证码失败:', error)
      wx.showToast({
        title: error.message || '发送失败',
        icon: 'none'
      })
    } finally {
      this.setData({ sending: false })
    }
  },

  // 重新发送验证码
  async resendCode() {
    await this.sendCode()
  },

  // 开始倒计时
  startCountdown() {
    const timer = setInterval(() => {
      const { countdown } = this.data
      if (countdown <= 1) {
        clearInterval(timer)
        this.setData({
          countdown: 0,
          timer: null
        })
      } else {
        this.setData({
          countdown: countdown - 1
        })
      }
    }, 1000)

    this.setData({ timer })
  },

  // 重置密码
  async resetPassword() {
    const { email, code, newPassword, confirmPassword } = this.data

    if (!code || code.length !== 6) {
      wx.showToast({
        title: '请输入6位验证码',
        icon: 'none'
      })
      return
    }

    if (!newPassword || newPassword.length < 6) {
      wx.showToast({
        title: '密码至少6位',
        icon: 'none'
      })
      return
    }

    if (newPassword !== confirmPassword) {
      wx.showToast({
        title: '两次密码不一致',
        icon: 'none'
      })
      return
    }

    this.setData({ resetting: true })

    try {
      const res = await app.request({
        url: '/api/auth/reset-password',
        method: 'POST',
        data: {
          email,
          verification_code: code,
          new_password: newPassword
        }
      })

      if (res.success) {
        wx.showToast({
          title: '密码重置成功',
          icon: 'success'
        })

        // 延迟跳转到登录页
        setTimeout(() => {
          wx.redirectTo({
            url: '/pages/login/login'
          })
        }, 1500)
      } else {
        wx.showToast({
          title: res.message || '重置失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('重置密码失败:', error)
      wx.showToast({
        title: error.message || '重置失败',
        icon: 'none'
      })
    } finally {
      this.setData({ resetting: false })
    }
  },

  // 返回步骤1
  backToStep1() {
    this.setData({
      step: 1,
      code: '',
      newPassword: '',
      confirmPassword: '',
      canReset: false
    })

    // 清除倒计时
    if (this.data.timer) {
      clearInterval(this.data.timer)
      this.setData({
        countdown: 0,
        timer: null
      })
    }
  },

  // 返回登录
  backToLogin() {
    wx.navigateBack({
      delta: 1
    })
  }
})

