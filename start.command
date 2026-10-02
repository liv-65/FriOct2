#!/bin/bash
cd "$(dirname "$0")"
# 如果你创建了 secrets.env (云端总结用的密钥), 启动时读取; 没有也能正常使用, 只是不能自动总结
if [ -f secrets.env ]; then set -a; . ./secrets.env; set +a; fi
python3 server.py
