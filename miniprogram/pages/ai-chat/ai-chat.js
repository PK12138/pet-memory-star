const app = getApp()

Page({
  data: {
    memorialId: '',
    petName: '',
    petAvatar: '',
    messages: [],
    inputMessage: '',
    scrollIntoView: '',
    loading: false,
    greeting: ''
  },

  onLoad(options) {
    console.log('AI对话页面加载', options)
    
    if (options.id) {
      this.setData({
        memorialId: options.id,
        petName: options.name || '宠物',
        petAvatar: options.avatar || ''
      })
      
      this.loadChatHistory()
      this.loadGreeting()
    } else {
      wx.showModal({
        title: '错误',
        content: '缺少纪念馆信息',
        showCancel: false,
        success: () => {
          wx.navigateBack()
        }
      })
    }
  },

  // 加载问候语
  async loadGreeting() {
    try {
      const res = await app.request({
        url: `/api/chat/${this.data.memorialId}/greeting`,
        method: 'GET'
      })
      
      if (res.success && res.greeting) {
        // 添加问候语作为第一条消息
        this.setData({
          greeting: res.greeting,
          messages: [{
            role: 'assistant',
            content: res.greeting,
            created_at: new Date().toISOString()
          }]
        })
        this.scrollToBottom()
      }
    } catch (error) {
      console.error('加载问候语失败:', error)
    }
  },

  // 加载对话历史
  async loadChatHistory() {
    try {
      const res = await app.request({
        url: `/api/chat/${this.data.memorialId}/history`,
        method: 'GET'
      })
      
      if (res.success && res.history) {
        // 如果有历史记录，显示历史；否则只显示问候语
        if (res.history.length > 0) {
          this.setData({
            messages: res.history
          })
          this.scrollToBottom()
        }
      }
    } catch (error) {
      console.error('加载对话历史失败:', error)
    }
  },

  // 输入框变化
  onInput(e) {
    this.setData({
      inputMessage: e.detail.value
    })
  },

  // 发送消息
  async sendMessage() {
    const message = this.data.inputMessage.trim()
    
    if (!message) {
      wx.showToast({
        title: '请输入消息',
        icon: 'none'
      })
      return
    }
    
    if (this.data.loading) {
      return
    }
    
    // 添加用户消息到界面
    const userMessage = {
      role: 'user',
      content: message,
      created_at: new Date().toISOString()
    }
    
    this.setData({
      messages: [...this.data.messages, userMessage],
      inputMessage: '',
      loading: true
    })
    
    this.scrollToBottom()
    
    try {
      // 调用API发送消息
      const res = await app.request({
        url: `/api/chat/${this.data.memorialId}`,
        method: 'POST',
        data: {
          message: message
        }
      })
      
      if (res.success && res.message) {
        // 添加AI回复
        const aiMessage = {
          role: 'assistant',
          content: res.message,
          created_at: res.timestamp || new Date().toISOString()
        }
        
        this.setData({
          messages: [...this.data.messages, aiMessage],
          loading: false
        })
        
        this.scrollToBottom()
      } else {
        throw new Error(res.message || 'AI回复失败')
      }
    } catch (error) {
      console.error('发送消息失败:', error)
      
      // 移除用户消息
      const messages = this.data.messages.slice(0, -1)
      this.setData({
        messages,
        loading: false,
        inputMessage: message  // 恢复输入
      })
      
      wx.showToast({
        title: error.message || '发送失败',
        icon: 'none'
      })
    }
  },

  // 滚动到底部
  scrollToBottom() {
    setTimeout(() => {
      this.setData({
        scrollIntoView: `msg-${this.data.messages.length - 1}`
      })
    }, 100)
  },

  // 清空对话历史
  clearHistory() {
    wx.showModal({
      title: '确认清空',
      content: '是否清空所有对话记录？',
      success: async (res) => {
        if (res.confirm) {
          try {
            const result = await app.request({
              url: `/api/chat/${this.data.memorialId}/history`,
              method: 'DELETE'
            })
            
            if (result.success) {
              // 重新加载问候语
              this.setData({
                messages: []
              })
              this.loadGreeting()
              
              wx.showToast({
                title: '已清空',
                icon: 'success'
              })
            } else {
              throw new Error(result.message)
            }
          } catch (error) {
            wx.showToast({
              title: '清空失败',
              icon: 'none'
            })
          }
        }
      }
    })
  },

  // 格式化时间
  formatTime(timestamp) {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now - date
    
    // 1分钟内
    if (diff < 60000) {
      return '刚刚'
    }
    
    // 1小时内
    if (diff < 3600000) {
      return `${Math.floor(diff / 60000)}分钟前`
    }
    
    // 今天
    if (date.toDateString() === now.toDateString()) {
      return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    }
    
    // 昨天
    const yesterday = new Date(now)
    yesterday.setDate(yesterday.getDate() - 1)
    if (date.toDateString() === yesterday.toDateString()) {
      return `昨天 ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    }
    
    // 其他
    return `${date.getMonth() + 1}月${date.getDate()}日`
  }
})

