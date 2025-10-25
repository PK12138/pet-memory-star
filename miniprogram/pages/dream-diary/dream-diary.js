// pages/dream-diary/dream-diary.js
const app = getApp()

Page({
  data: {
    memorialId: '',
    petName: '',
    activeTab: 'list',
    dreams: [],
    stats: {},
    loading: false,
    refreshing: false,
    
    // 月历相关
    currentYear: new Date().getFullYear(),
    currentMonth: new Date().getMonth() + 1,
    calendarDays: [],
    calendarData: {},
    
    // 统计相关
    emotionStats: [],
    avgFrequency: 0,
    maxGap: 0
  },

  onLoad(options) {
    console.log('梦境日记页面参数:', options)
    
    this.setData({
      memorialId: options.memorialId || '',
      petName: decodeURIComponent(options.petName || '宠物')
    })
    
    // 加载数据
    this.loadData()
  },

  // 加载所有数据
  loadData() {
    this.loadDreams()
    this.loadStats()
    if (this.data.activeTab === 'calendar') {
      this.loadCalendar()
    }
  },

  // 加载梦境列表
  loadDreams() {
    this.setData({ loading: true })
    
    wx.request({
      url: `${app.globalData.apiUrl}/api/dreams/${this.data.memorialId}`,
      header: {
        'x-session-token': wx.getStorageSync('session_token')
      },
      success: (res) => {
        console.log('获取梦境列表:', res.data)
        if (res.data.success) {
          this.setData({
            dreams: res.data.dreams
          })
        } else {
          wx.showToast({
            title: res.data.message || '加载失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        console.error('获取梦境列表失败:', err)
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        })
      },
      complete: () => {
        this.setData({ 
          loading: false,
          refreshing: false 
        })
      }
    })
  },

  // 加载统计数据
  loadStats() {
    wx.request({
      url: `${app.globalData.apiUrl}/api/dreams/${this.data.memorialId}/stats`,
      header: {
        'x-session-token': wx.getStorageSync('session_token')
      },
      success: (res) => {
        console.log('获取梦境统计:', res.data)
        if (res.data.success) {
          this.setData({
            stats: res.data.stats
          })
          
          // 处理情感统计数据
          this.processEmotionStats(res.data.stats.emotions)
        }
      },
      fail: (err) => {
        console.error('获取统计失败:', err)
      }
    })
  },

  // 处理情感统计数据
  processEmotionStats(emotions) {
    const emotionIcons = {
      '温馨': '💕',
      '思念': '💭',
      '快乐': '😊',
      '悲伤': '😢',
      '平静': '😌',
      '焦虑': '😰'
    }
    
    const total = Object.values(emotions).reduce((sum, count) => sum + count, 0)
    
    const emotionStats = Object.entries(emotions).map(([emotion, count]) => ({
      emotion,
      icon: emotionIcons[emotion] || '💫',
      count,
      percentage: total > 0 ? (count / total * 100).toFixed(1) : 0
    })).sort((a, b) => b.count - a.count)
    
    this.setData({ emotionStats })
  },

  // 加载月历数据
  loadCalendar() {
    const { currentYear, currentMonth, memorialId } = this.data
    
    wx.request({
      url: `${app.globalData.apiUrl}/api/dreams/${memorialId}/calendar`,
      data: {
        year: currentYear,
        month: currentMonth
      },
      header: {
        'x-session-token': wx.getStorageSync('session_token')
      },
      success: (res) => {
        console.log('获取月历数据:', res.data)
        if (res.data.success) {
          this.setData({
            calendarData: res.data.calendar
          })
          this.generateCalendar()
        }
      },
      fail: (err) => {
        console.error('获取月历失败:', err)
      }
    })
  },

  // 生成月历
  generateCalendar() {
    const { currentYear, currentMonth, calendarData } = this.data
    
    // 获取当月第一天是星期几
    const firstDay = new Date(currentYear, currentMonth - 1, 1).getDay()
    
    // 获取当月天数
    const daysInMonth = new Date(currentYear, currentMonth, 0).getDate()
    
    // 获取上个月天数
    const prevMonthDays = new Date(currentYear, currentMonth - 1, 0).getDate()
    
    const calendarDays = []
    const today = new Date()
    const isCurrentMonth = today.getFullYear() === currentYear && (today.getMonth() + 1) === currentMonth
    const todayDate = today.getDate()
    
    // 填充上个月的日期
    for (let i = firstDay - 1; i >= 0; i--) {
      calendarDays.push({
        day: prevMonthDays - i,
        isOtherMonth: true,
        hasDream: false,
        isToday: false
      })
    }
    
    // 填充当月的日期
    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${currentYear}-${String(currentMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`
      calendarDays.push({
        day,
        isOtherMonth: false,
        hasDream: !!calendarData[dateStr],
        isToday: isCurrentMonth && day === todayDate
      })
    }
    
    // 填充下个月的日期，补齐6行
    const remainingDays = 42 - calendarDays.length
    for (let day = 1; day <= remainingDays; day++) {
      calendarDays.push({
        day,
        isOtherMonth: true,
        hasDream: false,
        isToday: false
      })
    }
    
    this.setData({ calendarDays })
  },

  // 切换Tab
  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({ activeTab: tab })
    
    if (tab === 'calendar' && this.data.calendarDays.length === 0) {
      this.loadCalendar()
    }
  },

  // 下拉刷新
  onRefresh() {
    this.setData({ refreshing: true })
    this.loadData()
  },

  // 查看详情
  viewDetail(e) {
    const dreamId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/dream-detail/dream-detail?dreamId=${dreamId}&memorialId=${this.data.memorialId}&petName=${encodeURIComponent(this.data.petName)}`
    })
  },

  // 新增梦境
  addDream() {
    wx.navigateTo({
      url: `/pages/add-dream/add-dream?memorialId=${this.data.memorialId}&petName=${encodeURIComponent(this.data.petName)}`
    })
  },

  // 切换收藏
  toggleFavorite(e) {
    const dreamId = e.currentTarget.dataset.id
    const isFavorite = e.currentTarget.dataset.favorite
    
    wx.request({
      url: `${app.globalData.apiUrl}/api/dreams/${this.data.memorialId}/${dreamId}/favorite`,
      method: 'POST',
      header: {
        'x-session-token': wx.getStorageSync('session_token')
      },
      data: {
        is_favorite: !isFavorite
      },
      success: (res) => {
        if (res.data.success) {
          // 更新本地数据
          const dreams = this.data.dreams.map(dream => {
            if (dream.id === dreamId) {
              return { ...dream, is_favorite: !isFavorite }
            }
            return dream
          })
          
          this.setData({ dreams })
          
          wx.showToast({
            title: res.data.is_favorite ? '已收藏' : '已取消收藏',
            icon: 'success'
          })
          
          // 刷新统计数据
          this.loadStats()
        }
      },
      fail: (err) => {
        console.error('切换收藏失败:', err)
        wx.showToast({
          title: '操作失败',
          icon: 'none'
        })
      }
    })
  },

  // 上一个月
  prevMonth() {
    let { currentYear, currentMonth } = this.data
    currentMonth--
    if (currentMonth < 1) {
      currentMonth = 12
      currentYear--
    }
    this.setData({ currentYear, currentMonth })
    this.loadCalendar()
  },

  // 下一个月
  nextMonth() {
    let { currentYear, currentMonth } = this.data
    currentMonth++
    if (currentMonth > 12) {
      currentMonth = 1
      currentYear++
    }
    this.setData({ currentYear, currentMonth })
    this.loadCalendar()
  },

  // 获取情感图标
  getEmotionIcon(emotion) {
    const icons = {
      '温馨': '💕',
      '思念': '💭',
      '快乐': '😊',
      '悲伤': '😢',
      '平静': '😌',
      '焦虑': '😰'
    }
    return icons[emotion] || '💫'
  },

  onShow() {
    // 从其他页面返回时刷新数据
    if (this.data.memorialId) {
      this.loadData()
    }
  }
})

