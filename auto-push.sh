#!/bin/bash
# Hot Search 自动推送脚本 - 每 10 分钟重试，直到成功

cd ~/.openclaw/workspace/skills/hot-search

MAX_ATTEMPTS=36  # 最多重试 36 次（6 小时）
ATTEMPT=1

echo "🚀 Hot Search 自动推送任务启动"
echo "📍 工作目录：$(pwd)"
echo "⏰ 重试间隔：10 分钟"
echo "📊 最大尝试次数：$MAX_ATTEMPTS"
echo ""

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔄 第 $ATTEMPT 次尝试推送 ($(date '+%Y-%m-%d %H:%M:%S'))"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 执行推送
    git push origin main 2>&1 | tee /tmp/hot-search-push-log.txt
    
    # 检查是否成功
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo ""
        echo "✅ 推送成功！"
        echo "📦 已推送到 GitHub: https://github.com/fishsome/hot-search"
        echo ""
        exit 0
    else
        echo ""
        echo "❌ 推送失败，错误信息："
        cat /tmp/hot-search-push-log.txt
        echo ""
        
        if [ $ATTEMPT -lt $MAX_ATTEMPTS ]; then
            echo "⏳ 等待 10 分钟后重试..."
            echo "下次尝试时间：$(date -d '+10 minutes' '+%Y-%m-%d %H:%M:%S')"
            echo ""
            sleep 600  # 等待 600 秒（10 分钟）
        fi
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
done

echo ""
echo "❌ 已达到最大尝试次数 ($MAX_ATTEMPTS)，推送任务终止"
echo "📝 请检查网络连接或手动推送"
exit 1
