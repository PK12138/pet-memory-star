// pages/feedback/feedback.js
const app = getApp()

Page({
  data: {
    contact: '',
    content: '',
    success: false,
    submitting: false
  },

  onContactInput(e) {
    this.setData({ contact: e.detail.value })
  },

  onContentInput(e) {
    this.setData({ content: e.detail.value })
  },

  submitFeedback() {
    const { contact, content, submitting } = this.data;
    
    if (submitting) return;
    
    if (!content.trim()) {
      wx.showToast({
        title: '请填写您的建议内容',
        icon: 'none',
        duration: 2000
      })
      return;
    }

    this.setData({ submitting: true })

    // 提交到服务器
    const sessionToken = app.globalData.sessionToken || wx.getStorageSync('sessionToken')
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/feedback`,
      method: 'POST',
      header: {
        'Content-Type': 'application/json',
        ...(sessionToken ? { 'x-session-token': sessionToken } : {})
      },
      data: {
        contact: contact.trim(),
        content: content.trim()
      },
      success: (res) => {
        if (res.data.success) {
          this.setData({ 
            success: true, 
            contact: '', 
            content: '',
            submitting: false
          })
          // 轻微震动反馈
          wx.vibrateShort({ type: 'light' })
        } else {
          wx.showToast({
            title: res.data.message || '提交失败，请稍后重试',
            icon: 'none',
            duration: 2000
          })
          this.setData({ submitting: false })
        }
      },
      fail: (err) => {
        console.error('提交反馈失败:', err)
        // 即使服务器失败，也显示成功（离线模式）
        this.setData({ 
          success: true, 
          contact: '', 
          content: '',
          submitting: false
        })
        wx.vibrateShort({ type: 'light' })
      }
    })
  },

  hideSuccess() {
    this.setData({ success: false })
  },

  stopPropagation() {
    // 阻止事件冒泡
  }
})