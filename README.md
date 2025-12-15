# 合规审查知识库系统

智能文档对比与标注系统，用于自动识别员工文档与制度文件的不符合项。

## 项目概述

本系统通过AI技术，自动对比员工撰写的文档与知识库中的制度文件，识别不符合制度要求的内容，并进行智能标注，提高合规审查效率。

## 技术架构

### 前端
- **框架**: Vue 3 + TypeScript
- **UI组件库**: Element Plus
- **构建工具**: Vite

### 后端
- **框架**: Python + FastAPI
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **向量数据库**: Chroma
- **AI模型**: Ollama (本地部署，使用 deepseek-r1:7b)

## 快速开始

### 5分钟快速上手

**第一步：启动后端（终端1）**
```bash
cd backend
./start.sh
```
看到 `Application startup complete` 表示启动成功 ✅

**第二步：启动前端（终端2）**
```bash
cd frontend
npm install  # 首次运行需要
npm run dev
```
看到 `Local: http://localhost:5173` 表示启动成功 ✅

**第三步：打开浏览器**
访问：**http://localhost:5173**

**详细说明请查看 [完整使用指南](./使用指南.md)**

## 项目结构

```
业务审查系统/
├── backend/              # 后端服务
│   ├── app/             # 应用代码
│   │   ├── api/        # API路由
│   │   ├── core/       # 核心配置
│   │   ├── models/     # 数据模型
│   │   ├── schemas/    # Pydantic模式
│   │   └── services/   # 业务服务
│   ├── data/           # 数据目录
│   └── requirements.txt
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── api/        # API封装
│   │   ├── views/      # 页面组件
│   │   └── router/     # 路由配置
│   └── package.json
└── 使用指南.md          # 完整使用指南（包含所有说明）
```

## 核心功能

1. **知识库管理**: 上传和管理制度文件
2. **文档上传**: 上传员工撰写的文档
3. **智能对比**: 使用Ollama进行语义对比分析
4. **差异标注**: 自动识别并标注不符合项
5. **结果展示**: 清晰的审查结果和统计信息
6. **系统状态监控**: 实时检查Ollama服务和模型状态

## 前置要求

1. **Python**: 3.8 或更高版本
2. **Node.js**: 16 或更高版本
3. **Ollama**: 已安装并运行
4. **模型**: 已下载 deepseek-r1:7b 模型

```bash
# 检查环境
python --version
node --version
ollama list

# 下载模型（如果未下载）
ollama pull deepseek-r1:7b
```

## 完整文档

**⭐ [完整使用指南](./使用指南.md)** - **推荐阅读，包含所有说明**

使用指南包含以下内容：
- ✅ 环境准备和配置
- ✅ 快速开始指南
- ✅ 详细使用流程
- ✅ 功能详解
- ✅ API接口参考
- ✅ 环境配置说明（虚拟环境、Ollama配置）
- ✅ 功能实现说明
- ✅ 功能更新说明
- ✅ 故障排查指南
- ✅ 最佳实践

## 访问地址

- **前端应用**: http://localhost:5173
- **后端API文档**: http://localhost:8000/api/docs
- **后端ReDoc文档**: http://localhost:8000/api/redoc
- **健康检查**: http://localhost:8000/health
- **系统状态**: http://localhost:8000/api/v1/system/status

## 常见问题

**端口被占用？**
```bash
cd backend
./stop.sh  # 停止旧进程
./start.sh # 重新启动
```

**Ollama未运行？**
```bash
ollama list  # 检查服务
ollama pull deepseek-r1:7b  # 下载模型
```

**详细说明？**
查看 [完整使用指南](./使用指南.md) 中的故障排查章节

## 许可证

MIT License

