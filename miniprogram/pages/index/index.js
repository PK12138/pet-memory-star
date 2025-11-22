// pages/index/index.js
const app = getApp()

Page({
  data: {
    userInfo: null,
    stars: [],
    myStarCount: 0,
    totalStars: 0,
    loading: true,
    showWelcome: true,
    selectedStar: null,
    unreadLetters: 0,
    canvasWidth: 375,
    canvasHeight: 667,
    lastTouchX: 0,
    lastTouchY: 0,
    welcomeAnimation: null,
    // 3D球体相关
    rotationX: 0,  // 上下旋转角度
    rotationY: 0,  // 左右旋转角度
    sphereRadius: 300,  // 球体半径
    autoRotate: true  // 自动旋转
  },

  onLoad() {
    console.log('新主页加载')
    
    // 获取屏幕尺寸
    const systemInfo = wx.getSystemInfoSync()
    this.setData({
      canvasWidth: systemInfo.windowWidth,
      canvasHeight: systemInfo.windowHeight
    })

    // 检查登录状态
    this.checkAuthStatus()
    
    // 加载星空数据
    this.loadStars()
    
    // 3秒后隐藏欢迎界面
    setTimeout(() => {
      this.hideWelcome()
    }, 3000)
  },

  onShow() {
    console.log('新主页显示')
    this.checkAuthStatus()
    
    // 如果已经初始化过，重新加载数据
    if (this.ctx) {
      this.loadStars()
    }
  },

  onUnload() {
    // 清理动画
    if (this.animationFrame) {
      clearTimeout(this.animationFrame)
    }
  },

  // 检查用户登录状态
  async checkAuthStatus() {
    try {
      let userInfo = app.globalData.userInfo
      let sessionToken = app.globalData.sessionToken
      
      // 尝试从本地存储读取
      if (!sessionToken) {
        sessionToken = wx.getStorageSync('sessionToken')
        if (sessionToken) {
          app.globalData.sessionToken = sessionToken
        }
      }
      
      if (!userInfo && sessionToken) {
        userInfo = wx.getStorageSync('userInfo')
        if (userInfo) {
          app.globalData.userInfo = userInfo
        }
      }
      
      console.log('登录状态:', {
        hasUserInfo: !!userInfo,
        hasSessionToken: !!sessionToken
      })
      
        this.setData({
        userInfo: userInfo || null
      })
      
      // 如果已登录，加载未读信件数
      if (userInfo && sessionToken) {
        this.loadUnreadLetters()
      }
    } catch (error) {
      console.error('检查登录状态失败:', error)
    }
  },

  // 加载未读信件数（占位功能）
  async loadUnreadLetters() {
    // TODO: 实现信件系统后调用真实API
    this.setData({
      unreadLetters: 0
    })
  },

  // 加载星星数据
  loadStars() {
    const sessionToken = wx.getStorageSync('sessionToken') || app.globalData.sessionToken
    
    wx.request({
      url: `${app.globalData.baseUrl}/api/star-sky/memorials`,
      header: sessionToken ? {
        'x-session-token': sessionToken
      } : {},
      success: (res) => {
        console.log('星空数据:', res.data)
        if (res.data.success) {
          const stars = res.data.stars || []
          
          // 将星星分布在球体表面（使用球面坐标）
          stars.forEach((star, index) => {
            // 使用原始x,y作为球面坐标的theta和phi
            // 或者均匀分布（斐波那契球面分布）
            const phi = Math.acos(-1 + (2 * star.y) / 100)  // 纬度 0-π
            const theta = Math.sqrt(stars.length * Math.PI) * phi + (star.x / 100) * Math.PI * 2  // 经度 0-2π
            
            star.phi = phi
            star.theta = theta
            star.currentBrightness = star.brightness || 0.8
            star.baseSize = star.size || 3
            
            // 清理无效的图片URL（避免500错误）
            if (star.photo_url && (star.photo_url === 'null' || star.photo_url === null)) {
              star.photo_url = null
            }
          })
          
          // 计算星星数量（全部星星，不再过滤 is_mine）
          const myStarCount = stars.length
          
        this.setData({
            stars,
            myStarCount,
            totalStars: stars.length,
            loading: false
          }, () => {
            // 数据加载完成后绘制星空
            this.initCanvas()
        })
      } else {
          this.setData({ loading: false })
        }
      },
      fail: (err) => {
        console.error('加载星空失败:', err)
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

  // 绘制星星（3D球体投影）
  drawStars() {
    if (!this.ctx) return
    
    const ctx = this.ctx
    const { canvasWidth, canvasHeight, stars, rotationX, rotationY, sphereRadius } = this.data
    
    // 清空画布
    ctx.clearRect(0, 0, canvasWidth, canvasHeight)
    
    // 绘制背景星星（装饰性小星星）
    this.drawBackgroundStars(ctx, canvasWidth, canvasHeight)
    
    // 计算每颗星星的3D投影位置
    const projectedStars = stars.map(star => {
      // 球面坐标转3D笛卡尔坐标
      const x3d = sphereRadius * Math.sin(star.phi) * Math.cos(star.theta + rotationY)
      const y3d = sphereRadius * Math.cos(star.phi + rotationX)
      const z3d = sphereRadius * Math.sin(star.phi) * Math.sin(star.theta + rotationY)
      
      // 透视投影到2D（简单正交投影，可以改为透视投影）
      const perspective = 600  // 视距
      const scale = perspective / (perspective + z3d)
      
      const x2d = canvasWidth / 2 + x3d * scale
      const y2d = canvasHeight / 2 + y3d * scale
      
      // 计算深度（用于排序和透明度）
      const depth = z3d
      
      // 根据深度调整大小和亮度
      const sizeScale = Math.max(0.3, scale)
      const brightness = Math.max(0.2, Math.min(1, (depth + sphereRadius) / (sphereRadius * 2)))
      
      return {
        ...star,
        x2d,
        y2d,
        depth,
        displaySize: star.baseSize * sizeScale,
        displayBrightness: star.currentBrightness * brightness,
        visible: z3d > -sphereRadius * 0.3  // 只显示前半球
      }
    })
    
    // 按深度排序（后面的先绘制）
    projectedStars.sort((a, b) => a.depth - b.depth)
    
    // 绘制纪念星星
    projectedStars.forEach(star => {
      if (!star.visible) return
      
      const x = star.x2d
      const y = star.y2d
      const size = star.displaySize
      const color = star.color || '#FFD700'
      const brightness = star.displayBrightness
      
      // 绘制光晕
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, size * 4)
      gradient.addColorStop(0, this.hexToRgba(color, brightness * 0.6))
      gradient.addColorStop(0.5, this.hexToRgba(color, brightness * 0.3))
      gradient.addColorStop(1, this.hexToRgba(color, 0))
      
      ctx.fillStyle = gradient
      ctx.beginPath()
      ctx.arc(x, y, size * 4, 0, Math.PI * 2)
      ctx.fill()
      
      // 绘制星星主体
      ctx.fillStyle = this.hexToRgba(color, brightness)
      ctx.beginPath()
      ctx.arc(x, y, size, 0, Math.PI * 2)
      ctx.fill()
      
      // 如果是我的星星，添加标记
      if (star.is_mine) {
        ctx.strokeStyle = this.hexToRgba('#FFD700', brightness * 0.8)
        ctx.lineWidth = 1.5
        ctx.beginPath()
        ctx.arc(x, y, size + 3, 0, Math.PI * 2)
        ctx.stroke()
      }
      
      // 绘制宠物名称
      if (star.pet_name && size > 2) {
        ctx.fillStyle = this.hexToRgba('#FFFFFF', brightness * 0.9)
        ctx.font = `${Math.max(10, size * 2)}px sans-serif`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'top'
        
        // 添加文字阴影
        ctx.shadowColor = 'rgba(0, 0, 0, 0.8)'
        ctx.shadowBlur = 4
        ctx.shadowOffsetX = 1
        ctx.shadowOffsetY = 1
        
        ctx.fillText(star.pet_name, x, y + size + 8)
        
        // 重置阴影
        ctx.shadowColor = 'transparent'
        ctx.shadowBlur = 0
        ctx.shadowOffsetX = 0
        ctx.shadowOffsetY = 0
      }
    })
    
    // 保存投影后的星星数据，用于点击检测
    this.projectedStars = projectedStars
  },

  // 绘制背景装饰星星
  drawBackgroundStars(ctx, width, height) {
    // 使用固定种子生成随机但稳定的背景星星
    if (!this.backgroundStars) {
      this.backgroundStars = []
      for (let i = 0; i < 100; i++) {
        this.backgroundStars.push({
          x: Math.random() * width,
          y: Math.random() * height,
          size: Math.random() * 1.5 + 0.5,
          brightness: Math.random() * 0.5 + 0.3
        })
      }
    }
    
    this.backgroundStars.forEach(star => {
      ctx.fillStyle = this.hexToRgba('#FFFFFF', star.brightness)
      ctx.beginPath()
      ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2)
      ctx.fill()
    })
  },

  // 启动动画
  startAnimation() {
    const animate = () => {
      const { stars, autoRotate, rotationY } = this.data
      
      // 更新星星亮度（闪烁效果）
      stars.forEach(star => {
        const delta = (Math.random() - 0.5) * 0.08
        star.currentBrightness += delta
        star.currentBrightness = Math.max(0.4, Math.min(1, star.currentBrightness))
      })
      
      // 自动旋转
      let newRotationY = rotationY
      if (autoRotate && !this.isTouching) {
        newRotationY += 0.002  // 缓慢自动旋转
      }
      
      this.setData({
        stars,
        rotationY: newRotationY
      })
      this.drawStars()
      
      // 继续动画
      this.animationFrame = setTimeout(animate, 1000 / 30) // 30fps
    }
    
    animate()
  },

  // 隐藏欢迎界面
  hideWelcome() {
    const animation = wx.createAnimation({
      duration: 500,
      timingFunction: 'ease-out'
    })
    animation.opacity(0).step()
    
    this.setData({
      welcomeAnimation: animation.export()
    })
    
    setTimeout(() => {
      this.setData({
        showWelcome: false
      })
    }, 500)
  },

  // 触摸事件（旋转球体）
  onTouchStart(e) {
    const touch = e.touches[0]
    this.setData({
      lastTouchX: touch.x,
      lastTouchY: touch.y
    })
    this.touchStartTime = Date.now()
    this.touchMoved = false
    this.isTouching = true  // 停止自动旋转
  },

  onTouchMove(e) {
    this.touchMoved = true
    const touch = e.touches[0]
    const { lastTouchX, lastTouchY, rotationX, rotationY, canvasWidth, canvasHeight } = this.data
    
    const deltaX = touch.x - lastTouchX
    const deltaY = touch.y - lastTouchY
    
    // 根据滑动距离计算旋转角度
    const rotationSpeedX = 0.005  // 上下旋转灵敏度
    const rotationSpeedY = 0.005  // 左右旋转灵敏度
    
    let newRotationX = rotationX - deltaY * rotationSpeedX
    let newRotationY = rotationY - deltaX * rotationSpeedY  // 反转左右滑动方向
    
    // 限制上下旋转角度（避免翻转过头）
    newRotationX = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, newRotationX))
    
    this.setData({
      rotationX: newRotationX,
      rotationY: newRotationY,
      lastTouchX: touch.x,
      lastTouchY: touch.y
    })
  },

  onTouchEnd(e) {
    const touchDuration = Date.now() - this.touchStartTime
    this.isTouching = false  // 恢复自动旋转
    
    // 如果是点击（没有拖动且时间短）
    if (!this.touchMoved && touchDuration < 300) {
      const touch = e.changedTouches[0]
      this.checkStarClick(touch.x, touch.y)
    }
  },

  // 检查是否点击了星星（使用3D投影后的坐标）
  checkStarClick(touchX, touchY) {
    if (!this.projectedStars) return
    
    // 从前往后检测（因为已按深度排序）
    const reversedStars = [...this.projectedStars].reverse()
    
    for (let star of reversedStars) {
      if (!star.visible) continue
      
      const x = star.x2d
      const y = star.y2d
      const size = star.displaySize * 4 // 扩大点击范围
      
      const distance = Math.sqrt(Math.pow(touchX - x, 2) + Math.pow(touchY - y, 2))
      
      if (distance <= size) {
        // 点击了这颗星星
        this.showStarDetail(star)
        return
      }
    }
  },

  // 显示星星详情
  showStarDetail(star) {
    console.log('显示星星详情:', star)
    
    // 轻微震动反馈
    wx.vibrateShort({
      type: 'light'
    })
    
        this.setData({
      selectedStar: star
    })
  },

  // 关闭星星详情
  closeStarDetail() {
        this.setData({
      selectedStar: null
    })
  },

  // 阻止事件冒泡
  stopPropagation() {
    // 空函数，用于阻止冒泡
  },

  // 图片加载失败处理
  onImageError(e) {
    console.log('图片加载失败，使用占位符')
    // 图片加载失败时，更新当前星星数据，避免重复尝试加载
    if (this.data.selectedStar) {
      this.setData({
        'selectedStar.photo_url': null
      })
    }
  },

  // 导航方法
  startCreateStar() {
    const sessionToken = app.globalData.sessionToken || wx.getStorageSync('sessionToken')
    
    if (!sessionToken) {
      wx.showModal({
        title: '提示',
        content: '请先登录后再创建星星',
        confirmText: '去登录',
        success: (res) => {
          if (res.confirm) {
      wx.navigateTo({
        url: '/pages/login/login'
            })
          }
        }
      })
      return
    }
    
    // 跳转到性格测试页面（创建纪念馆）
    wx.navigateTo({
      url: '/pages/personality-test/personality-test'
    })
  },

  goToLetterBox() {
    wx.showToast({
      title: '信件箱功能开发中',
      icon: 'none'
    })
    // TODO: 实现后跳转到信件箱页面
    // wx.navigateTo({
    //   url: '/pages/letter-box/letter-box'
    // })
  },

  goToChat() {
    const sessionToken = app.globalData.sessionToken || wx.getStorageSync('sessionToken')
    
    if (!sessionToken) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      return
    }
    
    // 如果有星星，跳转到纪念馆列表选择对话对象
    if (this.data.myStarCount > 0) {
    wx.navigateTo({
      url: '/pages/memorials/memorials'
    })
    } else {
      wx.showModal({
        title: '提示',
        content: '您还没有创建星星，是否立即创建？',
        confirmText: '创建星星',
        success: (res) => {
          if (res.confirm) {
            this.startCreateStar()
          }
        }
      })
    }
  },

  goToProfile() {
    const sessionToken = app.globalData.sessionToken || wx.getStorageSync('sessionToken')
    
    if (!sessionToken) {
      // 未登录，显示登录/注册选项
      wx.showModal({
        title: '提示',
        content: '请先登录',
        confirmText: '去登录',
        cancelText: '去注册',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({
              url: '/pages/login/login'
            })
          } else if (res.cancel) {
            wx.navigateTo({
              url: '/pages/register/register'
            })
          }
        }
      })
      return
    }
    
    // 已登录，跳转到个人中心
    wx.navigateTo({
      url: '/pages/user-center/user-center'
    })
  },

  goToFeedback() {
    wx.navigateTo({
      url: '/pages/feedback/feedback'
    })
  },

  // 查看纪念馆
  viewMemorial(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/memorial-detail/memorial-detail?id=${id}`
    })
  },

  // 与宠物对话
  chatWithPet(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/ai-chat/ai-chat?memorialId=${id}`
    })
  },

  // 工具方法：16进制颜色转RGBA
  hexToRgba(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16)
    const g = parseInt(hex.slice(3, 5), 16)
    const b = parseInt(hex.slice(5, 7), 16)
    return `rgba(${r}, ${g}, ${b}, ${alpha})`
  }
})
