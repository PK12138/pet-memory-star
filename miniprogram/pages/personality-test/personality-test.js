// pages/personality-test/personality-test.js
const app = getApp()

Page({
  data: {
    currentQuestion: 1,
    totalQuestions: 10,
    progress: 0,
    showPetInfo: true,
    showResult: false,
    showMoreInfo: false, // 是否展开更多信息
    showMemoryQuestions: false, // 是否显示简答题环节
    currentMemoryQuestion: 1,
    totalMemoryQuestions: 5,
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
    memoryQuestions: [
      {
        id: 1,
        question: "还记得你们第一次见面吗？",
        placeholder: "描述一下那个特别的时刻：在哪里？ta当时是什么样子？你的第一感觉是什么？",
        hint: "比如：在宠物店的笼子里，ta用水汪汪的大眼睛看着我..."
      },
      {
        id: 2,
        question: "ta有什么让你印象最深刻的习惯或癖好？",
        placeholder: "那些只属于ta的小动作、小习惯...",
        hint: "比如：每次喝水前一定要用爪子拨一拨水碗..."
      },
      {
        id: 3,
        question: "你们之间发生过什么特别温馨或有趣的事？",
        placeholder: "分享一个让你现在想起来还会笑/感动的故事...",
        hint: "比如：有一次我发烧，ta整晚趴在我身边寸步不离..."
      },
      {
        id: 4,
        question: "ta最喜欢做什么事？或者你们最喜欢一起做什么？",
        placeholder: "那些专属于你们的快乐时光...",
        hint: "比如：每天晚上一起窝在沙发上看电视..."
      },
      {
        id: 5,
        question: "如果用一句话总结ta的性格，你会怎么说？",
        placeholder: "用最能代表ta的话，描述ta在你心中的样子...",
        hint: "比如：一个外表高冷内心温柔的小傲娇..."
      }
    ],
    memoryAnswers: {
      1: '',
      2: '',
      3: '',
      4: '',
      5: ''
    },
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
    
    // 精选10个核心性格测试题目 - 覆盖主要性格维度，保持用户耐心
    const localQuestions = {
      1: {
        id: 1,
        question: "清晨醒来后，ta的第一件事通常是：",
        options: [
          "立刻跳到你身上要早安亲亲",
          "伸个懒腰，慢悠悠地开始新的一天",
          "直奔食盆或水碗",
          "安静地趴着，等你主动叫ta"
        ]
      },
      2: {
        id: 2,
        question: "你在家工作/学习时，ta最常做的是：",
        options: [
          "趴在你脚边或腿上，寸步不离",
          "在你视线范围内自己玩，偶尔看看你",
          "完全独立，在房间另一头做自己的事",
          "不断来「打扰」你，要求关注"
        ]
      },
      3: {
        id: 3,
        question: "看到窗外的鸟/虫子时，ta会：",
        options: [
          "发出特殊的「咔咔」声或呜呜声，超级专注",
          "兴奋地拍打窗户，想要抓住",
          "只是看几眼，然后失去兴趣",
          "完全不在意，眼都不瞟一下"
        ]
      },
      4: {
        id: 4,
        question: "你下班回家时，ta的欢迎方式是：",
        options: [
          "在门口疯狂转圈/摇尾巴，激动到快飞起来",
          "温柔地蹭你，发出小声的「欢迎回家」",
          "慢悠悠地走过来瞟一眼，然后继续自己的事",
          "根本不出现，你得主动去找ta"
        ]
      },
      5: {
        id: 5,
        question: "吃饭时间到了，ta的表现是：",
        options: [
          "提前半小时就开始催，喵喵叫/汪汪叫个不停",
          "准时出现在食盆旁，用眼神提醒你",
          "等你叫ta，不催不急",
          "记不住时间，经常要你主动喂"
        ]
      },
      6: {
        id: 6,
        question: "家里来客人时，ta通常会：",
        options: [
          "秒变「社交达人」，主动上前求摸摸",
          "在远处观察，确认安全后才慢慢靠近",
          "直接消失不见，躲到房间/柜子里",
          "完全无视客人，该干嘛干嘛"
        ]
      },
      7: {
        id: 7,
        question: "午后阳光洒进来时，ta最喜欢：",
        options: [
          "找一块阳光地板，摊成「饼」晒太阳",
          "在阳光和阴影之间来回试探温度",
          "完全不在意阳光，喜欢阴凉的地方",
          "在阳光里疯玩，追逐光影"
        ]
      },
      8: {
        id: 8,
        question: "你拿起外出用的包/钥匙时，ta会：",
        options: [
          "立刻警觉，焦虑地跟着你，怕被丢下",
          "跑到门口或窗边，用眼神送你",
          "完全不在意，继续睡觉",
          "开心地以为要带ta出门，兴奋地转圈"
        ]
      },
      9: {
        id: 9,
        question: "深夜你准备睡觉时，ta通常：",
        options: [
          "已经在你床上/旁边占好位置等你了",
          "在房间里做最后的「巡逻」，检查安全",
          "还在客厅玩，精神十足，不想睡",
          "在自己的小窝里睡得正香"
        ]
      },
      10: {
        id: 10,
        question: "当你哭泣或难过时，ta会：",
        options: [
          "立刻察觉，用头蹭你或舔你的脸/手",
          "安静地趴在你身边，默默陪伴",
          "似乎感觉到了，但不太知道怎么办",
          "没有特别反应，继续做自己的事"
        ]
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
    const { currentQuestion, totalQuestions, showPetInfo, showMemoryQuestions, currentMemoryQuestion, totalMemoryQuestions } = this.data
    let progress = 0
    
    if (showPetInfo) {
      // 基本信息：10%
      progress = 10
    } else if (!showMemoryQuestions) {
      // 性格测试：10% + 60%
      progress = 10 + (currentQuestion / totalQuestions) * 60
    } else {
      // 简答题：70% + 30%
      progress = 70 + (currentMemoryQuestion / totalMemoryQuestions) * 30
    }
    
    this.setData({
      progress: Math.round(progress)
    })
  },

  // 检查是否可以继续
  checkCanProceed() {
    const { showPetInfo, petInfo, currentQuestion, answers, showMemoryQuestions } = this.data
    let canProceed = false
    
    if (showPetInfo) {
      // 必填项：宠物姓名、种类、宠物状态、照片
      canProceed = petInfo.name && 
                   petInfo.species && 
                   petInfo.status && 
                   petInfo.photos.length > 0
    } else if (showMemoryQuestions) {
      // 简答题：选填，始终可以继续
      canProceed = true
    } else {
      // 性格测试：必须选择一个选项
      canProceed = answers[currentQuestion] !== undefined
    }
    
    this.setData({
      canProceed
    })
  },

  // 切换更多信息展开/收起
  toggleMoreInfo() {
    this.setData({
      showMoreInfo: !this.data.showMoreInfo
    })
  },

  // 简答题输入
  onMemoryAnswerInput(e) {
    const { currentMemoryQuestion } = this.data
    const value = e.detail.value
    this.setData({
      [`memoryAnswers.${currentMemoryQuestion}`]: value
    })
    this.checkCanProceed()
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
    const { showPetInfo, currentQuestion, totalQuestions, showMemoryQuestions, currentMemoryQuestion, totalMemoryQuestions } = this.data
    
    if (showPetInfo) {
      // 从宠物信息进入性格测试
      this.setData({
        showPetInfo: false
      })
      this.loadQuestionOptions(1)
    } else if (!showMemoryQuestions && currentQuestion < totalQuestions) {
      // 性格测试：进入下一题
      const nextQuestion = currentQuestion + 1
      this.setData({
        currentQuestion: nextQuestion
      })
      this.loadQuestionOptions(nextQuestion)
    } else if (!showMemoryQuestions && currentQuestion === totalQuestions) {
      // 性格测试完成，进入简答题环节
      this.setData({
        showMemoryQuestions: true,
        currentMemoryQuestion: 1,
        currentQuestionData: null  // 清空当前题目数据
      })
      this.updateProgress()
      this.checkCanProceed()
    } else if (showMemoryQuestions && currentMemoryQuestion < totalMemoryQuestions) {
      // 简答题：进入下一题
      this.setData({
        currentMemoryQuestion: currentMemoryQuestion + 1
      })
      this.checkCanProceed()
    } else {
      // 所有测试完成，显示结果
      this.generateResult()
    }
  },

  // 上一步
  prevStep() {
    const { showPetInfo, currentQuestion, showMemoryQuestions, currentMemoryQuestion, totalQuestions } = this.data
    
    if (showPetInfo) {
      // 返回首页
      wx.navigateBack()
    } else if (showMemoryQuestions && currentMemoryQuestion > 1) {
      // 简答题：返回上一题
      this.setData({
        currentMemoryQuestion: currentMemoryQuestion - 1
      })
      this.checkCanProceed()
    } else if (showMemoryQuestions && currentMemoryQuestion === 1) {
      // 从简答题返回性格测试最后一题
      this.setData({
        showMemoryQuestions: false,
        currentQuestion: totalQuestions
      })
      this.loadQuestionOptions(totalQuestions)
    } else if (!showMemoryQuestions && currentQuestion > 1) {
      // 性格测试：返回上一题
      const prevQuestion = currentQuestion - 1
      this.setData({
        currentQuestion: prevQuestion
      })
      this.loadQuestionOptions(prevQuestion)
    } else {
      // 返回宠物信息
      this.setData({
        showPetInfo: true,
        currentQuestionData: null
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
          status: petInfo.status === '已逝世' ? 'passed' : (petInfo.status === '健在' ? 'alive' : 'alive'),
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
        title: error?.message || '创建失败',
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