# Agent Demo - 可切换业务场景的 AI 助手

> 🎯 求职作品集项目：展示 RAG、工具调用、场景迁移能力的 AI Agent Demo

## 项目简介

这是一个基于 RAG（检索增强生成）技术的 AI 助手应用，支持**旅游助手**和**健身顾问**两个业务场景的自由切换。项目展示了 AI Agent 的核心能力：

- **RAG 检索**：基于 FAISS 向量数据库的语义检索
- **工具调用**：天气查询、BMI 计算等实用工具
- **场景迁移**：一套代码支持多业务场景

## 功能特性

### 🏖️ 旅游助手
- 长沙景点、美食、交通等信息查询
- 天气查询工具调用
- 智能行程推荐

### 💪 健身顾问
- 增肌、减脂、营养等知识问答
- BMI 计算工具调用
- 个性化健身建议

### 🔧 通用功能
- 多轮对话历史记录
- 内部推理步骤展示（RAG 检索、工具调用过程）
- 流式响应输出

## 技术架构

```
┌─────────────────────────────────────────────┐
│                  Streamlit UI               │
├─────────────────────────────────────────────┤
│              主应用 (app.py)                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────────┐ │
│  │场景切换  │  │对话管理  │  │ 工具调度    │ │
│  └─────────┘  └─────────┘  └─────────────┘ │
├─────────────────────────────────────────────┤
│              RAG 核心 (rag.py)               │
│  ┌─────────┐  ┌─────────┐  ┌─────────────┐ │
│  │文档加载  │  │向量检索  │  │ Prompt 构建 │ │
│  └─────────┘  └─────────┘  └─────────────┘ │
├─────────────────────────────────────────────┤
│              工具模块 (tools/)               │
│  ┌─────────┐  ┌─────────┐                  │
│  │天气查询  │  │BMI 计算 │                  │
│  └─────────┘  └─────────┘                  │
├─────────────────────────────────────────────┤
│           知识库 (data/)                     │
│  ┌─────────┐  ┌─────────┐                  │
│  │旅游知识  │  │健身知识  │                  │
│  └─────────┘  └─────────┘                  │
└─────────────────────────────────────────────┘
```

### 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 前端框架 | Streamlit | 快速构建 Web 应用 |
| LLM API | mimo API | 兼容 OpenAI 格式的大模型 API |
| 向量模型 | sentence-transformers | 多语言 Embedding 模型 |
| 向量数据库 | FAISS | 高效向量检索 |
| 工具调用 | 自定义工具 | 天气查询、BMI 计算 |

## 本地运行

### 1. 克隆项目

```bash
git clone https://github.com/yz/agent-demo.git
cd agent-demo
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key
```

### 4. 运行应用

```bash
streamlit run app.py
```

访问 http://localhost:8501 即可使用。

## 部署到 Streamlit Cloud

### 步骤

1. Fork 本仓库到你的 GitHub 账号
2. 访问 [Streamlit Cloud](https://share.streamlit.io)
3. 登录 GitHub 账号
4. 点击 "New app"，选择你 fork 的仓库
5. 设置 Main file path: `app.py`
6. 在 "Advanced settings" 中添加环境变量：
   - `API_BASE_URL`: API 地址
   - `API_KEY`: 你的 API Key
   - `MODEL_NAME`: 模型名称
7. 点击 "Deploy"

### 环境变量说明

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `API_BASE_URL` | API 服务地址 | `https://api.xiaomimimo.com/v1` |
| `API_KEY` | API 密钥 | `your_api_key_here` |
| `MODEL_NAME` | 模型名称 | `xiaomi-token-plan-cn/mimo-v2.5-pro` |

## 项目亮点

### 🎯 展示 AI Agent 核心能力

- **RAG（检索增强生成）**：使用 FAISS 向量数据库实现知识检索，让 AI 回答基于特定领域知识
- **工具调用（Tool Calling）**：通过关键词检测自动触发工具，扩展 AI 能力边界
- **场景迁移**：同一套架构支持不同业务场景，展示系统的可扩展性

### 💼 求职作品集

本项目由求职者使用 **OpenCode + OMO skills** 辅助开发，展示了：

- AI 辅助开发能力
- 全栈开发能力（前端 Streamlit + 后端 Python）
- 系统设计能力（模块化架构、工具注册机制）
- 快速学习和应用新技术的能力

### 🏗️ 工程实践

- 模块化设计：RAG、工具、UI 三层分离
- 环境变量管理：敏感信息不提交到代码仓库
- 缓存优化：使用 Streamlit cache 避免重复计算
- 错误处理：完善的异常处理和用户提示

## 项目结构

```
agent-demo/
├── app.py              # 主应用
├── rag.py              # RAG 核心逻辑
├── requirements.txt    # 依赖列表
├── .env.example        # 环境变量模板
├── .gitignore          # Git 忽略规则
├── README.md           # 项目文档
├── data/
│   ├── tourism.txt     # 旅游知识库
│   └── fitness.txt     # 健身知识库
└── tools/
    ├── __init__.py     # 工具注册
    ├── weather.py      # 天气查询工具
    └── bmi.py          # BMI 计算工具
```

## 联系方式

如有问题或建议，欢迎通过以下方式联系：

- GitHub: [yz](https://github.com/yz)
- Email: your-email@example.com

## License

MIT License
