-- 查看所有表
.tables

-- 查看用户表结构和数据
.schema users
SELECT '=== 用户数据 ===' as info;
SELECT id, email, user_level, email_verified, created_at FROM users LIMIT 10;

-- 查看用户等级表
.schema user_levels
SELECT '=== 用户等级配置 ===' as info;
SELECT * FROM user_levels;

-- 查看纪念馆表
.schema memorials
SELECT '=== 纪念馆统计 ===' as info;
SELECT COUNT(*) as total_memorials FROM memorials;

-- 查看照片相关表
SELECT '=== 照片表检查 ===' as info;
SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%photo%';

-- 如果 memorial_photos 表存在
.schema memorial_photos
SELECT '=== memorial_photos 表数据 ===' as info;
SELECT COUNT(*) as total_photos FROM memorial_photos;

-- 查看用户会话
.schema user_sessions
SELECT '=== 活跃会话 ===' as info;
SELECT COUNT(*) as active_sessions FROM user_sessions WHERE expires_at > datetime('now');

-- 查看用户纪念馆关联
.schema user_memorials
SELECT '=== 用户纪念馆关联 ===' as info;
SELECT user_id, COUNT(*) as memorial_count 
FROM user_memorials 
GROUP BY user_id;



