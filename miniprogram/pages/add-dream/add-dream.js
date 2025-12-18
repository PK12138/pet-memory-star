// pages/add-dream/add-dream.js
const app = getApp()

Page({
  data: {
    memorialId: '',
    petName: '',
    dreamDate: '',
    dreamTime: '',
    dreamContent: '',
    emotionType: '',
    tags: [],
    tagInput: '',
    isPrivate: false,
    submitting: false,
    emotions: [
      { value: '温馨', label: '温馨', icon: '💕' },
      { value: '思念', label: '思念', icon: '💭' },
      { value: '快乐', label: '快乐', icon: '😊' },
      { value: '悲伤', label: '悲伤', icon: '😢' },
      { value: '平静', label: '平静', icon: '😌' },
      { value: '焦虑', label: '焦虑', icon: '😰' }
    ],
    suggestedTags: ['玩耍', '温暖', '重逢', '日常', '告别']
  },

  onLoad(options) {
    const today = new Date()
    const dateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
    
    this.setData({
      memorialId: options.memorialId || '',
      petName: decodeURIComponent(options.petName || '宠物'),
      dreamDate: dateStr
    })
  },

  onDateChange(e) {
    this.setData({ dreamDate: e.detail.value })
  },

  onTimeChange(e) {
    this.setData({ dreamTime: e.detail.value })
  },

  onContentInput(e) {
    this.setData({ dreamContent: e.detail.value })
  },

  selectEmotion(e) {
    this.setData({ emotionType: e.currentTarget.dataset.value })
  },

  onTagInput(e) {
    this.setData({ tagInput: e.detail.value })
  },

  addTag() {
    const tag = this.data.tagInput.trim()
    if (tag && !this.data.tags.includes(tag)) {
      this.setData({
        tags: [...this.data.tags, tag],
        tagInput: ''
      })
    }
  },

  addSuggestedTag(e) {
    const tag = e.currentTarget.dataset.tag
    if (!this.data.tags.includes(tag)) {
      this.setData({
        tags: [...this.data.tags, tag]
      })
    }
  },

  removeTag(e) {
    const index = e.currentTarget.dataset.index
    const tags = [...this.data.tags]
    tags.splice(index, 1)
    this.setData({ tags })
  },

  onPrivateChange(e) {
    this.setData({ isPrivate: e.detail.value })
  },

  submitDream() {
    const { memorialId, dreamDate, dreamContent, emotionType, tags, dreamTime, isPrivate } = this.data

    if (!dreamContent.trim()) {
      wx.showToast({ title: '请填写梦境内容', icon: 'none' })
      return
    }

    this.setData({ submitting: true })

    wx.request({
      url: `${app.globalData.apiUrl}/api/dreams/${memorialId}`,
      method: 'POST',
      header: {
        'x-session-token': wx.getStorageSync('session_token')
      },
      data: {
        dream_date: dreamDate,
        dream_time: dreamTime,
        dream_content: dreamContent,
        emotion_type: emotionType || undefined,
        tags: tags,
        is_private: isPrivate
      },
      success: (res) => {
        console.log('创建梦境日记:', res.data)
        if (res.data.success) {
          wx.showToast({
            title: '保存成功',
            icon: 'success',
            duration: 2000
          })
          setTimeout(() => {
            wx.navigateBack()
          }, 2000)
        } else {
          wx.showToast({
            title: res.data.message || '保存失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        console.error('创建梦境失败:', err)
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        })
      },
      complete: () => {
        this.setData({ submitting: false })
      }
    })
  },

  goBack() {
    wx.navigateBack()
  }
})

