# 后端接口文档

说明：本文件基于当前后端实现（`app.py`、`api/auth.py`、`api/courses.py`）整理，所有接口前缀均以 `/api` 开始。需要登录的接口使用 Bearer token（access_token）。token 通过 `/api/login` 获得，使用 refresh token 在 `/api/refresh` 刷新。

通用请求头（需要登录的接口）
Authorization: Bearer <access_token>  
Content-Type: application/json

用户类型约定（usertype / login_type）
- 0 = 管理员
- 1 = 教师
- 2 = 学生

---

## 1. 注册（批量 / 单个）
URL: `/api/register`  
方法: `POST`  
权限: 需教师或管理员（代码使用 `@teacher_required`，管理员也被允许）  
说明: 当前路由以批量注册为主，接受字段 `user_list`（数组）。内部使用 `register_user` 可创建单条记录。

请求体（JSON）
```json
{
  "user_list": [
    {
      "uid": 242029634,
      "username": "star",
      "password": "123456",
      "usertype": 2,
      "school": "清华大学",
      "profession": "计算机科学"
    }
  ]
}
```

行为与限制
- 管理员可以注册任意用户类型（0/1/2）。
- 教师只能注册学生（usertype = 2）。
- 若 `uid` 已存在，将在返回的 `fail_list` 中给出错误信息。

成功响应（示例）
```json
{
  "success": 3,
  "fail": 1,
  "fail_list": [
    {"user": {...}, "error": "用户 ID 已存在"}
  ]
}
```

---

## 2. 登录
URL: `/api/login`  
方法: `POST`  
权限: 公开

请求体（JSON）

```json
{
  "uid": 242029634,
  "password": "123456",
  "login_type": 2
}
```
响应（成功）

```json
{
  "access_token": "<jwt access token>",
  "refresh_token": "<jwt refresh token>"
}
```
响应（失败）

```json
{ "error": "用户名或密码错误" }
```

实现要点
- 登录成功后会更新用户的 `token_version`（用于使旧 token 无效）。
- `access_token` 和 `refresh_token` 的 claims 中包含 `login_type`, `uid`, `username`, `token_version`。

---

## 3. 刷新 Token
URL: `/api/refresh`  
方法: `POST`  
权限: 需提供 `refresh_token`（`@jwt_required(refresh=True)`）

响应（成功）
```json
{
  "access_token": "<new access token>"
}
```
---

## 4. 修改个人信息
URL: `/api/modify_info`  
方法: `POST`  
权限: 登录用户（`@login_required`）

请求体（JSON）

```json
{
  "username": "newname",
  "password": "oldpassword",
  "new_password": "newpassword",
  "school": "北大",
  "profession": "数学"
}
```

说明
- 需要提供当前密码 `password` 以验证身份。
- 如果修改密码，会更新 `token_version` 强制重新登录（旧 token 失效）。
- 管理员（usertype=0）不需要 `school` / `profession` 字段（这些字段仅对教师/学生有效）。

成功响应

```json
{ "success": "修改成功" }
```

失败响应

```json
{ "error": "用户不存在或密码错误" }
```
---

## 5. 注销 / 退出登录
URL: `/api/logout`  
方法: `POST`  
权限: 登录用户

行为
- 将用户的 `token_version` 更新为新的 UUID，从而让现有 access token 失效。

响应（成功）

```json
{ "success": "注销成功" }
```

---

## 6. 批量修改用户信息（管理员/教师）
URL: `/api/modify_user`  
方法: `POST`  
权限: 需教师或管理员（`@teacher_required`，内部会根据 `login_type` 限制可修改对象）

请求体（JSON）

```json
{
  "user_list": [
    {
      "id": 12,
      "usertype": 2,
      "username": "newname",
      "school": "新学校",
      "profession": "新专业",
      "password": "resetpassword",
      "course_list": [1,2,3]
    }
  ]
}
```

说明
- 教师只能修改学生（代码检查 `login_type == 1` 时只允许修改 `usertype == 2`）。
- 如果提供 `password` 字段，则视为重置密码，并强制更新 `token_version`。
- 可以为学生/教师绑定课程（通过 course id 列表）。

响应示例

```json
{
  "success": 3,
  "fail": 1,
  "fail_list": [{"id": 9, "error": "目标用户不存在"}]
}
```

---

