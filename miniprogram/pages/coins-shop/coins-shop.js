const app = getApp()
const api = require('../../utils/api')

Page({
  data: {
    coinsBalance: 0,
    activeCategory: 'membership',
    membershipProducts: [
      {
        id: 'monthly_vip',
        name: '月度会员',
        desc: '30天尊享特权',
        icon: '👑',
        badge: '推荐',
        price: 300,
        features: [
          '无限次AI对话',
          '梦境深度分析',
          '专属纪念模板',
          '照片无限上传'
        ],
        duration: 30
      },
      {
        id: 'yearly_vip',
        name: '年度会员',
        desc: '365天超值特权',
        icon: '💎',
        badge: '超值',
        price: 3000,
        features: [
          '包含月度会员所有特权',
          '专属VIP客服',
          '优先体验新功能',
          '每月赠送100星币'
        ],
        duration: 365
      },
      {
        id: 'lifetime_vip',
        name: '终身会员',
        desc: '永久尊享所有特权',
        icon: '⭐',
        badge: '限时',
        price: 9999,
        features: [
          '永久所有会员特权',
          '专属身份标识',
          '免费参加线下活动',
          '终身技术支持'
        ],
        duration: -1
      }
    ],
    featureProducts: [
      {
        id: 'extra_storage',
        name: '扩容包',
        desc: '增加1GB存储空间',
        icon: '📦',
        price: 100
      },
      {
        id: 'ai_quota',
        name: 'AI次数包',
        desc: '额外100次AI对话',
        icon: '🤖',
        price: 50
      },
      {
        id: 'custom_theme',
        name: '定制主题',
        desc: '解锁专属纪念主题',
        icon: '🎨',
        price: 200
      },
      {
        id: 'priority_support',
        name: '优先客服',
        desc: '7天优先客服支持',
        icon: '💬',
        price: 80
      }
    ]
  },

  onLoad() {
    this.loadCoinsBalance()
  },

  onShow() {
    this.loadCoinsBalance()
  },

  async loadCoinsBalance() {
    try {
      const res = await api.request({
        url: '/api/coins/balance',
        method: 'GET'
      })
      if (res.success) {
        this.setData({
          coinsBalance: res.balance
        })
      }
    } catch (error) {
      console.error('获取星币余额失败:', error)
    }
  },

  refreshBalance() {
    wx.showLoading({ title: '刷新中...' })
    this.loadCoinsBalance()
    setTimeout(() => {
      wx.hideLoading()
      wx.showToast({
        title: '刷新成功',
        icon: 'success'
      })
    }, 500)
  },

  switchCategory(e) {
    const category = e.currentTarget.dataset.category
    this.setData({
      activeCategory: category
    })
  },

  async handleBuy(e) {
    const product = e.currentTarget.dataset.product

    // 检查余额
    if (this.data.coinsBalance < product.price) {
      wx.showModal({
        title: '星币不足',
        content: `您的星币余额不足，还需${product.price - this.data.coinsBalance}星币`,
        confirmText: '去赚取',
        success: (res) => {
          if (res.confirm) {
            wx.navigateBack()
          }
        }
      })
      return
    }

    // 确认购买
    wx.showModal({
      title: '确认兑换',
      content: `确定花费${product.price}星币兑换"${product.name}"吗？`,
      confirmText: '确认兑换',
      success: async (res) => {
        if (res.confirm) {
          await this.processPurchase(product)
        }
      }
    })
  },

  async processPurchase(product) {
    wx.showLoading({ title: '兑换中...' })

    try {
      const res = await api.request({
        url: '/api/coins/spend',
        method: 'POST',
        data: {
          type: `buy_${product.id}`,
          amount: product.price,
          description: `购买${product.name}`
        }
      })

      wx.hideLoading()

      if (res.success) {
        // 如果是会员商品，需要激活会员
        if (product.duration) {
          await this.activateMembership(product)
        }

        wx.showModal({
          title: '兑换成功',
          content: `成功兑换${product.name}！\n剩余星币: ${res.new_balance}`,
          showCancel: false,
          success: () => {
            this.setData({
              coinsBalance: res.new_balance
            })
          }
        })
      } else {
        wx.showToast({
          title: res.message || '兑换失败',
          icon: 'none'
        })
      }
    } catch (error) {
      wx.hideLoading()
      console.error('兑换失败:', error)
      wx.showToast({
        title: '兑换失败，请重试',
        icon: 'none'
      })
    }
  },

  async activateMembership(product) {
    try {
      // 调用会员激活接口（需要后端支持）
      const duration = product.duration === -1 ? 36500 : product.duration
      await api.request({
        url: '/api/user/activate-membership',
        method: 'POST',
        data: {
          type: product.id,
          duration: duration
        }
      })
    } catch (error) {
      console.error('激活会员失败:', error)
    }
  }
})

