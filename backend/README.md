# 后端接口文档

> **重要变动说明**  
> - 用户模型已合并为单一 `UserModel`，`usertype` 字段为字符串枚举（'admin'/'teacher'/'student'），部分接口参数仍用数字（0/1/2），请前端与后端确认统一约定。  
> - 部分接口参数、返回结构有调整，详见下方接口说明。  
> - `problemset` 相关接口为测试/实验功能，仅供开发或测试使用，前端请勿在正式页面或生产环境依赖，务必在 UI 明显标注“测试功能”。

---

## 用户类型约定（usertype / login_type）

- 后端模型字段 `usertype` 为字符串枚举：'admin'（管理员）、'teacher'（教师）、'student'（学生）

---

## 1. 注册（批量）
- URL: `/api/register`
- 方法: POST
- 权限: 教师或管理员（`@teacher_required`，管理员也被允许）
- 请求体:
  ```json
  {
    "user_list": [
      {
        "uid": "242029634",
        "username": "star",
        "password": "123456",
        "usertype": "student",
        "school": "清华大学",
        "profession": "计算机科学"
      }
    ]
  }
  ```
- 行为与限制
  - 管理员可注册任意类型
  - 教师只能注册学生
  - 已存在 `uid` 会在 `fail_list` 返回错误
- 响应示例
  ```json
  {
    "success": 3,
    "fail": 1,
    "fail_list": [
      {"user": {...}, "error": "用户 ID 已存在"}
    ]
  }
  ```
- **变动说明**：`usertype` 字段已改为字符串枚举

---

## 2. 登录
- URL: `/api/login`
- 方法: POST
- 权限: 公开
- 请求体:
  ```json
  {
    "uid": "242029634",
    "password": "123456",
    "login_type": "student"
  }
  ```
- 响应
  ```json
  {
    "access_token": "<jwt access token>",
    "refresh_token": "<jwt refresh token>"
  }
  ```
- **变动说明**：`login_type` 字段已改为字符串枚举

---

## 3. 刷新 Token
- URL: `/api/refresh`
- 方法: POST
- 权限: 需提供 refresh token
- 响应
  ```json
  { "access_token": "<new access token>" }
  ```

---

## 4. 修改个人信息
- URL: `/api/modify_info`
- 方法: POST
- 权限: 登录用户
- 请求体:
  ```json
  {
    "username": "newname",
    "password": "oldpassword",
    "new_password": "newpassword",
    "school": "北大",
    "profession": "数学"
  }
  ```
- 响应
  ```json
  { "success": "修改成功" }
  ```

---

## 5. 注销 / 退出登录
- URL: `/api/logout`
- 方法: POST
- 权限: 登录用户
- 行为: 更新 `token_version`，使现有 access token 失效
- 响应
  ```json
  { "success": "注销成功" }
  ```

---

## 6. 批量修改用户信息
- URL: `/api/modify_user`
- 方法: POST
- 权限: 教师或管理员
- 请求体:
  ```json
  {
    "user_list": [
      {
        "id": 12,
        "usertype": "student",
        "username": "newname",
        "school": "新学校",
        "profession": "新专业",
        "password": "resetpassword",
        "course_list": [1,2,3]
      }
    ]
  }
  ```
- 响应
  ```json
  {
    "success": 3,
    "fail": 1,
    "fail_list": [{"id": 9, "error": "目标用户不存在"}]
  }
  ```
- **变动说明**：`usertype` 字段为字符串枚举

---

## 7. 删除用户（批量）
- URL: `/api/delete_user`
- 方法: POST
- 权限: 教师或管理员
- 请求体:
  ```json
  {
    [1, 2, 3]
  }
  ```
- 响应
  ```json
  {
    "fail": 1,
    "fail_list": [{"error":"用户不存在", "id": 1}],
    "success": 1
  }
  ```
- **变动说明**：删除目标从 json 对象改为用户 id 列表

---

## 8. 查询单个用户信息
- URL: `/api/user_info`
- 方法: GET
- 权限: 登录
- 查询参数: `?id=<user_id>`
- 响应
  ```json
  {
    "id": 12,
    "uid": "242029634",
    "usertype": "student",
    "username": "star",
    "timestamp": "2025-08-19 10:00:00",
    "school": "清华大学",
    "profession": "计算机科学",
    "courses": [
      {"id": 1, "name": "高等数学"}
    ]
  }
  ```
- **变动说明**：返回结构包含 `usertype` 字段

---

## 课程相关接口

### 9. 获取用户列表（带过滤与分页）
- URL: `/api/user_list`
- 方法: POST
- 权限: 教师或管理员
- 请求体:
  ```json
  {
    "usertype": "student",
    "uid": "2420",
    "username": "star",
    "school": "清华",
    "profession": "计算机",
    "course_ids": [1,2],
    "page": 1,
    "per_page": 20
  }
  ```
- **变动说明**：`usertype` 字段为字符串枚举

- 响应
  ```json
  {
    "total": 123,
    "page": 1,
    "per_page": 20,
    "users": [ ... ]
  }
  ```

### 10. 新增或修改课程
- URL: `/api/modify_course`
- 方法: POST
- 权限: 教师或管理员（新增仅管理员）
- 请求体:
  ```json
  {
    "course_name": "高等数学",
    "course_description": "课程简介",
    "teacher_ids": ["1", "2"],
    "student_ids": ["3", "4"]
  }
  ```

- **变动说明**：`teachers` 字段改为 `teacher_ids`，传入的参数改为 id 列表，`students` 同理


### 11. 获取课程列表（分页）
- URL: `/api/course_list`
- 方法: GET
- 权限: 登录
- 查询参数: `?id=<user_id>&page=1&per_page=10`
- 响应
  ```json
  {
    "total": 10,
    "pages": 1,
    "page": 1,
    "per_page": 10,
    "items": [
      {
        "id": 1,
        "name": "课程名",
        "description": "简介",
        "timestamp": "时间戳",
        "teachers": [...],
        "student_cnt": 100
      }
    ]
  }
  ```
- **变动说明**：取消了查询参数 `usertype`

### 12. 获取课程详情
- URL: `/api/course_info`
- 方法: GET
- 权限: 登录
- 查询参数: `?id=<course_id>`
- 响应
  ```json
  {
    "course_name": "高等数学",
    "description": "课程简介",
    "teachers": [ ... ],
    "students": [ ... ]
  }
  ```

### 13. 删除课程（批量）
- URL: `/api/delete_course`
- 方法: POST
- 权限: 管理员
- 请求体:
  ```json
  { "courses": [1, 2, 3] }
  ```
- 响应
  ```json
  { "success": 2, "fail": 1, "fail_list": [3] }
  ```

---

## Problemset（题库/题单）接口 — **测试功能，前端请勿用于正式页面**

> ⚠️ **前端注意：以下接口为测试/实验功能**

- `/api/import_legacy_problems` (POST) — 导入传统题目（教师权限）
- `/api/delete_legacy_problems` (POST) — 批量删除（教师权限）
- `/api/modify_problemset` (POST) — 新建/更新题单（教师权限）
- `/api/problemset_info` (GET) — 查询题单信息
- `/api/delete_problemset` (POST) — 删除题单（教师权限）
- `/api/judge_legacy` (POST) — 简易自动判题（仅供测试）

---

## 变动汇总
- 用户模型已合并为单一模型，`usertype` 字段为字符串枚举
- 所有相关接口参数、返回结构已同步调整
- `problemset` 相关接口为测试功能