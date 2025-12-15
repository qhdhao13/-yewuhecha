#!/bin/bash
# 启动脚本 - 自动激活虚拟环境并运行应用

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "错误: 虚拟环境不存在，请先运行 setup.sh 配置环境"
    exit 1
fi

# 检查端口是否被占用
PORT=8000
PID=$(lsof -ti:$PORT)

if [ ! -z "$PID" ]; then
    echo "警告: 端口 $PORT 已被进程 $PID 占用"
    read -p "是否要终止该进程并继续启动? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在终止进程 $PID..."
        kill -9 $PID
        sleep 1
        echo "进程已终止"
    else
        echo "启动已取消"
        exit 1
    fi
fi

# 激活虚拟环境并运行程序
echo "正在启动应用..."
source venv/bin/activate
python run.py
