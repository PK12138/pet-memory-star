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
      breed: '',
      age: '',
      gender: '',
      genderIndex: 0
    },
    genderOptions: ['公', '母'],
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
    try {
      const res = await app.request({
        url: '/api/personality-questions'
      })
      
      if (res.success) {
        this.setData({
          questions: res.questions,
          totalQuestions: Object.keys(res.questions).length
        })
        this.updateProgress()
      }
    } catch (error) {
      console.error('加载问题失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  // 加载问题选项
  async loadQuestionOptions(questionId) {
    try {
      const res = await app.request({
        url: `/api/personality-options/${questionId}`
      })
      
      if (res.success) {
        this.setData({
          currentQuestionData: this.data.questions[questionId],
          currentQuestionOptions: res.options
        })
        this.updateProgress()
        this.checkCanProceed()
      }
    } catch (error) {
      console.error('加载选项失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
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
      canProceed = petInfo.name && petInfo.breed && petInfo.age && petInfo.gender
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

  // 宠物品种输入
  onPetBreedInput(e) {
    this.setData({
      'petInfo.breed': e.detail.value
    })
    this.checkCanProceed()
  },

  // 宠物年龄输入
  onPetAgeInput(e) {
    this.setData({
      'petInfo.age': e.detail.value
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
    const { petInfo, memorialInfo, personalityResult } = this.data
    
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
    
    try {
      const res = await app.request({
        url: '/api/memorial/create',
        method: 'POST',
        data: {
          pet_name: petInfo.name,
          species: petInfo.breed,
          breed: petInfo.breed,
          age: petInfo.age,
          gender: petInfo.gender,
          description: memorialInfo.description,
          personality: personalityResult
        }
      })
      
      if (res.success) {
        wx.showToast({
          title: '纪念馆创建成功',
          icon: 'success'
        })
        
        setTimeout(() => {
          wx.navigateTo({
            url: '/pages/memorials/memorials'
          })
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
        title: '创建失败',
        icon: 'none'
      })
    } finally {
      this.setData({
        loading: false
      })
    }
  }
})