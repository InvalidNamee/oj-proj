# 后端接口文档

---
## Auth 相关接口（`api/auth.py`）

### 1. 用户登录

* URL: `/api/auth/login`
* 方法: POST
* 权限: 无需登录
* 请求体

  ```json
  {
    "uid": "2025001",
    "password": "123456",
    "login_type": "student"
  }
  ```
* 响应示例

  ```json
  {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "uid": "2025001",
      "usertype": "student",
      "username": "wangyafei"
    }
  }
  ```
* 错误示例

  ```json
  {
    "error": "用户名或密码错误"
  }
  ```

---

### 2. 刷新 access\_token

* URL: `/api/auth/refresh`
* 方法: POST
* 权限: 需提供有效的 refresh\_token
* 请求头

  ```
  Authorization: Bearer <refresh_token>
  ```
* 响应示例

  ```json
  {
    "access_token": "new_access_token_here"
  }
  ```

---

### 3. 用户注销

* URL: `/api/auth/logout`
* 方法: POST
* 权限: 登录用户
* 请求头

  ```
  Authorization: Bearer <access_token>
  ```
* 响应示例

  ```json
  {
    "success": "注销成功"
  }
  ```
* 错误示例

  ```json
  {
    "error": "用户不存在"
  }
  ```

## Users 相关接口（`api/users.py`）

---

### 1. 批量注册用户

* URL: `/api/users/import`
* 方法: POST
* 权限: 教师或管理员
* 请求体

  ```json
  {
    "user_list": [
      {
        "uid": "2025001",
        "username": "张三",
        "password": "123456",
        "usertype": "student",
        "school": "计算机学院",
        "profession": "软件工程",
        "course_list": [1, 2]
      },
      {
        "uid": "2025002",
        "username": "李四",
        "password": "123456",
        "usertype": "student",
        "school": "计算机学院",
        "profession": "人工智能",
        "course_list": [1]
      }
    ]
  }
  ```
* 响应示例

  ```json
  {
    "success_count": 2,
    "fail_count": 0,
    "results": [
      {"status": "success", "user": {"uid": "2025001", "username": "张三"}},
      {"status": "success", "user": {"uid": "2025002", "username": "李四"}}
    ]
  }
  ```

---

### 2. 单独注册用户

* URL: `/api/users/`
* 方法: POST
* 权限: 教师或管理员
* 请求体

  ```json
  {
    "uid": "admin01",
    "username": "管理员",
    "password": "123456",
    "usertype": "admin",
    "school": "信息工程学院",
    "profession": "计算机科学",
    "course_list": []
  }
  ```
* 响应示例

  ```json
  {
    "status": "success",
    "user": {
      "uid": "admin01",
      "username": "管理员",
      "usertype": "admin"
    }
  }
  ```

---

### 3. 修改当前用户密码

* URL: `/api/users/`
* 方法: PATCH
* 权限: 登录用户
* 请求体

  ```json
  {
    "password": "123456",
    "new_password": "654321"
  }
  ```
* 响应示例

  ```json
  {
    "success": true
  }
  ```
* 错误示例

  ```json
  {
    "error": "Wrong password"
  }
  ```

---

### 4. 批量删除用户

* URL: `/api/users/`
* 方法: DELETE
* 权限: 管理员
* 请求体

  ```json
  {
    "user_ids": [1, 2, 3]
  }
  ```
* 响应示例

  ```json
  {
    "total": 3,
    "success": 2,
    "fail": 1,
    "results": [
      {"id": 1, "status": "success"},
      {"id": 2, "status": "fail", "error": "User not found"},
      {"id": 3, "status": "success"}
    ]
  }
  ```

---

### 5. 查询单个用户

* URL: `/api/users/<user_id>`
* 方法: GET
* 权限: 登录用户
* 路径参数

  * `user_id`: 用户 ID
* 响应示例

  ```json
  {
    "id": 1,
    "uid": "2025001",
    "username": "张三",
    "usertype": "student",
    "school": "计算机学院",
    "profession": "软件工程",
    "courses": [
      {"id": 1, "name": "数据结构"},
      {"id": 2, "name": "操作系统"}
    ]
  }
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

