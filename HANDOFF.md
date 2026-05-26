# 交接文档 - Agent Demo 项目

## ✅ 已完成

### Wave 1 - 基础文件
- [x] 项目目录结构：`C:\Users\yz\projects\agent-demo\`
- [x] 知识库文件：`data/tourism.txt`（长沙旅游）、`data/fitness.txt`（健身知识）
- [x] 配置文件：`requirements.txt`、`.env.example`、`.gitignore`
- [x] 工具模块：`tools/weather.py`（天气查询）、`tools/bmi.py`（BMI计算）、`tools/__init__.py`（工具注册）

### Wave 2 - 核心逻辑
- [x] RAG 核心逻辑：`rag.py`（文档加载、分块、向量化、FAISS索引、检索、Prompt构建）
- [x] 主应用：`app.py`（Streamlit UI、场景切换、对话历史、RAG集成、工具调用、LLM调用）
- [x] README：`README.md`（项目文档）

### Wave 3 - Git
- [x] Git 仓库初始化
- [x] 代码提交（6个commit）

---

## ⏳ 待完成（需要你操作）

### 1. GitHub 仓库创建和推送

```bash
# 进入项目目录
cd C:\Users\yz\projects\agent-demo

# 登录 GitHub（会打开浏览器）
gh auth login

# 创建公开仓库并推送
gh repo create agent-demo --public --source=. --push --description="可切换业务场景的 AI Agent Demo - 求职作品集"
```

### 2. Streamlit Cloud 部署

1. 访问 https://share.streamlit.io
2. 登录 GitHub 账号
3. 点击 "New app"
4. 选择仓库：`yz/agent-demo`
5. Main file path：`app.py`
6. 点击 "Advanced settings"
7. 添加环境变量：
   - `API_BASE_URL` = `https://api.xiaomimimo.com/v1`
   - `API_KEY` = `你的API密钥`
   - `MODEL_NAME` = `xiaomi-token-plan-cn/mimo-v2.5-pro`
8. 点击 "Deploy!"

### 3. 本地测试（可选）

```bash
cd C:\Users\yz\projects\agent-demo

# 安装依赖
pip install -r requirements.txt

# 创建 .env 文件
cp .env.example .env
# 编辑 .env 填入 API_KEY

# 运行
streamlit run app.py
```

---

## 项目结构

```
agent-demo/
├── app.py              # 主应用（286行）
├── rag.py              # RAG核心（317行）
├── requirements.txt    # 依赖
├── .env.example        # 环境变量模板
├── .gitignore          # Git忽略规则
├── README.md           # 项目文档
├── HANDOFF.md          # 本交接文档
├── data/
│   ├── tourism.txt     # 旅游知识库
│   └── fitness.txt     # 健身知识库
└── tools/
    ├── __init__.py     # 工具注册
    ├── weather.py      # 天气查询
    └── bmi.py          # BMI计算
```

---

## 功能说明

### 支持的场景
- **🏖️ 旅游助手**：长沙景点、美食、交通、天气查询
- **💪 健身顾问**：增肌、减脂、营养、BMI计算

### 核心功能
- RAG 检索：基于 FAISS 的语义搜索
- 工具调用：天气查询、BMI计算
- 对话历史：Streamlit session_state
- 内部步骤展示：可展开查看 RAG 检索和工具调用详情
