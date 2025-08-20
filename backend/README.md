# 后端接口文档

> **重要变动说明**  
> - 用户模型已合并为单一 `UserModel`，`usertype` 字段为字符串枚举（'admin'/'teacher'/'student'）。
> - 部分接口参数、返回结构有调整，详见下方接口说明。  
> - `problemsets`, `legacy_problems`, `coding_problems` 相关接口都已经稳定。

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

## Problemsets 相关接口（`api/problemsets.py`）

### 1. 查询所有题单（分页/筛选）
- URL: `/api/problemsets/`
- 方法: GET
- 权限: 登录用户
- 查询参数（可选）:
  - `page`: 页码（默认 1）
  - `per_page`: 每页数量（默认 20）
  - 其他筛选字段（如课程 id、标题等，视后端实现而定）
- 响应示例
  ```json
  {
    "total": 100,
    "page": 1,
    "per_page": 20,
    "problemsets": [
      {
        "id": 1,
        "title": "期中测试",
        "description": "期中考试题单",
        "course": {
          "id": 1,
          "title": "我是标题"
        },
        "timestamp": "2025-08-20 10:00:00",
        "num_legacy_problems": 1,
        "num_coding_problems": 2,
      }
    ]
  }
  ```

### 2. 查询单个题单详情
- URL: `/api/problemsets/<id>`
- 方法: GET
- 权限: 登录用户
- 路径参数
  - `id`: 题单 id
- 响应示例
  ```json
  {
    "id": 1,
    "title": "期中测试",
    "description": "期中考试题单",
    "timestamp": "2025-08-20 10:00:00",
    "course": {
      "id": 1,
      "title": "我是课程标题"
    },
    "legacy_problems": [
      {"id": 101, "title": "选择题1", "status": "AC", "score": 100.0}
    ],
    "coding_problems": [
      {"id": 201, "title": "编程题1", "status": "CE", "score": 0.0}
    ]
  }
  ```

### 3. 新建题单
- URL: `/api/problemsets`
- 方法: POST
- 权限: 教师或管理员
- 请求体
  ```json
  {
    "title": "期中测试",
    "description": "期中考试题单",
    "course_id": 2,
    "legacy_problem_ids": [101, 102],
    "coding_problem_ids": [201]
  }
  ```
- 响应示例
  ```json
  {
    "id": 1,
    "legacy": 2,
    "coding": 1
  }
  ```

### 4. 更新题单
- URL: `/api/problemsets/<id>`
- 方法: PUT
- 权限: 教师或管理员
- 路径参数
  - `id`: 题单 id
- 请求体
  ```json
  {
    "title": "期中测试（更新）",
    "description": "期中考试题单（更新）",
    "course_id": 2,
    "legacy_problem_ids": [101, 103],
    "coding_problem_ids": [201, 202]
  }
  ```
- 响应示例
  ```json
  {
    "id": 1,
    "legacy": 2,
    "coding": 2
  }
  ```

### 5. 删除题单
- URL: `/api/problemsets/`
- 方法: DELETE
- 权限: 教师或管理员
- 请求体
  ```json
  {
    "ids": [1, 2, 3, 4]
  }
  ```
- 响应示例
  ```json
  {
    "deleted": 3,
    "failed": [
      {"id": 1, "error": "ProblemSet not found"}
    ]
  }
  ```

---

## Legacy Problems 相关接口（`api/legacy_problems.py`）

### 1. 查询所有传统题目（分页/筛选）
<!-- TODO 这里改一下再提交 -->
- URL: `/api/legacy_problems/`
- 方法: GET
- 权限: 登录用户
- 查询参数（可选）:
  - `page`: 页码
  - `per_page`: 每页数量
  - 其他筛选字段（如类型、标题等）
- 响应示例
  ```json
  {
    "total": 50,
    "page": 1,
    "per_page": 20,
    "items": [
      {
        "id": 101,
        "problem_type": "single",
        "title": "选择题1",
        "description": "题目描述",
        "options": ["A", "B", "C", "D"],
        "answers": ["A"],
        "timestamp": "2025-08-20 10:00:00"
      }
    ]
  }
  ```

### 2. 查询单个题目详情
- URL: `/api/legacy_problems/<id>`
- 方法: GET
- 权限: 登录用户
- 路径参数
  - `id`: 题目 id
- 响应示例
  ```json
  {
    "id": 101,
    "problem_type": "single",
    "title": "选择题1",
    "description": "题目描述",
    "options": ["A", "B", "C", "D"],
    "timestamp": "2025-08-20 10:00:00"
  }
  ```

### 3. 新建传统题目
- URL: `/api/legacy_problems/import`
- 方法: POST
- 权限: 教师或管理员
- 请求体
  ```json
  {
    "problem_list": [
      {
        "problem_type": "single",
        "title": "选择题1",
        "description": "题目描述",
        "options": ["A", "B", "C", "D"],
        "answers": ["A"]
      }, 
      {
        "problem_type": "multiple",
        "title": "选择题2",
        "description": "题目描述",
        "options": ["A", "B", "C", "D"],
        "answers": ["A", "C"]
      }
    ]
  }
  ```
- 响应示例
  ```json
  {
    "success": true
  }
  ```

### 4. 更新传统题目
- URL: `/api/legacy_problems/<id>`
- 方法: PUT
- 权限: 教师或管理员
- 路径参数
  - `id`: 题目 id
- 请求体
  ```json
  {
    "title": "选择题1（更新）",
    "description": "题目描述（更新）",
    "options": ["A", "B", "C", "D"],
    "answers": ["B"]
  }
  ```
- 响应示例
  ```json
  {
    "success": true
  }
  ```

