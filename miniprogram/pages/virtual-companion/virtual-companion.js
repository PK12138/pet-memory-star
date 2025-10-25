const app = getApp()

Page({
  data: {
    memorialId: '',
    petName: '',
    petAvatar: '',
    
    // 宠物状态
    petState: {
      mood: 70,
      energy: 60,
      intimacy: 0
    },
    
    // 问候消息
    greetings: [],
    loadingGreetings: true,
    
    // 互动统计
    stats: {
      feed: 0,
      play: 0,
      walk: 0,
      pet: 0
    },
    
    // 情绪曲线数据
    emotionData: {
      dates: [],
      scores: []
    },
    
    // 加载状态
    loading: true,
    interacting: false
  },

  onLoad(options) {
    console.log('虚拟陪伴页加载', options)
    
    if (options.memorialId) {
      this.setData({
        memorialId: options.memorialId,
        petName: decodeURIComponent(options.petName || '宠物'),
        petAvatar: options.petAvatar ? decodeURIComponent(options.petAvatar) : ''
      })
      
      this.loadCompanionStatus()
      this.loadGreetings()
      this.loadEmotionCurve()
    }
  },

  // 加载陪伴状态
  async loadCompanionStatus() {
    const token = wx.getStorageSync('session_token')
    if (!token) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      return
    }

    try {
      const res = await wx.request({
        url: `${app.globalData.baseUrl}/api/companion/${this.data.memorialId}/status`,
        header: {
          'x-session-token': token
        }
      })

      console.log('加载陪伴状态:', res.data)

      if (res.data.success) {
        this.setData({
          petState: res.data.pet_state || this.data.petState,
          stats: res.data.interaction_stats || this.data.stats,
          loading: false
        })
      }
    } catch (error) {
      console.error('加载陪伴状态失败:', error)
      this.setData({ loading: false })
    }
  },

  // 加载问候消息
  async loadGreetings() {
    const token = wx.getStorageSync('session_token')
    if (!token) return

    try {
      const res = await wx.request({
        url: `${app.globalData.baseUrl}/api/companion/${this.data.memorialId}/recent-greetings?limit=5`,
        header: {
          'x-session-token': token
        }
      })

      console.log('加载问候消息:', res.data)

      if (res.data.success) {
        this.setData({
          greetings: res.data.greetings || [],
          loadingGreetings: false
        })
      }
    } catch (error) {
      console.error('加载问候消息失败:', error)
      this.setData({ loadingGreetings: false })
    }
  },

  // 加载情绪曲线
  async loadEmotionCurve() {
    const token = wx.getStorageSync('session_token')
    if (!token) return

    try {
      const res = await wx.request({
        url: `${app.globalData.baseUrl}/api/companion/${this.data.memorialId}/emotion-curve?days=7`,
        header: {
          'x-session-token': token
        }
      })

      console.log('加载情绪曲线:', res.data)

      if (res.data.success && res.data.curve_data) {
        const dates = res.data.curve_data.map(d => d.date.slice(5)) // 月-日
        const scores = res.data.curve_data.map(d => d.score)
        
        this.setData({
          'emotionData.dates': dates,
          'emotionData.scores': scores
        })
      }
    } catch (error) {
      console.error('加载情绪曲线失败:', error)
    }
  },

  // 互动游戏
  async playGame(e) {
    const gameType = e.currentTarget.dataset.type
    
    if (this.data.interacting) {
      return
    }

    this.setData({ interacting: true })

    const token = wx.getStorageSync('session_token')
    if (!token) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      this.setData({ interacting: false })
      return
    }

    try {
      const res = await wx.request({
        url: `${app.globalData.baseUrl}/api/companion/${this.data.memorialId}/interact`,
        method: 'POST',
        header: {
          'Content-Type': 'application/json',
          'x-session-token': token
        },
        data: {
          game_type: gameType
        }
      })

      console.log('互动结果:', res.data)

      if (res.data.success) {
        wx.showToast({
          title: res.data.message,
          icon: 'none',
          duration: 2000
        })
        
        // 更新宠物状态
        this.setData({
          petState: res.data.pet_state
        })
        
        // 重新加载统计
        setTimeout(() => {
          this.loadCompanionStatus()
        }, 1000)
      } else {
        wx.showToast({
          title: res.data.message || '互动失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('互动失败:', error)
      wx.showToast({
        title: '互动失败，请稍后重试',
        icon: 'none'
      })
    } finally {
      setTimeout(() => {
        this.setData({ interacting: false })
      }, 1000)
    }
  },

  // 获取新问候
  async getNewGreeting() {
    const token = wx.getStorageSync('session_token')
    if (!token) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      return
    }

    wx.showLoading({ title: '生成中...' })

    // 根据时间决定问候类型
    const hour = new Date().getHours()
    let greetingType = 'random'
    if (hour >= 6 && hour < 12) {
      greetingType = 'morning'
    } else if (hour >= 20 || hour < 6) {
      greetingType = 'evening'
    }

    try {
      const res = await wx.request({
        url: `${app.globalData.baseUrl}/api/companion/${this.data.memorialId}/greeting?greeting_type=${greetingType}`,
        header: {
          'x-session-token': token
        }
      })

      wx.hideLoading()

      console.log('获取新问候:', res.data)

      if (res.data.success) {
        wx.showModal({
          title: '来自' + this.data.petName + '的问候',
          content: res.data.message,
          showCancel: false,
          confirmText: '收到了❤️'
        })
        
        // 重新加载问候列表
        this.loadGreetings()
      } else {
        wx.showToast({
          title: res.data.message || '获取失败',
          icon: 'none'
        })
      }
    } catch (error) {
      wx.hideLoading()
      console.error('获取新问候失败:', error)
      wx.showToast({
        title: '获取失败，请稍后重试',
        icon: 'none'
      })
    }
  },

  // 格式化时间
  formatTime(dateStr) {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now - date
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return '刚刚'
    if (minutes < 60) return `${minutes}分钟前`
    if (hours < 24) return `${hours}小时前`
    if (days < 7) return `${days}天前`

    const m = date.getMonth() + 1
    const d = date.getDate()
    return `${m}月${d}日`
  },

  // 返回纪念馆
  goBack() {
    wx.navigateBack()
  }
})

