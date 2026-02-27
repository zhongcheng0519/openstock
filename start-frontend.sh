#!/bin/bash

# 股票分析系统前端启动脚本

set -e

echo "🚀 启动 OpenStock 前端服务..."

cd "$(dirname "$0")/frontend"

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖..."
    npm install
fi

# 启动开发服务器
echo "✅ 启动 Vue 开发服务器..."
echo "🌐 访问地址: http://localhost:5172"
npm run dev
