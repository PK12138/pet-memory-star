// pages/personality-test/personality-test.js
const app = getApp()

Page({
  data: {
    currentQuestion: 1,
    totalQuestions: 10,
    progress: 0,
    showPetInfo: true,
    showResult: false,
    petInfo: {
      name: '',
      species: '',
      speciesIndex: -1,
      breed: '',
      color: '',
      gender: '',
      genderIndex: -1,
      weight: '',
      birthDate: '',
      memorialDate: '',
      status: '',
      statusIndex: -1,
      address: '',
      photos: []
    },
    speciesOptions: ['猫', '狗', '兔子', '鸟', '仓鼠', '其他'],
    genderOptions: ['公', '母'],
    statusOptions: ['健在', '已逝世'],
    questions: {},
    currentQuestionData: null,
    currentQuestionOptions: [],
    answers: {},
    personalityResult: '',
    memorialInfo: {
      description: ''
    },
    loading: false,
    canProceed: false
  },

  onLoad() {
    console.log('性格测试页加载')
    this.loadQuestions()
  },

  // 加载问题数据
  async loadQuestions() {
    console.log('开始加载问题')
    
    // 使用与网页版一致的题目数据
    const localQuestions = {
      1: {
        id: 1,
        question: "当遇到陌生人时，你的宠物通常会：",
        options: ["躲起来观察", "主动上前打招呼", "保持距离但好奇", "完全不在意"]
      },
      2: {
        id: 2,
        question: "在玩耍时，你的宠物更喜欢：",
        options: ["独自探索", "与主人互动", "与其他宠物玩耍", "安静地观察"]
      },
      3: {
        id: 3,
        question: "当主人回家时，你的宠物会：",
        options: ["兴奋地跑来跑去", "温柔地蹭主人", "摇尾巴表示欢迎", "继续做自己的事"]
      },
      4: {
        id: 4,
        question: "面对新玩具时，你的宠物会：",
        options: ["立即尝试", "先观察再尝试", "等主人示范", "不感兴趣"]
      },
      5: {
        id: 5,
        question: "在休息时，你的宠物喜欢：",
        options: ["找个安静角落", "靠近主人身边", "在能看到主人的地方", "随意找个地方"]
      },
      6: {
        id: 6,
        question: "当听到奇怪声音时，你的宠物会：",
        options: ["立即警觉", "好奇地寻找声源", "寻求主人保护", "继续休息"]
      },
      7: {
        id: 7,
        question: "与其他宠物相处时，你的宠物：",
        options: ["保持独立", "主动社交", "谨慎接触", "完全忽视"]
      },
      8: {
        id: 8,
        question: "在训练时，你的宠物：",
        options: ["专注且快速学习", "需要鼓励和奖励", "容易分心", "抗拒训练"]
      },
      9: {
        id: 9,
        question: "当主人心情不好时，你的宠物会：",
        options: ["默默陪伴", "主动安慰", "试图转移注意力", "保持距离"]
      },
      10: {
        id: 10,
        question: "面对食物时，你的宠物：",
        options: ["立即吃完", "慢慢品尝", "先闻再吃", "挑食"]
      }
    }
    
    this.setData({
      questions: localQuestions,
      totalQuestions: Object.keys(localQuestions).length
    })
    
    console.log('问题加载完成:', localQuestions)
    this.updateProgress()
  },

  // 加载问题选项
  loadQuestionOptions(questionId) {
    console.log('加载第', questionId, '题')
    
    const questionData = this.data.questions[questionId]
    if (questionData) {
      this.setData({
        currentQuestionData: questionData,
        currentQuestionOptions: questionData.options
      })
      console.log('当前题目:', questionData)
      this.updateProgress()
      this.checkCanProceed()
    } else {
      console.error('找不到题目:', questionId)
    }
  },

  // 更新进度
  updateProgress() {
    const { currentQuestion, totalQuestions, showPetInfo } = this.data
    let progress = 0
    
    if (showPetInfo) {
      progress = 10
    } else {
      progress = 10 + (currentQuestion / totalQuestions) * 90
    }
    
    this.setData({
      progress: Math.round(progress)
    })
  },

  // 检查是否可以继续
  checkCanProceed() {
    const { showPetInfo, petInfo, currentQuestion, answers } = this.data
    let canProceed = false
    
    if (showPetInfo) {
      // 必填项：宠物姓名、种类、纪念日期、状态、照片
      canProceed = petInfo.name && 
                   petInfo.species && 
                   petInfo.memorialDate && 
                   petInfo.status && 
                   petInfo.photos.length > 0
    } else {
      canProceed = answers[currentQuestion] !== undefined
    }
    
    this.setData({
      canProceed
    })
  },

  // 宠物姓名输入
  onPetNameInput(e) {
    this.setData({
      'petInfo.name': e.detail.value
    })
    this.checkCanProceed()
  },

  // 宠物种类选择
  onSpeciesChange(e) {
    const index = e.detail.value
    this.setData({
      'petInfo.species': this.data.speciesOptions[index],
      'petInfo.speciesIndex': index
    })
    this.checkCanProceed()
  },

  // 宠物品种输入
  onPetBreedInput(e) {
    this.setData({
      'petInfo.breed': e.detail.value
    })
    this.checkCanProceed()
  },

  // 毛色输入
  onPetColorInput(e) {
    this.setData({
      'petInfo.color': e.detail.value
    })
    this.checkCanProceed()
  },

  // 性别选择
  onGenderChange(e) {
    const index = e.detail.value
    this.setData({
      'petInfo.gender': this.data.genderOptions[index],
      'petInfo.genderIndex': index
    })
    this.checkCanProceed()
  },

  // 体重输入
  onPetWeightInput(e) {
    this.setData({
      'petInfo.weight': e.detail.value
    })
    this.checkCanProceed()
  },

  // 出生日期选择
  onBirthDateChange(e) {
    this.setData({
      'petInfo.birthDate': e.detail.value
    })
    this.checkCanProceed()
  },

  // 纪念日期选择
  onMemorialDateChange(e) {
    this.setData({
      'petInfo.memorialDate': e.detail.value
    })
    this.checkCanProceed()
  },

  // 状态选择
  onStatusChange(e) {
    const index = e.detail.value
    this.setData({
      'petInfo.status': this.data.statusOptions[index],
      'petInfo.statusIndex': index
    })
    this.checkCanProceed()
  },

  // 地址输入
  onPetAddressInput(e) {
    this.setData({
      'petInfo.address': e.detail.value
    })
    this.checkCanProceed()
  },

  // 选择图片
  chooseImage(e) {
    // 阻止事件冒泡
    if (e.currentTarget.dataset.index !== undefined) {
      return
    }
    
    const maxCount = 9 - this.data.petInfo.photos.length
    
    wx.chooseImage({
      count: maxCount,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePaths = res.tempFilePaths
        const photos = this.data.petInfo.photos.concat(tempFilePaths)
        this.setData({
          'petInfo.photos': photos
        })
        this.checkCanProceed()
      }
    })
  },

  // 删除图片
  deleteImage(e) {
    const index = e.currentTarget.dataset.index
    const photos = this.data.petInfo.photos
    photos.splice(index, 1)
    this.setData({
      'petInfo.photos': photos
    })
    this.checkCanProceed()
  },

  // 选择答案
  selectAnswer(e) {
    const option = e.currentTarget.dataset.option
    const { currentQuestion } = this.data
    
    this.setData({
      [`answers.${currentQuestion}`]: option
    })
    
    this.checkCanProceed()
  },

  // 下一步
  nextStep() {
    const { showPetInfo, currentQuestion, totalQuestions } = this.data
    
    if (showPetInfo) {
      // 从宠物信息进入问题测试
      this.setData({
        showPetInfo: false
      })
      this.loadQuestionOptions(1)
    } else if (currentQuestion < totalQuestions) {
      // 进入下一题
      const nextQuestion = currentQuestion + 1
      this.setData({
        currentQuestion: nextQuestion
      })
      this.loadQuestionOptions(nextQuestion)
    } else {
      // 完成测试，显示结果
      this.generateResult()
    }
  },

  // 上一步
  prevStep() {
    const { showPetInfo, currentQuestion } = this.data
    
    if (showPetInfo) {
      // 返回首页
      wx.navigateBack()
    } else if (currentQuestion > 1) {
      // 返回上一题
      const prevQuestion = currentQuestion - 1
      this.setData({
        currentQuestion: prevQuestion
      })
      this.loadQuestionOptions(prevQuestion)
    } else {
      // 返回宠物信息
      this.setData({
        showPetInfo: true
      })
      this.updateProgress()
      this.checkCanProceed()
    }
  },

  // 生成测试结果
  generateResult() {
    const { answers, petInfo } = this.data
    
    // 简单的性格分析逻辑
    let personality = '温和'
    let description = ''
    
    // 根据答案分析性格
    const answerValues = Object.values(answers)
    const activeCount = answerValues.filter(answer => 
      answer.includes('活泼') || answer.includes('玩耍') || answer.includes('好动')
    ).length
    
    const calmCount = answerValues.filter(answer => 
      answer.includes('安静') || answer.includes('睡觉') || answer.includes('温顺')
    ).length
    
    if (activeCount > calmCount) {
      personality = '活泼好动'
      description = `${petInfo.name}是一只活泼好动的${petInfo.breed}，喜欢玩耍和运动，充满活力。`
    } else if (calmCount > activeCount) {
      personality = '安静温顺'
      description = `${petInfo.name}是一只安静温顺的${petInfo.breed}，性格温和，喜欢安静的环境。`
    } else {
      personality = '平衡型'
      description = `${petInfo.name}是一只性格平衡的${petInfo.breed}，既有活泼的一面，也有安静的时候。`
    }
    
    this.setData({
      showResult: true,
      personalityResult: description
    })
    this.updateProgress()
  },

  // 纪念馆描述输入
  onDescriptionInput(e) {
    this.setData({
      'memorialInfo.description': e.detail.value
    })
  },

  // 创建纪念馆
  async createMemorial() {
    const { petInfo, memorialInfo, personalityResult, answers } = this.data
    
    if (!memorialInfo.description.trim()) {
      wx.showToast({
        title: '请输入纪念馆描述',
        icon: 'none'
      })
      return
    }
    
    this.setData({
      loading: true
    })
    
    console.log('开始创建纪念馆，宠物信息:', petInfo)
    
    try {
      // 1. 先创建纪念馆
      const res = await app.request({
        url: '/api/memorial/create',
        method: 'POST',
        data: {
          pet_name: petInfo.name,
          species: petInfo.species || petInfo.breed, // 使用新的 species 字段
          breed: petInfo.breed || '',
          color: petInfo.color || '',
          gender: petInfo.gender || '',
          birth_date: petInfo.birthDate || '',
          memorial_date: petInfo.memorialDate || '',
          weight: parseFloat(petInfo.weight) || 0.0,
          status: petInfo.status || 'alive',
          address: petInfo.address || '',
          description: memorialInfo.description,
          personality: personalityResult,
          personality_answers: answers // 传递性格测试答案
        }
      })
      
      console.log('创建纪念馆响应:', res)
      
      if (res.success) {
        // 2. 如果有照片，上传照片
        if (petInfo.photos && petInfo.photos.length > 0) {
          console.log('开始上传照片，共', petInfo.photos.length, '张')
          await this.uploadPhotos(res.memorial_id, petInfo.photos)
        }
        
        wx.showToast({
          title: '纪念馆创建成功',
          icon: 'success'
        })
        
        // 等待一段时间后跳转
        setTimeout(() => {
          // 确保登录状态存在
          if (app.globalData.sessionToken) {
            wx.reLaunch({
              url: '/pages/memorials/memorials'
            })
          } else {
            wx.reLaunch({
              url: '/pages/login/login'
            })
          }
        }, 1500)
      } else {
        wx.showToast({
          title: res.message || '创建失败',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('创建纪念馆失败:', error)
      wx.showToast({
        title: error.message || '创建失败',
        icon: 'none'
      })
    } finally {
      this.setData({
        loading: false
      })
    }
  },

  // 上传照片到纪念馆
  async uploadPhotos(memorialId, photos) {
    try {
      for (let i = 0; i < photos.length; i++) {
        const photo = photos[i]
        console.log(`上传第 ${i + 1}/${photos.length} 张照片:`, photo)
        
        await new Promise((resolve, reject) => {
          wx.uploadFile({
            url: `${app.globalData.baseUrl}/api/memorial/upload-photos/${memorialId}`,
            filePath: photo,
            name: 'photos',
            header: {
              'x-session-token': app.globalData.sessionToken
            },
            success: (res) => {
              console.log(`照片 ${i + 1} 上传成功:`, res)
              resolve(res)
            },
            fail: (err) => {
              console.error(`照片 ${i + 1} 上传失败:`, err)
              reject(err)
            }
          })
        })
      }
      console.log('所有照片上传完成')
    } catch (error) {
      console.error('上传照片出错:', error)
      // 不阻止纪念馆创建，只记录错误
    }
  }
})