#!/bin/bash
# 后端环境快速配置脚本（macOS/Linux）

echo "=========================================="
echo "合规审查知识库系统 - 后端环境配置"
echo "=========================================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装 Python 3.8+"
    exit 1
fi

echo "✓ Python 版本: $(python3 --version)"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "正在创建虚拟环境..."
    python3 -m venv venv
    echo "✓ 虚拟环境创建成功"
else
    echo "✓ 虚拟环境已存在"
fi

# 激活虚拟环境
echo "正在激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "正在升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "正在安装项目依赖..."
pip install -r requirements.txt

# 配置环境变量
if [ ! -f ".env" ]; then
    echo "正在创建环境变量文件..."
    cp env.example .env
    echo "✓ 环境变量文件已创建，请编辑 .env 文件配置Ollama等设置"
else
    echo "✓ 环境变量文件已存在"
fi

# 初始化数据库
echo "正在初始化数据库..."
python init_db.py

echo ""
echo "=========================================="
echo "配置完成！"
echo "=========================================="
echo ""
echo "下一步操作："
echo "1. 编辑 .env 文件，配置Ollama模型等设置"
echo "2. 激活虚拟环境: source venv/bin/activate"
echo "3. 启动服务: python run.py"
echo ""

