// pages/memorial-detail/memorial-detail.js
const app = getApp()

Page({
  data: {
    memorialId: null,
    memorialInfo: {},
    messages: [],
    isSelf: false,  // 新增：是否自己的纪念馆
    newMessage: {
      name: '',
      content: ''
    },
    submitting: false,
    visitStats: {
      total_visits: 0,
      unique_visitors: 0,
      last_visit: null
    }
  },

  onLoad(options) {
    console.log('纪念馆详情页加载', options)
    const { id } = options
    if (id) {
      this.setData({
        memorialId: id
      })
      this.loadMemorialDetail()
      this.loadMessages()
      this.recordVisit()
      this.loadVisitStats()
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

  // 加载纪念馆详情
  async loadMemorialDetail() {
    wx.showLoading({
      title: '加载中...'
    })

    try {
      const res = await app.request({
        url: `/api/memorial/get/${this.data.memorialId}`
      })

      if (res.success) {
        const memorial = res.memorial || {}
        
        // 将照片相对路径转换为完整URL
        if (memorial.photos && Array.isArray(memorial.photos)) {
          memorial.photos = memorial.photos.map(photo => {
            // 如果是相对路径，拼接完整URL
            if (photo && photo.startsWith('/')) {
              return `${app.globalData.baseUrl}${photo}`
            }
            return photo
          })
        }
        
        // 判断是否属于本人
        let isSelf = false;
        const user = app.globalData.userInfo;
        if (user && memorial.user_id && (user.id === memorial.user_id || user.user_id === memorial.user_id)) {
          isSelf = true;
        }
        
        // 确保pet_status字段存在（兼容旧数据）
        if (!memorial.pet_status && memorial.pet_info) {
          const petStatus = memorial.pet_info.status || 'alive'
          memorial.pet_status = petStatus === '已逝世' ? 'passed' : (petStatus === '健在' ? 'alive' : petStatus)
        }
        
        // 如果没有AI信件但有预览，确保显示
        if (!memorial.ai_letter && memorial.ai_letter_preview && memorial.pet_status === 'passed') {
          memorial.ai_letter_locked = true
        }
        
        this.setData({
          memorialInfo: memorial,
          isSelf: isSelf
        })
        
        console.log('纪念馆详情加载完成:', {
          has_ai_letter: !!memorial.ai_letter,
          has_preview: !!memorial.ai_letter_preview,
          pet_status: memorial.pet_status,
          ai_letter_locked: memorial.ai_letter_locked
        })
      } else {
        wx.showToast({
          title: res.message || '加载失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('加载纪念馆详情失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 预览照片
  previewPhoto(e) {
    const url = e.currentTarget.dataset.url
    const photos = this.data.memorialInfo.photos || []
    wx.previewImage({
      current: url,
      urls: photos
    })
  },

  // 编辑纪念馆
  editMemorial() {
    wx.navigateTo({
      url: `/pages/memorial-edit/memorial-edit?id=${this.data.memorialId}`
    })
  },

  // 跳转到提醒设置
  goToReminderSetup() {
    wx.navigateTo({
      url: `/pages/reminder-setup/reminder-setup?id=${this.data.memorialId}`
    })
  },

  // 跳转到心情日记
  goToMoodDiary() {
    wx.navigateTo({
      url: `/pages/mood-diary/mood-diary?id=${this.data.memorialId}`
    })
  },

  // 跳转到虚拟陪伴页面
  goToVirtualCompanion() {
    const { memorialId, memorialInfo } = this.data
    const petName = memorialInfo.pet_name || '宠物'
    const petAvatar = memorialInfo.photos && memorialInfo.photos.length > 0
      ? encodeURIComponent(memorialInfo.photos[0])
      : ''
    
    wx.navigateTo({
      url: `/pages/virtual-companion/virtual-companion?memorialId=${memorialId}&petName=${encodeURIComponent(petName)}&petAvatar=${petAvatar}`
    })
  },

  // 跳转到梦境日记
  goToDreamDiary() {
    const { memorialId, memorialInfo } = this.data
    const petName = memorialInfo.pet_name || '宠物'
    
    wx.navigateTo({
      url: `/pages/dream-diary/dream-diary?memorialId=${memorialId}&petName=${encodeURIComponent(petName)}`
    })
  },

  // 跳转到AI对话页面
  goToAIChat() {
    const { memorialId, memorialInfo } = this.data
    const petName = memorialInfo.pet_name || '宠物'
    const petAvatar = memorialInfo.photos && memorialInfo.photos.length > 0 
      ? memorialInfo.photos[0] 
      : ''
    
    wx.navigateTo({
      url: `/pages/ai-chat/ai-chat?id=${memorialId}&name=${encodeURIComponent(petName)}&avatar=${encodeURIComponent(petAvatar)}`
    })
  },

  // 分享纪念馆
  shareMemorial() {
    wx.showActionSheet({
      itemList: ['分享给朋友', '分享到朋友圈', '复制链接'],
      success: (res) => {
        switch (res.tapIndex) {
          case 0:
            this.shareToFriend()
            break
          case 1:
            this.shareToMoments()
            break
          case 2:
            this.copyLink()
            break
        }
      }
    })
  },

  // 分享给朋友
  shareToFriend() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })
  },

  // 分享到朋友圈
  shareToMoments() {
    wx.showModal({
      title: '分享到朋友圈',
      content: '请使用右上角分享',
      showCancel: false,
      success: () => {
        // 分享后调用奖励API
        this.claimShareReward()
      }
    })
  },
  
  // 领取朋友圈分享奖励
  async claimShareReward() {
    try {
      const res = await app.request({
        url: '/api/coins/share-moments',
        method: 'POST'
      })
      
      if (res.success) {
        wx.showToast({
          title: `获得${res.reward}星币！`,
          icon: 'success'
        })
        // 更新星币余额
        if (app.globalData.coinsInfo) {
          app.globalData.coinsInfo.balance = res.new_balance
        }
      } else if (!res.already_completed) {
        wx.showToast({
          title: res.message || '领取失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('领取分享奖励失败:', error)
    }
  },
  
  // 解锁AI信件
  async unlockAiLetter() {
    const { memorialId } = this.data
    
    wx.showModal({
      title: '解锁AI信件',
      content: '确定要花费160星币解锁完整信件吗？',
      success: async (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '解锁中...' })
          
          try {
            const unlockRes = await app.request({
              url: `/api/memorials/${memorialId}/unlock-letter`,
              method: 'POST'
            })
            
            wx.hideLoading()
            
            if (unlockRes.success) {
              wx.showToast({
                title: '解锁成功！',
                icon: 'success'
              })
              
              // 更新纪念馆信息
              this.setData({
                'memorialInfo.ai_letter': unlockRes.ai_letter,
                'memorialInfo.ai_letter_locked': false,
                'memorialInfo.ai_letter_preview': null
              })
              
              // 更新星币余额
              if (app.globalData.coinsInfo) {
                app.globalData.coinsInfo.balance = unlockRes.new_balance
              }
            } else {
              wx.showModal({
                title: '解锁失败',
                content: unlockRes.message || '星币不足，请完成任务或观看广告获取星币',
                showCancel: false,
                success: (modalRes) => {
                  if (modalRes.confirm && unlockRes.balance !== undefined) {
                    // 星币不足，引导去任务/广告页
                    wx.navigateTo({
                      url: '/pages/coins-shop/coins-shop'
                    })
                  }
                }
              })
            }
          } catch (error) {
            wx.hideLoading()
            console.error('解锁AI信件失败:', error)
            wx.showToast({
              title: '解锁失败，请重试',
              icon: 'none'
            })
          }
        }
      }
    })
  },

  // 复制链接
  copyLink() {
    const link = `${app.globalData.baseUrl}/memorial/${this.data.memorialId}`
    wx.setClipboardData({
      data: link,
      success: () => {
        wx.showToast({
          title: '链接已复制',
          icon: 'success'
        })
      }
    })
  },

  // 分享配置
  onShareAppMessage() {
    const { memorialInfo } = this.data
    return {
      title: `${memorialInfo.pet_name}的纪念馆`,
      desc: memorialInfo.description || '珍贵的回忆，永远的陪伴',
      path: `/pages/memorial-detail/memorial-detail?id=${this.data.memorialId}`,
      imageUrl: memorialInfo.photos && memorialInfo.photos.length > 0 ? memorialInfo.photos[0] : ''
    }
  },

  onShareTimeline() {
    const { memorialInfo } = this.data
    // 分享后调用奖励API
    setTimeout(() => {
      this.claimShareReward()
    }, 500)
    
    return {
      title: `${memorialInfo.pet_name}的纪念馆 - 爪迹星`,
      query: `id=${this.data.memorialId}`,
      imageUrl: memorialInfo.photos && memorialInfo.photos.length > 0 ? memorialInfo.photos[0] : ''
    }
  },

  // 加载留言列表
  async loadMessages() {
    try {
      const res = await app.request({
        url: `/api/messages/${this.data.memorialId}`
      })

      if (res.success) {
        this.setData({
          messages: res.messages || []
        })
        console.log('留言加载成功:', res.messages)
      }
    } catch (error) {
      console.error('加载留言失败:', error)
      // 不显示错误提示，避免影响用户体验
    }
  },

  // 昵称输入
  onNameInput(e) {
    this.setData({
      'newMessage.name': e.detail.value
    })
  },

  // 留言内容输入
  onMessageInput(e) {
    this.setData({
      'newMessage.content': e.detail.value
    })
  },

  // 记录访问
  async recordVisit() {
    try {
      await app.request({
        url: '/api/visit-stat',
        method: 'POST',
        data: {
          memorial_id: this.data.memorialId
        }
      })
      console.log('访问记录成功')
    } catch (error) {
      console.error('记录访问失败:', error)
      // 不显示错误提示，避免影响用户体验
    }
  },

  // 加载访问统计
  async loadVisitStats() {
    try {
      const res = await app.request({
        url: `/api/visit-stats/${this.data.memorialId}`
      })

      if (res.success && res.stats) {
        this.setData({
          visitStats: {
            total_visits: res.stats.total_visits || 0,
            unique_visitors: res.stats.unique_visitors || 0,
            last_visit: res.stats.last_visit || null
          }
        })
        console.log('访问统计加载成功:', res.stats)
      }
    } catch (error) {
      console.error('加载访问统计失败:', error)
      // 不显示错误提示
    }
  },

  // 提交留言
  async submitMessage() {
    const { memorialId, newMessage } = this.data

    if (!newMessage.name || !newMessage.name.trim()) {
      wx.showToast({
        title: '请输入昵称',
        icon: 'none'
      })
      return
    }

    if (!newMessage.content || !newMessage.content.trim()) {
      wx.showToast({
        title: '请输入留言内容',
        icon: 'none'
      })
      return
    }

    this.setData({ submitting: true })

    try {
      const res = await app.request({
        url: '/api/message',
        method: 'POST',
        data: {
          memorial_id: memorialId,
          visitor_name: newMessage.name.trim(),
          message: newMessage.content.trim()
        }
      })

      if (res.success) {
        wx.showToast({
          title: '留言成功',
          icon: 'success'
        })

        // 清空输入
        this.setData({
          newMessage: {
            name: '',
            content: ''
          }
        })

        // 重新加载留言列表
        await this.loadMessages()
      } else {
        wx.showToast({
          title: res.message || '留言失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('提交留言失败:', error)
      wx.showToast({
        title: error.message || '留言失败',
        icon: 'none'
      })
    } finally {
      this.setData({ submitting: false })
    }
  },

  // 擦亮星星
  shineStar() {
    wx.showToast({ title: '⭐ 星星被你擦亮啦，让更多人看到Ta吧～', icon: 'success' });
  },
  // 送花
  giveFlower() {
    wx.showToast({ title: '🌸 鲜花已送达～', icon: 'success' });
  }
})