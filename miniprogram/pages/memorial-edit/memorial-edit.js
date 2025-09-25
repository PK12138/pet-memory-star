// pages/memorial-edit/memorial-edit.js
const app = getApp()

Page({
  data: {
    memorialId: null,
    memorialInfo: {
      pet_name: '',
      breed: '',
      age: '',
      gender: '',
      genderIndex: 0,
      color: '',
      birth_date: '',
      memorial_date: '',
      weight: '',
      description: '',
      personality: '',
      photos: []
    },
    genderOptions: ['公', '母'],
    loading: false
  },

  onLoad(options) {
    console.log('纪念馆编辑页加载', options)
    const { id } = options
    if (id) {
      this.setData({
        memorialId: id
      })
      this.loadMemorialInfo()
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

  // 加载纪念馆信息
  async loadMemorialInfo() {
    wx.showLoading({
      title: '加载中...'
    })

    try {
      const res = await app.request({
        url: `/api/memorial/get/${this.data.memorialId}`
      })

      if (res.success) {
        const memorial = res.memorial
        this.setData({
          memorialInfo: {
            pet_name: memorial.pet_name || '',
            breed: memorial.breed || '',
            age: memorial.age || '',
            gender: memorial.gender || '',
            genderIndex: memorial.gender === '母' ? 1 : 0,
            color: memorial.color || '',
            birth_date: memorial.birth_date || '',
            memorial_date: memorial.memorial_date || '',
            weight: memorial.weight || '',
            description: memorial.description || '',
            personality: memorial.personality || '',
            photos: memorial.photos || []
          }
        })
      } else {
        wx.showToast({
          title: res.message || '加载失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('加载纪念馆信息失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 宠物姓名输入
  onPetNameInput(e) {
    this.setData({
      'memorialInfo.pet_name': e.detail.value
    })
  },

  // 品种输入
  onBreedInput(e) {
    this.setData({
      'memorialInfo.breed': e.detail.value
    })
  },

  // 年龄输入
  onAgeInput(e) {
    this.setData({
      'memorialInfo.age': e.detail.value
    })
  },

  // 性别选择
  onGenderChange(e) {
    const index = e.detail.value
    this.setData({
      'memorialInfo.gender': this.data.genderOptions[index],
      'memorialInfo.genderIndex': index
    })
  },

  // 毛色输入
  onColorInput(e) {
    this.setData({
      'memorialInfo.color': e.detail.value
    })
  },

  // 出生日期选择
  onBirthDateChange(e) {
    this.setData({
      'memorialInfo.birth_date': e.detail.value
    })
  },

  // 纪念日期选择
  onMemorialDateChange(e) {
    this.setData({
      'memorialInfo.memorial_date': e.detail.value
    })
  },

  // 体重输入
  onWeightInput(e) {
    this.setData({
      'memorialInfo.weight': e.detail.value
    })
  },

  // 描述输入
  onDescriptionInput(e) {
    this.setData({
      'memorialInfo.description': e.detail.value
    })
  },

  // 性格输入
  onPersonalityInput(e) {
    this.setData({
      'memorialInfo.personality': e.detail.value
    })
  },

  // 选择照片
  choosePhotos() {
    wx.chooseImage({
      count: 9 - this.data.memorialInfo.photos.length,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePaths = res.tempFilePaths
        const photos = [...this.data.memorialInfo.photos, ...tempFilePaths]
        this.setData({
          'memorialInfo.photos': photos
        })
      },
      fail: (error) => {
        console.error('选择照片失败:', error)
        wx.showToast({
          title: '选择照片失败',
          icon: 'none'
        })
      }
    })
  },

  // 预览照片
  previewPhoto(e) {
    const url = e.currentTarget.dataset.url
    const photos = this.data.memorialInfo.photos
    wx.previewImage({
      current: url,
      urls: photos
    })
  },

  // 删除照片
  deletePhoto(e) {
    const index = e.currentTarget.dataset.index
    const photos = this.data.memorialInfo.photos
    photos.splice(index, 1)
    this.setData({
      'memorialInfo.photos': photos
    })
  },

  // 保存纪念馆
  async saveMemorial() {
    const { memorialInfo } = this.data

    // 验证必填字段
    if (!memorialInfo.pet_name.trim()) {
      wx.showToast({
        title: '请输入宠物姓名',
        icon: 'none'
      })
      return
    }

    if (!memorialInfo.breed.trim()) {
      wx.showToast({
        title: '请输入宠物品种',
        icon: 'none'
      })
      return
    }

    this.setData({
      loading: true
    })

    try {
      // 上传照片
      const uploadedPhotos = []
      for (const photo of memorialInfo.photos) {
        if (photo.startsWith('http')) {
          // 已经是服务器图片
          uploadedPhotos.push(photo)
        } else {
          // 需要上传的本地图片
          const uploadRes = await this.uploadPhoto(photo)
          if (uploadRes.success) {
            uploadedPhotos.push(uploadRes.url)
          }
        }
      }

      // 更新纪念馆信息
      const res = await app.request({
        url: `/api/memorial/update/${this.data.memorialId}`,
        method: 'PUT',
        data: {
          pet_name: memorialInfo.pet_name,
          breed: memorialInfo.breed,
          age: memorialInfo.age,
          gender: memorialInfo.gender,
          color: memorialInfo.color,
          birth_date: memorialInfo.birth_date,
          memorial_date: memorialInfo.memorial_date,
          weight: memorialInfo.weight,
          description: memorialInfo.description,
          personality: memorialInfo.personality,
          photos: uploadedPhotos
        }
      })

      if (res.success) {
        wx.showToast({
          title: '保存成功',
          icon: 'success'
        })
        
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      } else {
        wx.showToast({
          title: res.message || '保存失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('保存纪念馆失败:', error)
      wx.showToast({
        title: '保存失败',
        icon: 'none'
      })
    } finally {
      this.setData({
        loading: false
      })
    }
  },

  // 上传照片
  async uploadPhoto(filePath) {
    return new Promise((resolve) => {
      wx.uploadFile({
        url: `${app.globalData.baseUrl}/api/photos/upload`,
        filePath: filePath,
        name: 'photo',
        header: {
          'Authorization': `Bearer ${app.globalData.sessionToken}`
        },
        success: (res) => {
          try {
            const data = JSON.parse(res.data)
            resolve(data)
          } catch (error) {
            resolve({ success: false, message: '上传失败' })
          }
        },
        fail: () => {
          resolve({ success: false, message: '上传失败' })
        }
      })
    })
  },

  // 返回
  goBack() {
    wx.navigateBack()
  }
})