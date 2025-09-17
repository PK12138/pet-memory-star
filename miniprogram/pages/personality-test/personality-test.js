// pages/personality-test/personality-test.js
const app = getApp()

Page({
  data: {
    currentStep: 1,
    petInfo: {
      name: '',
      breed: '',
      age: ''
    },
    questions: [
      {
        id: 1,
        question: '您的宠物最喜欢什么活动？',
        options: ['睡觉', '玩耍', '散步', '吃东西']
      },
      {
        id: 2,
        question: '您的宠物性格如何？',
        options: ['活泼好动', '安静温顺', '独立自主', '粘人撒娇']
      },
      {
        id: 3,
        question: '您的宠物最喜欢什么食物？',
        options: ['肉类', '蔬菜', '零食', '什么都吃']
      }
    ],
    answers: {},
    personalityResult: '',
    memorialInfo: {
      description: ''
    },
    loading: false
  },

  onLoad() {
    console.log('性格测试页加载')
  },

  // 宠物姓名输入
  onPetNameInput(e) {
    this.setData({
      'petInfo.name': e.detail.value
    })
  },

  // 宠物品种输入
  onPetBreedInput(e) {
    this.setData({
      'petInfo.breed': e.detail.value
    })
  },

  // 宠物年龄输入
  onPetAgeInput(e) {
    this.setData({
      'petInfo.age': e.detail.value
    })
  },

  // 选择答案
  selectAnswer(e) {
    const questionId = e.currentTarget.dataset.questionId
    const option = e.currentTarget.dataset.option
    
    this.setData({
      [`answers.${questionId}`]: option
    })
  },

  // 描述输入
  onDescriptionInput(e) {
    this.setData({
      'memorialInfo.description': e.detail.value
    })
  },

  // 下一步
  nextStep() {
    const { currentStep, petInfo, answers } = this.data
    
    if (currentStep === 1) {
      // 验证基本信息
      if (!petInfo.name) {
        app.showError('请输入宠物姓名')
        return
      }
      if (!petInfo.breed) {
        app.showError('请输入宠物品种')
        return
      }
      if (!petInfo.age) {
        app.showError('请输入宠物年龄')
        return
      }
    } else if (currentStep === 2) {
      // 验证性格测试
      const questionCount = this.data.questions.length
      const answerCount = Object.keys(answers).length
      if (answerCount < questionCount) {
        app.showError('请完成所有性格测试题目')
        return
      }
      
      // 计算性格结果
      this.calculatePersonality()
    }
    
    this.setData({
      currentStep: currentStep + 1
    })
  },

  // 上一步
  prevStep() {
    this.setData({
      currentStep: this.data.currentStep - 1
    })
  },

  // 计算性格结果
  calculatePersonality() {
    const { answers } = this.data
    const results = []
    
    // 简单的性格分析逻辑
    Object.values(answers).forEach(answer => {
      if (answer.includes('活泼') || answer.includes('玩耍')) {
        results.push('活泼开朗')
      } else if (answer.includes('安静') || answer.includes('睡觉')) {
        results.push('安静温顺')
      } else if (answer.includes('独立')) {
        results.push('独立自主')
      } else if (answer.includes('粘人')) {
        results.push('粘人可爱')
      }
    })
    
    // 统计最常见的性格特征
    const personalityCount = {}
    results.forEach(personality => {
      personalityCount[personality] = (personalityCount[personality] || 0) + 1
    })
    
    const mostCommon = Object.keys(personalityCount).reduce((a, b) => 
      personalityCount[a] > personalityCount[b] ? a : b
    )
    
    this.setData({
      personalityResult: `根据测试结果，您的宠物${this.data.petInfo.name}是一个${mostCommon}的小可爱！`
    })
  },

  // 创建纪念馆
  async createMemorial() {
    const { petInfo, memorialInfo, personalityResult } = this.data
    
    if (!memorialInfo.description) {
      app.showError('请输入纪念馆描述')
      return
    }
    
    this.setData({ loading: true })
    app.showLoading('创建纪念馆中...')
    
    try {
      const res = await app.request({
        url: '/api/memorial/create',
        method: 'POST',
        data: {
          pet_name: petInfo.name,
          species: petInfo.breed,
          description: memorialInfo.description,
          personality: personalityResult
        }
      })
      
      if (res.success) {
        app.hideLoading()
        app.showSuccess('纪念馆创建成功')
        
        // 跳转到纪念馆列表
        setTimeout(() => {
          wx.switchTab({
            url: '/pages/memorials/memorials'
          })
        }, 1500)
      } else {
        app.hideLoading()
        app.showError(res.message || '创建纪念馆失败')
      }
    } catch (error) {
      console.error('创建纪念馆失败:', error)
      app.hideLoading()
      app.showError('网络错误，请稍后重试')
    } finally {
      this.setData({ loading: false })
    }
  }
})