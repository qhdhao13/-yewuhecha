# 合规审查知识库系统 - 后端

## 技术栈

- **框架**: FastAPI
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **向量数据库**: Chroma
- **AI模型**: Ollama (本地部署)
- **文档解析**: PyPDF2, pdfplumber, python-docx

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # 应用入口
│   ├── core/                 # 核心配置
│   │   ├── config.py        # 配置管理
│   │   └── database.py      # 数据库连接
│   ├── models/               # 数据库模型
│   │   ├── regulation.py    # 制度文件模型
│   │   ├── document.py      # 员工文档模型
│   │   ├── review.py        # 审查记录模型
│   │   └── annotation.py    # 标注模型
│   ├── schemas/              # Pydantic模式
│   │   ├── regulation.py
│   │   ├── document.py
│   │   ├── review.py
│   │   └── annotation.py
│   ├── api/                  # API路由
│   │   └── v1/
│   │       ├── regulations.py
│   │       ├── documents.py
│   │       ├── reviews.py
│   │       └── annotations.py
│   └── services/             # 业务逻辑服务
│       ├── document_parser.py  # 文档解析
│       ├── ollama_service.py   # Ollama集成
│       └── review_service.py   # 审查服务
├── data/                     # 数据目录（自动创建）
│   ├── uploads/              # 上传的文件
│   ├── chroma_db/            # 向量数据库
│   └── compliance.db         # SQLite数据库
├── requirements.txt          # Python依赖
├── .env.example             # 环境变量示例
├── run.py                   # 启动脚本
└── init_db.py               # 数据库初始化脚本
```

## 安装和运行

### 方式一：快速设置脚本（推荐）

#### macOS / Linux

```bash
cd backend
chmod +x setup.sh
./setup.sh
```

#### Windows

```bash
cd backend
setup.bat
```

脚本会自动完成：
- 创建虚拟环境
- 安装依赖
- 创建环境变量文件
- 初始化数据库

### 方式二：手动配置

#### 1. 创建虚拟环境（推荐）

```bash
cd backend

# 使用 venv 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

#### 2. 安装依赖

```bash
# 确保虚拟环境已激活（命令行前应显示 (venv)）
pip install -r requirements.txt
```

#### 3. 配置环境变量

复制 `env.example` 为 `.env` 并修改配置：

```bash
cp env.example .env
```

重要配置项：
- `OLLAMA_BASE_URL`: Ollama服务地址（默认：http://localhost:11434）
- `OLLAMA_EMBEDDING_MODEL`: 嵌入模型名称（可选）
- `OLLAMA_LLM_MODEL`: 大语言模型名称（已配置为 deepseek-r1:7b）

#### 4. 初始化数据库

```bash
python init_db.py
```

#### 5. 启动服务

```bash
python run.py
```

或者使用uvicorn直接启动：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，访问：
- API文档: http://localhost:8000/api/docs
- 健康检查: http://localhost:8000/health

## API接口

### 制度文件管理
- `POST /api/v1/regulations/` - 上传制度文件
- `GET /api/v1/regulations/` - 获取制度文件列表
- `GET /api/v1/regulations/{id}` - 获取制度文件详情
- `PUT /api/v1/regulations/{id}` - 更新制度文件信息
- `DELETE /api/v1/regulations/{id}` - 删除制度文件

### 员工文档管理
- `POST /api/v1/documents/` - 上传员工文档
- `GET /api/v1/documents/` - 获取员工文档列表
- `GET /api/v1/documents/{id}` - 获取员工文档详情
- `PUT /api/v1/documents/{id}` - 更新员工文档信息
- `DELETE /api/v1/documents/{id}` - 删除员工文档

### 合规审查
- `POST /api/v1/reviews/` - 创建审查任务
- `GET /api/v1/reviews/` - 获取审查记录列表
- `GET /api/v1/reviews/{id}` - 获取审查记录详情

### 标注管理
- `GET /api/v1/annotations/` - 获取标注列表
- `GET /api/v1/annotations/{id}` - 获取标注详情
- `PUT /api/v1/annotations/{id}` - 更新标注
- `DELETE /api/v1/annotations/{id}` - 删除标注

## 开发说明

### 数据库迁移

目前使用SQLAlchemy的`create_all`方法创建表。生产环境建议使用Alembic进行数据库迁移管理。

### Ollama配置

确保Ollama服务已启动，并且已下载所需的模型：

```bash
# 检查Ollama服务
ollama list

# 如果没有模型，需要先下载
ollama pull llama3
ollama pull nomic-embed-text
```

### 文件存储

上传的文件存储在 `data/uploads/` 目录下，按类型和日期组织。

## 注意事项

1. 开发环境使用SQLite，生产环境建议使用PostgreSQL
2. 确保Ollama服务正常运行
3. 大文件上传需要配置合适的超时时间
4. 向量数据库Chroma会在首次使用时自动创建

