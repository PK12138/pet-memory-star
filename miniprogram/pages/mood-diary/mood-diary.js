// pages/mood-diary/mood-diary.js
const app = getApp()

Page({
  data: {
    memorialId: null,
    diaries: [],
    showAddDialog: false,
    moodTypes: [
      { value: 'happy', name: '开心', emoji: '😊' },
      { value: 'sad', name: '伤心', emoji: '😢' },
      { value: 'calm', name: '平静', emoji: '😌' },
      { value: 'excited', name: '兴奋', emoji: '🤗' },
      { value: 'lonely', name: '孤独', emoji: '😔' },
      { value: 'grateful', name: '感恩', emoji: '🙏' }
    ],
    weatherTypes: [
      { value: 'sunny', name: '晴天', emoji: '☀️' },
      { value: 'cloudy', name: '多云', emoji: '⛅' },
      { value: 'rainy', name: '雨天', emoji: '🌧️' },
      { value: 'snowy', name: '雪天', emoji: '❄️' }
    ],
    formData: {
      moodType: '',
      moodScore: 5,
      weather: '',
      content: ''
    }
  },

  onLoad(options) {
    console.log('心情日记页加载', options)
    const { id } = options
    if (id) {
      this.setData({
        memorialId: id
      })
      this.loadDiaries()
    } else {
      wx.showToast({
        title: '参数错误',
        icon: 'none'
      })
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    }
  },

  onShow() {
    console.log('心情日记页显示')
  },

  // 加载日记列表
  async loadDiaries() {
    try {
      wx.showLoading({ title: '加载中...' })
      
      const res = await app.request({
        url: `/api/mood-diaries/${this.data.memorialId}`
      })

      wx.hideLoading()

      if (res.success) {
        this.setData({
          diaries: res.diaries || []
        })
        console.log('日记列表加载成功:', res.diaries)
      } else {
        throw new Error(res.error || '加载失败')
      }
    } catch (error) {
      wx.hideLoading()
      console.error('加载日记列表失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  // 显示添加对话框
  showAddDiary() {
    this.setData({
      showAddDialog: true,
      formData: {
        moodType: '',
        moodScore: 5,
        weather: '',
        content: ''
      }
    })
  },

  // 隐藏添加对话框
  hideAddDialog() {
    this.setData({
      showAddDialog: false
    })
  },

  // 选择心情类型
  selectMoodType(e) {
    const type = e.currentTarget.dataset.type
    this.setData({
      'formData.moodType': type
    })
    console.log('选择心情类型:', type)
  },

  // 选择天气
  selectWeather(e) {
    const weather = e.currentTarget.dataset.weather
    this.setData({
      'formData.weather': weather
    })
    console.log('选择天气:', weather)
  },

  // 心情评分改变
  onScoreChange(e) {
    this.setData({
      'formData.moodScore': e.detail.value
    })
    console.log('心情评分:', e.detail.value)
  },

  // 日记内容输入
  onContentInput(e) {
    this.setData({
      'formData.content': e.detail.value
    })
  },

  // 提交日记
  async submitDiary() {
    const { formData, memorialId } = this.data

    // 验证表单
    if (!formData.moodType) {
      wx.showToast({
        title: '请选择心情类型',
        icon: 'none'
      })
      return
    }

    if (!formData.content || !formData.content.trim()) {
      wx.showToast({
        title: '请输入日记内容',
        icon: 'none'
      })
      return
    }

    try {
      wx.showLoading({ title: '保存中...' })

      const requestData = {
        memorial_id: memorialId,
        mood_type: formData.moodType,
        mood_score: formData.moodScore,
        diary_content: formData.content.trim(),
        weather: formData.weather || ''
      }

      const res = await app.request({
        url: '/api/mood-diary',
        method: 'POST',
        data: requestData
      })

      wx.hideLoading()

      if (res.success) {
        wx.showToast({
          title: '记录成功',
          icon: 'success'
        })
        this.hideAddDialog()
        this.loadDiaries()
      } else {
        throw new Error(res.error || '保存失败')
      }
    } catch (error) {
      wx.hideLoading()
      console.error('保存日记失败:', error)
      wx.showToast({
        title: error.message || '保存失败',
        icon: 'none'
      })
    }
  },

  // 获取心情emoji
  getMoodEmoji(type) {
    const mood = this.data.moodTypes.find(m => m.value === type)
    return mood ? mood.emoji : '😊'
  },

  // 获取天气emoji
  getWeatherEmoji(weather) {
    const w = this.data.weatherTypes.find(wt => wt.value === weather)
    return w ? w.emoji : ''
  },

  // 格式化日期
  formatDate(dateStr) {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hour = String(date.getHours()).padStart(2, '0')
    const minute = String(date.getMinutes()).padStart(2, '0')
    return `${year}年${month}月${day}日 ${hour}:${minute}`
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadDiaries().then(() => {
      wx.stopPullDownRefresh()
    })
  }
})
