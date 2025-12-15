# 合规审查知识库系统 - 前端

## 技术栈

- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI组件库**: Element Plus
- **路由**: Vue Router
- **状态管理**: Pinia
- **HTTP客户端**: Axios

## 项目结构

```
frontend/
├── src/
│   ├── api/              # API接口封装
│   │   ├── request.ts    # Axios配置
│   │   ├── regulations.ts
│   │   ├── documents.ts
│   │   ├── reviews.ts
│   │   └── annotations.ts
│   ├── views/            # 页面组件
│   │   ├── Regulations.vue   # 制度文件管理
│   │   ├── Documents.vue     # 员工文档管理
│   │   ├── Reviews.vue       # 合规审查
│   │   └── Annotations.vue   # 标注管理
│   ├── router/           # 路由配置
│   │   └── index.ts
│   ├── App.vue           # 根组件
│   └── main.ts           # 入口文件
├── index.html
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## 安装和运行

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 3. 构建生产版本

```bash
npm run build
```

## 功能模块

### 1. 制度文件管理
- 上传制度文件（PDF、Word、TXT、Markdown）
- 制度文件列表展示
- 搜索和筛选
- 查看、编辑、删除制度文件

### 2. 员工文档管理
- 上传员工文档
- 文档列表展示
- 按状态、作者、部门筛选
- 开始审查功能

### 3. 合规审查
- 创建审查任务（选择文档和制度）
- 审查记录列表
- 查看审查详情和结果

### 4. 标注管理
- 标注列表展示
- 按严重程度、状态筛选
- 查看、编辑、删除标注

## 开发说明

### API代理配置

开发环境下，Vite会自动代理 `/api` 请求到后端服务器（http://localhost:8000）。

### 组件说明

- 所有页面组件使用 Element Plus 组件库
- 使用 TypeScript 提供类型安全
- API调用统一封装在 `src/api/` 目录下

## 注意事项

1. 确保后端服务已启动（默认端口 8000）
2. 开发时注意跨域问题，已配置代理
3. 生产环境需要配置正确的API地址