### 5. 删除传统题目
- URL: `/api/legacy_problems/`
- 方法: DELETE
- 权限: 教师或管理员
- 请求体
  ```json
  {
    "problem_id_list": [1, 2, 3]
  }
  ```
- 响应示例
  ```json
  {
    "success": false,
    "results": [
      {"id": 1, "status": "success"},
      {"id": 2, "status": "fail", "error": "Problem not found"}
      {"id": 3, "status": "success"}
    ]
  }
  ```

---

## Coding Problems 相关接口（`api/coding_problems.py`）

### 1. 新建编程题

* URL: `/api/coding_problems/`
* 方法: POST
* 权限: 教师或管理员
* 请求体（`multipart/form-data`）

  * 字段

    * `meta`: JSON 字符串，题目信息

      ```json
      {
        "title": "两数之和",
        "description": "给定一个整数数组和目标值，返回两数之和的下标。",
        "limitations": {
          "maxTime": 1.0,
          "maxMemory": 524288,
          "maxStack": 128,
          "maxOutput": 10
        }
      }
      ```
    * `test_cases.zip`: 压缩包文件，包含测试用例
* 响应示例

  ```json
  {
    "success": "Problem created successfully",
    "id": 1
  }
  ```
* **说明:** 后端会递归一层检查 test_cases.zip 中所有的文件名能匹配的 `.in` 和 `.out` 文件存入测试数据，重名覆盖，无效的删除。

---

### 2. 删除编程题（批量）

* URL: `/api/coding_problems/`
* 方法: DELETE
* 权限: 教师或管理员
* 请求体

  ```json
  {
    "pids": [1, 2, 3]
  }
  ```
* 响应示例（部分成功返回 207）

  ```json
  {
    "success": false,
    "results": [
      {"id": 1, "status": "success"},
      {"id": 2, "status": "success", "error": "Problem not found"},
      {"id": 3, "status": "success"}
    ]
  }
  ```

---

### 3. 更新编程题

* URL: `/api/coding_problems/<pid>`
* 方法: PUT
* 权限: 教师或管理员
* 路径参数

  * `pid`: 题目 id
* 请求体（`multipart/form-data`）

  * `meta`: JSON 字符串，同上

  * `test_cases.zip`: （可选）新的测试用例压缩包
* 响应示例

  ```json
  {
    "success": "Problem updated successfully"
  }
  ```

* **说明:** 测试用例和旧的取并，新的重名测试数据会覆盖旧的。
---

### 4. 查询单个编程题

* URL: `/api/coding_problems/<pid>`
* 方法: GET
* 权限: 学生 / 教师 / 管理员
* 路径参数

  * `pid`: 题目 id
* 响应示例

  ```json
  {
    "id": 1,
    "title": "两数之和",
    "description": "给定一个整数数组和目标值，返回两数之和的下标。",
    "limitations": {"maxTime": 1, "maxStack": 128, "maxMemory": 524288, "maxOutput": 10},
    "test_cases": {
      {
        "cases": [
          {
            "in": "data/3/2.in",
            "out": "data/3/2.out",
            "name": "2"
          },
          {
            "in": "data/3/6.in",
            "out": "data/3/6.out",
            "name": "6"
          },
          {
            "in": "data/3/7.in",
            "out": "data/3/7.out",
            "name": "7"
          },
          {
            "in": "data/3/3.in",
            "out": "data/3/3.out",
            "name": "3"
          },
          {
            "in": "data/3/4.in",
            "out": "data/3/4.out",
            "name": "4"
          },
          {
            "in": "data/3/1.in",
            "out": "data/3/1.out",
            "name": "1"
          },
          {
            "in": "data/3/5.in",
            "out": "data/3/5.out",
            "name": "5"
          }
        ],
        "num_cases": 7
      }
    },
    "timestamp": "2025-08-20 13:00:00"
  }
  ```

---

### 5. 查询编程题列表

* URL: `/api/coding_problems/`
* 方法: GET
* 权限: 学生 / 教师 / 管理员
* 查询参数

  * `problem_set_id` (可选): 指定题单 ID，返回该题单下的题目
* 响应示例

  ```json
  {
    "coding_problems": [
      {
        "id": 1,
        "title": "两数之和",
        "description": "返回数组中两个数的下标。",
        "timestamp": "2025-08-20 13:00:00",
        "num_test_cases": 5
      },
      {
        "id": 2,
        "title": "最长上升子序列",
        "description": "计算 LIS 的长度。",
        "timestamp": "2025-08-19 21:45:00",
        "num_test_cases": 7
      }
    ]
  }
  ```

---

### 6. 批量删除测试用例

* URL: `/api/coding_problems/<pid>/test_cases/delete`
* 方法: PATCH
* 权限: 教师或管理员
* 路径参数

  * `pid`: 题目 id
* 请求体

  ```json
  {
    "cases": [
      {"in": "2 7 11 15\n9", "out": "0 1", "name": "case1"},
      {"in": "3 2 4\n6", "out": "1 2", "name": "case2"}
    ]
  }
  ```
* 响应示例

  ```json
  {
    "success": true,
    "remaining": {
      "num_cases": 3,
      "cases": [
        {"in": "1 2\n3", "out": "0 1", "name": "case3"}
      ]
    }
  }
  ```

---

### 7. 批量添加测试用例

* URL: `/api/coding_problems/<pid>/test_cases/add`
* 方法: PATCH
* 权限: 教师或管理员
* 路径参数

  * `pid`: 题目 id
* 请求体（`multipart/form-data`）

  * `test_cases.zip`: 压缩包文件，包含测试用例
* 响应示例

  ```json
  {
    "success": true,
    "test_cases": {
      "num_cases": 6,
      "cases": [
        {"in": "5 6\n11", "out": "0 1", "name": "new_case"}
      ]
    }
  }
  ```

