// pages/theme-settings/theme-settings.js
const app = getApp()

Page({
  data: {
    currentTheme: 'default',
    themes: [
      {
        id: 'default',
        name: '默认主题',
        desc: '清新典雅，温馨舒适',
        primaryColor: '#667eea',
        secondaryColor: '#764ba2',
        icon: '🌸',
        preview: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      },
      {
        id: 'warm',
        name: '温暖阳光',
        desc: '温暖明亮，充满希望',
        primaryColor: '#f093fb',
        secondaryColor: '#f5576c',
        icon: '🌞',
        preview: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
      },
      {
        id: 'ocean',
        name: '海洋之心',
        desc: '宁静深邃，平和安详',
        primaryColor: '#4facfe',
        secondaryColor: '#00f2fe',
        icon: '🌊',
        preview: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
      },
      {
        id: 'forest',
        name: '森林绿意',
        desc: '自然清新，生机盎然',
        primaryColor: '#43e97b',
        secondaryColor: '#38f9d7',
        icon: '🌲',
        preview: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
      },
      {
        id: 'sunset',
        name: '日落余晖',
        desc: '温柔浪漫，怀念美好',
        primaryColor: '#fa709a',
        secondaryColor: '#fee140',
        icon: '🌅',
        preview: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
      },
      {
        id: 'lavender',
        name: '薰衣草',
        desc: '优雅梦幻，安静舒缓',
        primaryColor: '#a8edea',
        secondaryColor: '#fed6e3',
        icon: '💜',
        preview: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)'
      },
      {
        id: 'autumn',
        name: '秋日枫叶',
        desc: '成熟稳重，怀旧温馨',
        primaryColor: '#ff9a56',
        secondaryColor: '#ff6a88',
        icon: '🍁',
        preview: 'linear-gradient(135deg, #ff9a56 0%, #ff6a88 100%)'
      },
      {
        id: 'night',
        name: '星空夜幕',
        desc: '神秘深邃，静谧安宁',
        primaryColor: '#5f72bd',
        secondaryColor: '#9b23ea',
        icon: '🌙',
        preview: 'linear-gradient(135deg, #5f72bd 0%, #9b23ea 100%)'
      }
    ]
  },

  onLoad() {
    console.log('主题设置页加载')
    this.loadCurrentTheme()
  },

  onShow() {
    console.log('主题设置页显示')
  },

  // 加载当前主题
  loadCurrentTheme() {
    try {
      const theme = wx.getStorageSync('app_theme') || 'default'
      this.setData({
        currentTheme: theme
      })
      console.log('当前主题:', theme)
    } catch (error) {
      console.error('加载主题失败:', error)
    }
  },

  // 选择主题
  async selectTheme(e) {
    const themeId = e.currentTarget.dataset.id
    const theme = this.data.themes.find(t => t.id === themeId)
    
    if (!theme) {
      console.error('主题不存在:', themeId)
      return
    }

    console.log('选择主题:', themeId)

    try {
      // 保存主题到本地存储
      wx.setStorageSync('app_theme', themeId)
      wx.setStorageSync('app_theme_config', {
        id: theme.id,
        name: theme.name,
        primaryColor: theme.primaryColor,
        secondaryColor: theme.secondaryColor
      })

      // 更新当前主题
      this.setData({
        currentTheme: themeId
      })

      // 更新全局数据
      if (app.globalData) {
        app.globalData.theme = themeId
      }

      // 显示成功提示
      wx.showToast({
        title: `已切换到${theme.name}`,
        icon: 'success',
        duration: 1500
      })

      // 延迟返回，让用户看到主题变化
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)

    } catch (error) {
      console.error('保存主题失败:', error)
      wx.showToast({
        title: '设置失败',
        icon: 'none'
      })
    }
  },

  // 重置为默认主题
  resetTheme() {
    wx.showModal({
      title: '重置主题',
      content: '确定要重置为默认主题吗？',
      success: (res) => {
        if (res.confirm) {
          try {
            wx.removeStorageSync('app_theme')
            wx.removeStorageSync('app_theme_config')
            
            this.setData({
              currentTheme: 'default'
            })

            if (app.globalData) {
              app.globalData.theme = 'default'
            }

            wx.showToast({
              title: '已重置为默认主题',
              icon: 'success'
            })

            setTimeout(() => {
              wx.navigateBack()
            }, 1500)

          } catch (error) {
            console.error('重置主题失败:', error)
            wx.showToast({
              title: '重置失败',
              icon: 'none'
            })
          }
        }
      }
    })
  }
})

