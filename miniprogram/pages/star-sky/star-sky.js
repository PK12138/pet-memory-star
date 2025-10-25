// pages/star-sky/star-sky.js
const app = getApp()

Page({
  data: {
    stars: [],
    totalStars: 0,
    loading: true,
    showCard: false,
    selectedStar: {},
    showMeteor: false,
    canvasWidth: 375,
    canvasHeight: 667,
    offsetX: 0,
    offsetY: 0,
    lastTouchX: 0,
    lastTouchY: 0
  },

  onLoad() {
    // 获取屏幕尺寸
    const systemInfo = wx.getSystemInfoSync()
    this.setData({
      canvasWidth: systemInfo.windowWidth,
      canvasHeight: systemInfo.windowHeight
    })

    // 加载星空数据
    this.loadStars()

    // 定期触发流星
    this.startMeteorInterval()
  },

  // 加载星星数据
  loadStars() {
    wx.request({
      url: `${app.globalData.baseUrl}/api/star-sky/memorials`,
      success: (res) => {
        console.log('星空数据:', res.data)
        if (res.data.success) {
          const stars = res.data.stars
          
          // 将坐标从0-100映射到屏幕坐标
          stars.forEach(star => {
            star.displayX = (star.x / 100) * this.data.canvasWidth
            star.displayY = (star.y / 100) * this.data.canvasHeight
            star.currentBrightness = star.brightness
          })
          
          this.setData({
            stars,
            totalStars: stars.length,
            loading: false
          }, () => {
            // 数据加载完成后绘制星空
            this.initCanvas()
          })
        } else {
          wx.showToast({
            title: '加载失败',
            icon: 'none'
          })
          this.setData({ loading: false })
        }
      },
      fail: (err) => {
        console.error('加载星空失败:', err)
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        })
        this.setData({ loading: false })
      }
    })
  },

  // 初始化Canvas
  initCanvas() {
    const query = wx.createSelectorQuery()
    query.select('#starCanvas')
      .fields({ node: true, size: true })
      .exec((res) => {
        if (res[0]) {
          const canvas = res[0].node
          const ctx = canvas.getContext('2d')
          
          const dpr = wx.getSystemInfoSync().pixelRatio
          canvas.width = res[0].width * dpr
          canvas.height = res[0].height * dpr
          ctx.scale(dpr, dpr)
          
          this.canvas = canvas
          this.ctx = ctx
          
          // 开始绘制
          this.drawStars()
          
          // 启动动画
          this.startAnimation()
        }
      })
  },

  // 绘制星星
  drawStars() {
    if (!this.ctx) return
    
    const ctx = this.ctx
    const { canvasWidth, canvasHeight, stars, offsetX, offsetY } = this.data
    
    // 清空画布
    ctx.clearRect(0, 0, canvasWidth, canvasHeight)
    
    // 绘制每颗星星
    stars.forEach(star => {
      const x = star.displayX + offsetX
      const y = star.displayY + offsetY
      
      // 只绘制在可见范围内的星星
      if (x < -50 || x > canvasWidth + 50 || y < -50 || y > canvasHeight + 50) {
        return
      }
      
      // 绘制光晕
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, star.size * 3)
      gradient.addColorStop(0, this.hexToRgba(star.color, star.currentBrightness * 0.5))
      gradient.addColorStop(0.5, this.hexToRgba(star.color, star.currentBrightness * 0.2))
      gradient.addColorStop(1, this.hexToRgba(star.color, 0))
      
      ctx.fillStyle = gradient
      ctx.beginPath()
      ctx.arc(x, y, star.size * 3, 0, Math.PI * 2)
      ctx.fill()
      
      // 绘制星星主体
      ctx.fillStyle = this.hexToRgba(star.color, star.currentBrightness)
      ctx.beginPath()
      ctx.arc(x, y, star.size, 0, Math.PI * 2)
      ctx.fill()
    })
  },

  // 启动动画
  startAnimation() {
    const animate = () => {
      const { stars } = this.data
      
      // 更新星星亮度（闪烁效果）
      stars.forEach(star => {
        // 随机改变亮度
        const delta = (Math.random() - 0.5) * 0.05
        star.currentBrightness += delta
        
        // 限制亮度范围
        star.currentBrightness = Math.max(0.3, Math.min(1, star.currentBrightness))
      })
      
      this.setData({ stars })
      this.drawStars()
      
      // 继续动画
      this.animationFrame = requestAnimationFrame(animate)
    }
    
    animate()
  },

  // 触摸开始
  onTouchStart(e) {
    const touch = e.touches[0]
    this.setData({
      lastTouchX: touch.x,
      lastTouchY: touch.y
    })
    this.touchStartTime = Date.now()
  },

  // 触摸移动（拖动星空）
  onTouchMove(e) {
    const touch = e.touches[0]
    const { lastTouchX, lastTouchY, offsetX, offsetY } = this.data
    
    const deltaX = touch.x - lastTouchX
    const deltaY = touch.y - lastTouchY
    
    this.setData({
      offsetX: offsetX + deltaX,
      offsetY: offsetY + deltaY,
      lastTouchX: touch.x,
      lastTouchY: touch.y
    })
  },

  // 触摸结束（检测点击）
  onTouchEnd(e) {
    const touchDuration = Date.now() - this.touchStartTime
    
    // 如果触摸时间很短，认为是点击
    if (touchDuration < 200) {
      const touch = e.changedTouches[0]
      this.checkStarClick(touch.x, touch.y)
    }
  },

  // 检测是否点击了星星
  checkStarClick(touchX, touchY) {
    const { stars, offsetX, offsetY } = this.data
    
    for (let star of stars) {
      const x = star.displayX + offsetX
      const y = star.displayY + offsetY
      
      const distance = Math.sqrt((touchX - x) ** 2 + (touchY - y) ** 2)
      
      // 检测范围：星星大小的3倍
      if (distance < star.size * 10) {
        this.showStarInfo(star)
        return
      }
    }
  },

  // 显示星星信息
  showStarInfo(star) {
    this.setData({
      selectedStar: star,
      showCard: true
    })
  },

  // 关闭卡片
  closeCard() {
    this.setData({ showCard: false })
  },

  stopPropagation() {
    // 阻止事件冒泡
  },

  // 查看纪念馆
  viewMemorial() {
    const memorialId = this.data.selectedStar.id
    wx.navigateTo({
      url: `/pages/memorial-detail/memorial-detail?id=${memorialId}`
    })
  },

  // 送花
  sendFlower() {
    wx.showToast({
      title: '送花成功 🌸',
      icon: 'success'
    })
    this.closeCard()
  },

  // 点亮星星
  lightStar() {
    wx.showToast({
      title: '星星更亮了 ✨',
      icon: 'success'
    })
    
    // 让星星变亮
    const { stars, selectedStar } = this.data
    const star = stars.find(s => s.id === selectedStar.id)
    if (star) {
      star.currentBrightness = 1
      star.size += 0.5
      this.setData({ stars })
    }
    
    this.closeCard()
  },

  // 搜索
  goToSearch() {
    wx.showToast({
      title: '搜索功能开发中',
      icon: 'none'
    })
  },

  // 定位到我的星星
  goToMyStar() {
    const token = wx.getStorageSync('session_token')
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      return
    }
    
    // TODO: 获取当前用户的纪念馆，定位到对应星星
    wx.showToast({
      title: '定位到我的星星',
      icon: 'success'
    })
  },

  // 许愿
  makeWish() {
    wx.showModal({
      title: '对着流星许愿',
      content: '写下你的心愿',
      editable: true,
      placeholderText: '我希望...',
      success: (res) => {
        if (res.confirm && res.content) {
          // 触发流星
          this.triggerMeteor()
          
          wx.showToast({
            title: '愿望已送达 ✨',
            icon: 'success'
          })
        }
      }
    })
  },

  // 触发流星
  triggerMeteor() {
    this.setData({ showMeteor: true })
    setTimeout(() => {
      this.setData({ showMeteor: false })
    }, 2000)
  },

  // 定期触发流星
  startMeteorInterval() {
    setInterval(() => {
      // 20%概率出现流星
      if (Math.random() < 0.2) {
        this.triggerMeteor()
      }
    }, 10000) // 每10秒检查一次
  },

  // 工具函数：hex转rgba
  hexToRgba(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16)
    const g = parseInt(hex.slice(3, 5), 16)
    const b = parseInt(hex.slice(5, 7), 16)
    return `rgba(${r}, ${g}, ${b}, ${alpha})`
  },

  // 获取物种emoji
  getSpeciesEmoji(species) {
    if (!species) return '🐾'
    
    const speciesLower = species.toLowerCase()
    if (speciesLower.includes('猫') || speciesLower.includes('cat')) {
      return '🐱'
    } else if (speciesLower.includes('狗') || speciesLower.includes('dog')) {
      return '🐶'
    } else if (speciesLower.includes('兔') || speciesLower.includes('rabbit')) {
      return '🐰'
    } else if (speciesLower.includes('鸟') || speciesLower.includes('bird')) {
      return '🐦'
    } else {
      return '🐾'
    }
  },

  onUnload() {
    // 清理动画
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame)
    }
  }
})

