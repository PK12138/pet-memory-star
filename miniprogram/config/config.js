// config/config.js
// 小程序配置文件

module.exports = {
  // 小程序信息
  appId: 'wx9572f66945407446',
  appSecret: 'c4b410be644231ff5635ec960dde38c1',
  
  // 后端API地址
  baseUrl: 'https://pettrailstar.cn', // 你的域名
  
  // 微信API地址
  wechatApiUrl: 'https://api.weixin.qq.com',
  
  // 支付配置
  payment: {
    // 微信支付商户号（需要申请）
    mchId: '',
    // 微信支付API密钥（需要申请）
    apiKey: '',
    // 支付回调地址
    notifyUrl: 'https://yourdomain.com/api/payment/wechat/notify'
  },
  
  // 文件上传配置
  upload: {
    // 最大文件大小（字节）
    maxFileSize: 10 * 1024 * 1024, // 10MB
    // 支持的图片格式
    allowedImageTypes: ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    // 支持的视频格式
    allowedVideoTypes: ['mp4', 'mov', 'avi']
  },
  
  // 分页配置
  pagination: {
    // 默认每页数量
    defaultPageSize: 20,
    // 最大每页数量
    maxPageSize: 100
  },
  
  // 缓存配置
  cache: {
    // 用户信息缓存时间（毫秒）
    userInfoExpire: 24 * 60 * 60 * 1000, // 24小时
    // 纪念馆列表缓存时间（毫秒）
    memorialsExpire: 5 * 60 * 1000, // 5分钟
    // 照片列表缓存时间（毫秒）
    photosExpire: 10 * 60 * 1000 // 10分钟
  }
}
