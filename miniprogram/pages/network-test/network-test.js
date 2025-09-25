// pages/network-test/network-test.js
const networkDiagnostic = require('../../utils/network')
const config = require('../../config/config')

Page({
  data: {
    diagnosticResult: null,
    recommendations: [],
    baseUrl: config.baseUrl
  },

  onLoad() {
    console.log('网络诊断页加载')
  },

  // 运行网络诊断
  async runDiagnostic() {
    wx.showLoading({
      title: '诊断中...'
    })

    try {
      const result = await networkDiagnostic.getDiagnosticReport()
      
      this.setData({
        diagnosticResult: result,
        recommendations: result.recommendations
      })

      wx.hideLoading()
      
      if (result.apiTest.success) {
        wx.showToast({
          title: '诊断完成',
          icon: 'success'
        })
      } else {
        wx.showToast({
          title: '发现问题',
          icon: 'none'
        })
      }
    } catch (error) {
      console.error('诊断失败:', error)
      wx.hideLoading()
      wx.showToast({
        title: '诊断失败',
        icon: 'none'
      })
    }
  },

  // 测试特定URL
  async testUrl(url) {
    return new Promise((resolve, reject) => {
      const startTime = Date.now()
      
      wx.request({
        url: url,
        method: 'GET',
        timeout: 5000,
        success: (res) => {
          const responseTime = Date.now() - startTime
          resolve({
            success: true,
            status: res.statusCode,
            responseTime: responseTime
          })
        },
        fail: (error) => {
          reject(error)
        }
      })
    })
  }
})
