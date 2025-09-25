// config/config-local.js
// 本地测试配置文件

module.exports = {
  // 小程序信息
  appId: 'wx9572f66945407446',
  appSecret: 'c4b410be644231ff5635ec960dde38c1',
  
  // 本地测试API地址
  baseUrl: 'http://localhost:8000', // 本地开发服务器
  
  // 微信API地址
  wechatApiUrl: 'https://api.weixin.qq.com',
  
  // 支付配置
  payment: {
    mchId: '',
    apiKey: '',
    notifyUrl: 'http://localhost:8000/api/payment/wechat/notify'
  },
  
  // 文件上传配置
  upload: {
    maxFileSize: 10 * 1024 * 1024, // 10MB
    allowedImageTypes: ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    allowedVideoTypes: ['mp4', 'mov', 'avi']
  },
  
  // 分页配置
  pagination: {
    defaultPageSize: 20,
    maxPageSize: 100
  },
  
  // 缓存配置
  cache: {
    userInfoExpire: 24 * 60 * 60 * 1000, // 24小时
    memorialsExpire: 5 * 60 * 1000, // 5分钟
    photosExpire: 10 * 60 * 1000 // 10分钟
  }
}
