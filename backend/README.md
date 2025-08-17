# 后端接口

## 1. 用户注册

### 1.1 单独注册

**URL**: `/api/register`
**方法**: `POST`
**权限**: 需要登录（管理员 / 教师）
**请求体**（JSON）：

```json
{
  "uid": 242029634,
  "username": "star",
  "password": "123456",
  "usertype": 2,
  "school": "清华大学",
  "profession": "计算机科学"
}
```

* `usertype`:

  * 0 = 管理员
  * 1 = 教师
  * 2 = 学生
* 限制：

  * 管理员可以注册任意用户
  * 教师只能注册学生

**响应**:

* 成功

```json
{ "success": "注册成功" }
```

* 失败

```json
{ "error": "用户 ID 已存在" }
```

---

### 1.2 批量注册（Excel 待实现）

**URL**: `/api/multi-register`
**方法**: `POST`
**权限**: 暂无限制
**响应**:

```json
{ "success": "敬请期待" }
```

---

## 2. 登录

**URL**: `/api/login`
**方法**: `POST`
**请求体**（JSON）：

```json
{
  "uid": 242029634,
  "password": "123456",
  "login_type": 2
}
```

**响应**:

* 成功

```json
{
  "access_token": "xxxxx",
  "refresh_token": "xxxxx"
}
```

* 失败

```json
{ "error": "用户名或密码错误" }
```

---

## 3. 刷新 Token

**URL**: `/api/refresh`
**方法**: `POST`
**权限**: 需要 `refresh_token`
**响应**:

```json
{
  "access_token": "xxxxx"
}
```

---

## 4. 修改个人信息

**URL**: `/api/modify_info`
**方法**: `POST`
**权限**: 登录用户
**请求体**（JSON）：

```json
{
  "username": "newname",
  "password": "oldpassword",
  "new_password": "newpassword",
  "school": "北大",
  "profession": "数学"
}
```

**说明**:

* 需要提供旧密码校验
* 如果修改了密码，会强制要求重新登录（token 失效）

**响应**:

```json
{ "success": "修改成功" }
```

---

## 5. 注销 / 退出登录

**URL**: `/api/logout`
**方法**: `POST`
**权限**: 登录用户
**响应**:

```json
{ "success": "注销成功" }
```

---

## 🔑 请求头（需要登录的接口）

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```