## 7. 删除用户（批量）
URL: `/api/delete_user`  
方法: `POST`  
权限: 需教师或管理员（`@teacher_required`，内部会根据 `login_type` 限制可修改对象）

请求体（JSON）

```json
{
  "delete_list": [
    {"id": 1, "usertype": 2, "uid": 242029634},
    {"id": 2, "usertype": 1, "uid": 10001}
  ]
}
```

行为
- 教师只能删除学生（代码中有此限制）。
- 管理员可以删除任意用户（代码允许）。

响应示例

```json
{
  "fail": 1, 
  "fail_list": [{"error":" 用户不存在", "uid": 10001}], 
  "success": 1
}
```

---

## 8. 查询单个用户信息
URL: `/api/user_info`  
方法: `GET`  
权限: 登录（`@login_required`）

请求体 / 参数（JSON，例）

```json
{
  "id": 12,
  "usertype": 2
}
```

响应（成功）
用户对象的 `to_dict()` 返回结构。

```python
def to_dict(self):
    return {
        "id": self.id,
        "uid": self.uid,
        "username": self.username,
        "timestamp": self.time_stamp.strftime("%Y-%m-%d %H:%M:%S"),
        'school': self.school,
        "profession": self.profession,
        "courses": [
            {"id": course.id, "name": course.course_name}
            for course in self.courses
        ]
    }
```

失败响应

```json
{ "error": "用户不存在" }
```

---

## 课程相关接口（在 `api/courses.py`）

### 9. 获取用户列表（带过滤与分页）
URL: `/api/user_list`  
方法: `GET`  
权限: 需教师或管理员（`@teacher_required`）

请求体（JSON，示例）

```json
{
  "usertype": 2,
  "uid": "2420",
  "username": "star",
  "school": "清华",
  "profession": "计算机",
  "course_ids": [1,2],
  "page": 1,
  "per_page": 20
}
```

说明
- 支持按 uid、username 模糊匹配。
- 学生可按 school / profession 筛选。
- 可通过 `course_ids` 筛选属于某些课程的用户。
- 返回分页信息和 `users` 数组（每项为 `to_dict()` 结构）。

响应示例

```json
{
  "total": 123,
  "page": 1,
  "per_page": 20,
  "users": [ ... ]
}
```

---

### 10. 新增或修改课程
URL: `/api/modify_course`  
方法: `POST`  
权限: 需教师或管理员（创建新课时只允许管理员：代码中对 `login_type` 做了检查）

参数
- query 参数 `cid`（可选）：存在则为修改，不存在则为新增。
- 请求体（JSON）：

```json
{
  "course_name": "高等数学",
  "course_description": "课程简介",
  "teachers": [1001, 1002],   // teachers 的 uid 列表
  "students": [2001, 2002]    // students 的 uid 列表
}
```

行为要点
- 修改时会校验：若是教师修改，必须是该课程的任一教师之一。
- 创建时只有管理员可创建（`login_type == 0`）。

响应示例
{ "success": "成功修改 1 个课程" } 或 { "success": "成功添加 1 个课程" }

---

### 11. 获取课程列表（分页）
URL: `/api/course_list`  
方法: `GET`  
权限: 登录用户（`@login_required`）

查询参数（示例）
`?id=<user_id>&usertype=<usertype>&page=1&per_page=10`

说明
- 管理员可查看全部课程。
- 教师/学生只返回与当前用户相关的课程（代码通过 join teachers/students 做过滤）。
- 返回字段示例包含 course id、name、description、teachers（数组）、student_cnt 等。

响应示例

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

---

### 12. 获取课程详情
URL: `/api/course_info`  
方法: `GET`  
权限: 登录用户（`@login_required`）

查询参数 / 请求参数
`?id=<course_id>`

响应示例（成功）
```json
{
  "course_name": "高等数学",
  "description": "课程简介",
  "teachers": [ ... ],   // teacher.to_dict()
  "students": [ ... ]    // student.to_dict()
}
```
失败示例

```json
{ "error": "课程不存在" }
```

---

### 13. 删除课程（批量）
URL: `/api/delete_course`  
方法: `POST`  
权限: 管理员（代码使用 `@admin_required`）

请求体（JSON）

```json
{ "courses": [1, 2, 3] }
```

响应示例

```json
{ "success": 2, "fail": 1, "fail_list": [3] }
```
