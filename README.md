# ⬡ EvalForge — 大模型代码生成评测平台

> 一站式评测大语言模型（LLM）的代码生成能力，支持多模型横向对比、实时进度追踪、错误分类分析。

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![SQLite](https://img.shields.io/badge/SQLite-3-lightblue)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📸 功能概览

| 功能 | 说明 |
|------|------|
| 🚀 **评测控制台** | 选择模型 + 题库，一键发起评测，实时进度条展示 |
| 📊 **评测报告** | Pass Rate、Pass@1、平均执行时间、错误类型饼图 |
| 📚 **题库管理** | 支持 HumanEval、LeetCode-Easy、Hot100 等多个题库，可增删题目 |
| 🏆 **模型对比** | 多模型 Pass@1 / Pass Rate / 执行时间 / 错误分布横向对比柱状图 |
| 🔐 **用户鉴权** | JWT 登录注册，首个注册账号自动成为管理员 |
| 🐍 **代码沙盒** | 子进程隔离执行，超时/语法/运行时/断言错误自动分类 |

---

## 🗂️ 项目结构

```
evalforge/
├── main.py              # FastAPI 入口，所有路由
├── auth.py              # JWT 签发/校验，密码 bcrypt hash
├── models.py            # SQLAlchemy ORM + Pydantic 模型
├── runner.py            # 评测调度器（LLM → 沙盒 → 写库）
├── evaluator.py         # 代码沙盒（subprocess 隔离执行）
├── llm_client.py        # OpenAI 兼容 LLM 客户端 + MockLLM
├── metrics.py           # Pass@1、Pass Rate、错误分类计算
├── config.py            # .env 配置加载
├── seed_questions.py    # 基础题库注入脚本（HumanEval 等）
├── seed_hot100.py       # LeetCode Hot100 题库注入脚本（60 道）
├── requirements.txt     # Python 依赖
├── Dockerfile           # 后端容器镜像
├── railway.toml         # Railway 后端部署配置
└── frontend/
    ├── app/
    │   ├── page.tsx         # 评测控制台主页
    │   ├── questions/       # 题库管理页
    │   ├── compare/         # 模型对比页
    │   └── login/           # 登录/注册页
    ├── components/          # 复用组件（进度条、图表、表格等）
    ├── context/             # AuthContext（全局鉴权状态）
    ├── lib/
    │   ├── api.ts           # Axios 封装 + API helpers
    │   └── auth.ts          # localStorage token/user 工具
    ├── next.config.mjs      # 代理配置 + 生产 basePath
    └── railway.toml         # Railway 前端部署配置
```

---

## 🧠 支持的题库

| 题库名 | 题目数 | 说明 |
|--------|--------|------|
| `HumanEval` | 14 道 | 基础算法：排序、递归、字符串、数论 |
| `LeetCode-Easy` | 8 道 | LeetCode 简单题 |
| `字符串处理` | 7 道 | 字符串操作、罗马数字、异位词等 |
| `数据结构` | 4 道 | 集合、交集、矩阵转置等 |
| `Hot100` | 60 道 | **LeetCode Hot 100** 全函数式题目 |

> Hot100 覆盖：哈希、双指针、滑动窗口、二分查找、回溯、动态规划、贪心、栈、堆、图（BFS/DFS/拓扑排序）

---

## ⚙️ 技术栈

**后端**
- [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/) ORM + SQLite
- [Pydantic v2](https://docs.pydantic.dev/) 数据验证
- [python-jose](https://github.com/mpdavis/python-jose) JWT
- [passlib](https://passlib.readthedocs.io/) bcrypt 密码 hash
- subprocess 代码沙盒（硬超时隔离）

**前端**
- [Next.js 14](https://nextjs.org/) App Router
- [TailwindCSS](https://tailwindcss.com/) 深色极客风格
- [Recharts](https://recharts.org/) 数据可视化
- [Axios](https://axios-http.com/) HTTP 客户端

**部署**
- [Railway](https://railway.app/) 容器化部署（后端 Docker + 前端 Nixpacks）

---

## 🚀 本地运行

### 前置条件

- Python 3.11+
- Node.js 18+
- （可选）Groq / OpenAI API Key

### 后端

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 LLM_API_KEY 等

# 3. 启动后端
uvicorn main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)

# 4. 注入题库（首次运行）
python seed_questions.py
python seed_hot100.py
```

### 前端

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

---

## 🔑 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `LLM_API_KEY` | LLM API Key（Groq/OpenAI 等） | 空（使用 MockLLM） |
| `LLM_BASE_URL` | API Base URL | `https://api.openai.com/v1` |
| `LLM_MODEL` | 模型名称 | `gpt-4o-mini` |
| `LLM_TEMPERATURE` | 生成温度 | `0.2` |
| `LLM_TIMEOUT` | LLM 请求超时（秒） | `60.0` |
| `SANDBOX_TIMEOUT` | 代码沙盒超时（秒） | `10.0` |
| `JWT_SECRET` | JWT 签名密钥 | 随机开发默认值 |
| `JWT_EXPIRE_HOURS` | Token 有效期（小时） | `24` |
| `DATABASE_URL` | SQLite 路径 | `sqlite:///./evalforge.db` |

> `LLM_API_KEY` 留空时自动切换为 MockLLM，所有接口仍可正常工作，代码由模拟客户端生成。

---

## 📡 API 文档

启动后端后访问 `http://localhost:8000/docs` 查看完整 Swagger 文档。

主要接口：

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/auth/register` | 注册（首个用户自动成管理员） |
| `POST` | `/auth/login` | 登录，返回 JWT Token |
| `GET` | `/auth/me` | 获取当前用户信息 |
| `POST` | `/tasks` | 创建评测任务（需登录） |
| `GET` | `/tasks` | 任务列表 |
| `GET` | `/tasks/{id}/progress` | 实时评测进度 |
| `GET` | `/api/tasks/{id}/report` | 评测报告 |
| `GET` | `/compare` | 多模型对比数据 |
| `GET` | `/questions` | 题目列表 |
| `POST` | `/questions` | 新增题目（需登录） |

---

## 📊 评测指标说明

| 指标 | 说明 |
|------|------|
| **Pass Rate** | 通过测试用例数 / 总测试用例数 |
| **Pass@1** | 通过的题目数 / 总题目数（一次生成即通过） |
| **Avg Execution Time** | 通过用例的平均沙盒执行时间 |
| **错误分布** | 语法错误 / 运行时错误 / 断言失败 / 执行超时 / 其他 |

---

## 🛠️ 部署到 Railway

详见 [Railway 部署指南](#) 或查看 `railway.toml` 和 `Dockerfile`。

**后端环境变量**（在 Railway Variables 中配置）：
```
LLM_API_KEY=your_key
JWT_SECRET=your_random_secret
DATABASE_URL=sqlite:////data/evalforge.db
```

**前端环境变量**：
```
NODE_ENV=production
BACKEND_URL=https://your-backend.up.railway.app
```

---

## 📄 License

MIT © 2025 YoggyZhangzhen
