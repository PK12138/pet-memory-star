// utils/network.js
// 网络诊断工具

class NetworkDiagnostic {
  constructor() {
    this.baseUrl = require('../config/config').baseUrl
  }

  // 检查网络连接
  async checkConnection() {
    return new Promise((resolve) => {
      wx.getNetworkType({
        success: (res) => {
          resolve({
            connected: res.networkType !== 'none',
            networkType: res.networkType
          })
        },
        fail: () => {
          resolve({
            connected: false,
            networkType: 'unknown'
          })
        }
      })
    })
  }

  // 测试API连接
  async testApiConnection() {
    try {
      const res = await this.pingApi()
      return {
        success: true,
        responseTime: res.responseTime,
        status: res.status
      }
    } catch (error) {
      return {
        success: false,
        error: error.message || error.errMsg || '连接失败'
      }
    }
  }

  // Ping API服务器
  pingApi() {
    return new Promise((resolve, reject) => {
      const startTime = Date.now()
      
      wx.request({
        url: `${this.baseUrl}/api/health`,
        method: 'GET',
        timeout: 5000,
        success: (res) => {
          const responseTime = Date.now() - startTime
          resolve({
            status: res.statusCode,
            responseTime: responseTime,
            data: res.data
          })
        },
        fail: (error) => {
          reject(error)
        }
      })
    })
  }

  // 获取网络诊断报告
  async getDiagnosticReport() {
    const connection = await this.checkConnection()
    const apiTest = await this.testApiConnection()
    
    return {
      timestamp: new Date().toISOString(),
      connection,
      apiTest,
      baseUrl: this.baseUrl,
      recommendations: this.getRecommendations(connection, apiTest)
    }
  }

  // 获取修复建议
  getRecommendations(connection, apiTest) {
    const recommendations = []
    
    if (!connection.connected) {
      recommendations.push('请检查网络连接设置')
      recommendations.push('尝试切换到WiFi或移动数据')
    }
    
    if (!apiTest.success) {
      recommendations.push('服务器可能暂时不可用，请稍后重试')
      recommendations.push('检查服务器地址是否正确')
    }
    
    if (apiTest.success && apiTest.responseTime > 5000) {
      recommendations.push('网络连接较慢，建议检查网络质量')
    }
    
    return recommendations
  }
}

// 创建单例
const networkDiagnostic = new NetworkDiagnostic()

module.exports = networkDiagnostic
