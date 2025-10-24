// pages/reminder-setup/reminder-setup.js
const app = getApp()

Page({
  data: {
    memorialId: null,
    reminders: [],
    showAddDialog: false,
    reminderTypes: [
      { value: 'birthday', name: '🎂 生日', icon: '🎂' },
      { value: 'memorial', name: '🕯️ 纪念日', icon: '🕯️' },
      { value: 'adoption', name: '🏠 领养日', icon: '🏠' },
      { value: 'custom', name: '✨ 自定义', icon: '✨' }
    ],
    formData: {
      reminderType: '',
      reminderDate: '',
      customName: '',
      customDescription: ''
    },
    showCustomFields: false
  },

  onLoad(options) {
    console.log('提醒设置页加载', options)
    const { id } = options
    if (id) {
      this.setData({
        memorialId: id
      })
      this.loadReminders()
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

  onShow() {
    console.log('提醒设置页显示')
  },

  // 加载提醒列表
  async loadReminders() {
    try {
      wx.showLoading({ title: '加载中...' })
      
      const res = await app.request({
        url: `/api/reminders/${this.data.memorialId}`
      })

      wx.hideLoading()

      if (res.success) {
        this.setData({
          reminders: res.reminders || []
        })
        console.log('提醒列表加载成功:', res.reminders)
      } else {
        throw new Error(res.error || '加载失败')
      }
    } catch (error) {
      wx.hideLoading()
      console.error('加载提醒列表失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  // 选择提醒类型
  selectReminderType(e) {
    const type = e.currentTarget.dataset.type
    const showCustomFields = type === 'custom'
    
    this.setData({
      'formData.reminderType': type,
      showCustomFields
    })
    
    console.log('选择提醒类型:', type)
  },

  // 选择日期
  onDateChange(e) {
    this.setData({
      'formData.reminderDate': e.detail.value
    })
    console.log('选择日期:', e.detail.value)
  },

  // 输入自定义名称
  onCustomNameInput(e) {
    this.setData({
      'formData.customName': e.detail.value
    })
  },

  // 输入自定义描述
  onCustomDescInput(e) {
    this.setData({
      'formData.customDescription': e.detail.value
    })
  },

  // 显示添加对话框
  showAddReminder() {
    this.setData({
      showAddDialog: true,
      formData: {
        reminderType: '',
        reminderDate: '',
        customName: '',
        customDescription: ''
      },
      showCustomFields: false
    })
  },

  // 隐藏添加对话框
  hideAddDialog() {
    this.setData({
      showAddDialog: false
    })
  },

  // 提交提醒
  async submitReminder() {
    const { formData, memorialId } = this.data

    // 验证表单
    if (!formData.reminderType) {
      wx.showToast({
        title: '请选择提醒类型',
        icon: 'none'
      })
      return
    }

    if (!formData.reminderDate) {
      wx.showToast({
        title: '请选择日期',
        icon: 'none'
      })
      return
    }

    if (formData.reminderType === 'custom' && !formData.customName.trim()) {
      wx.showToast({
        title: '请输入自定义名称',
        icon: 'none'
      })
      return
    }

    try {
      wx.showLoading({ title: '添加中...' })

      const requestData = {
        memorial_id: memorialId,
        reminder_type: formData.reminderType,
        reminder_date: formData.reminderDate
      }

      if (formData.reminderType === 'custom') {
        requestData.custom_name = formData.customName.trim()
        requestData.custom_description = formData.customDescription.trim()
      }

      const res = await app.request({
        url: '/api/reminder',
        method: 'POST',
        data: requestData
      })

      wx.hideLoading()

      if (res.success) {
        wx.showToast({
          title: '添加成功',
          icon: 'success'
        })
        this.hideAddDialog()
        this.loadReminders()
      } else {
        throw new Error(res.error || '添加失败')
      }
    } catch (error) {
      wx.hideLoading()
      console.error('添加提醒失败:', error)
      wx.showToast({
        title: error.message || '添加失败',
        icon: 'none'
      })
    }
  },

  // 删除提醒
  deleteReminder(e) {
    const { id, name } = e.currentTarget.dataset
    
    wx.showModal({
      title: '确认删除',
      content: `确定要删除"${name}"提醒吗？`,
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '删除中...' })

            const result = await app.request({
              url: `/api/reminder/${id}`,
              method: 'DELETE'
            })

            wx.hideLoading()

            if (result.success) {
              wx.showToast({
                title: '删除成功',
                icon: 'success'
              })
              this.loadReminders()
            } else {
              throw new Error(result.error || '删除失败')
            }
          } catch (error) {
            wx.hideLoading()
            console.error('删除提醒失败:', error)
            wx.showToast({
              title: '删除失败',
              icon: 'none'
            })
          }
        }
      }
    })
  },

  // 获取提醒类型名称
  getReminderTypeName(type) {
    const typeMap = {
      'birthday': '🎂 生日',
      'memorial': '🕯️ 纪念日',
      'adoption': '🏠 领养日',
      'custom': '✨ 自定义'
    }
    return typeMap[type] || type
  },

  // 格式化日期显示
  formatDate(dateStr) {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}年${month}月${day}日`
  }
})

