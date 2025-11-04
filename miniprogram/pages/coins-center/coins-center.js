const app = getApp()
const api = require('../../utils/api')

Page({
  data: {
    coinsInfo: {
      balance: 0,
      total_earned: 0,
      total_spent: 0
    },
    signInInfo: {
      signed: false,
      continuous_days: 0
    },
    tasks: [
      { type: 'upload_photo', name: '上传照片', icon: '📷', reward: 5, max_daily: 3, today_count: 0 },
      { type: 'write_text', name: '撰写纪念文字', icon: '✍️', reward: 20, max_daily: 2, today_count: 0 },
      { type: 'ai_chat', name: 'AI对话', icon: '💬', reward: 2, max_daily: 10, today_count: 0 },
      { type: 'dream_diary', name: '记录梦境', icon: '🌙', reward: 15, max_daily: 2, today_count: 0 },
      { type: 'mood_diary', name: '记录心情', icon: '📔', reward: 15, max_daily: 2, today_count: 0 }
    ],
    adViewCount: 0,
    transactions: [],
    loading: false
  },

  onLoad() {
    this.loadCoinsData()
  },

  onShow() {
    this.loadCoinsData()
  },

  async loadCoinsData() {
    await Promise.all([
      this.loadCoinsBalance(),
      this.loadTransactions()
    ])
  },

  async loadCoinsBalance() {
    try {
      const res = await api.request({
        url: '/api/coins/balance',
        method: 'GET'
      })
      if (res.success) {
        this.setData({
          coinsInfo: {
            balance: res.balance,
            total_earned: res.total_earned,
            total_spent: res.total_spent
          }
        })
      }
    } catch (error) {
      console.error('获取星币余额失败:', error)
    }
  },

  async loadTransactions() {
    try {
      const res = await api.request({
        url: '/api/coins/transactions?page=1&limit=10',
        method: 'GET'
      })
      if (res.success) {
        this.setData({
          transactions: res.transactions.map(t => ({
            ...t,
            created_at: this.formatTime(t.created_at)
          }))
        })
      }
    } catch (error) {
      console.error('获取交易记录失败:', error)
    }
  },

  async handleSignIn() {
    if (this.data.signInInfo.signed) {
      wx.showToast({
        title: '今日已签到',
        icon: 'none'
      })
      return
    }

    if (this.data.loading) return
    this.setData({ loading: true })

    try {
      const res = await api.request({
        url: '/api/coins/sign-in',
        method: 'POST'
      })
      
      if (res.success) {
        wx.showModal({
          title: '签到成功',
          content: `${res.message}\n当前余额: ${res.new_balance}星币`,
          showCancel: false,
          success: () => {
            this.setData({
              'signInInfo.signed': true,
              'signInInfo.continuous_days': res.continuous_days,
              'coinsInfo.balance': res.new_balance
            })
            this.loadCoinsData()
          }
        })
      } else {
        wx.showToast({
          title: res.message || '签到失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('签到失败:', error)
      wx.showToast({
        title: '签到失败，请重试',
        icon: 'none'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  async handleWatchAd() {
    if (this.data.adViewCount >= 5) {
      wx.showToast({
        title: '今日观看次数已达上限',
        icon: 'none'
      })
      return
    }

    // 微信激励视频广告
    if (wx.createRewardedVideoAd) {
      const videoAd = wx.createRewardedVideoAd({
        adUnitId: 'your-ad-unit-id' // 需要在微信公众平台申请
      })

      videoAd.onLoad(() => {
        console.log('激励视频广告加载成功')
      })

      videoAd.onError((err) => {
        console.error('激励视频广告加载失败', err)
        wx.showToast({
          title: '广告加载失败',
          icon: 'none'
        })
      })

      videoAd.onClose((res) => {
        if (res && res.isEnded) {
          // 用户看完广告，发放奖励
          this.rewardAdComplete()
        } else {
          wx.showToast({
            title: '请看完广告才能获得奖励',
            icon: 'none'
          })
        }
      })

      videoAd.show().catch(() => {
        videoAd.load()
          .then(() => videoAd.show())
          .catch(err => {
            console.error('广告显示失败', err)
            // 开发阶段，直接模拟广告完成
            if (process.env.NODE_ENV === 'development') {
              this.rewardAdComplete()
            }
          })
      })
    } else {
      // 开发阶段或不支持广告的版本，直接模拟
      this.rewardAdComplete()
    }
  },

  async rewardAdComplete() {
    try {
      const res = await api.request({
        url: '/api/coins/watch-ad',
        method: 'POST',
        data: {
          ad_unit_id: 'your-ad-unit-id'
        }
      })

      if (res.success) {
        wx.showToast({
          title: `获得${res.reward}星币！`,
          icon: 'success'
        })
        this.setData({
          adViewCount: res.today_count,
          'coinsInfo.balance': res.new_balance
        })
        this.loadCoinsData()
      } else {
        wx.showToast({
          title: res.message || '领取奖励失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('领取广告奖励失败:', error)
    }
  },

  goToShop() {
    wx.navigateTo({
      url: '/pages/coins-shop/coins-shop'
    })
  },

  formatTime(timeStr) {
    if (!timeStr) return ''
    const date = new Date(timeStr)
    const now = new Date()
    const diff = now - date

    if (diff < 60000) return '刚刚'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`

    return `${date.getMonth() + 1}-${date.getDate()}`
  }
})

