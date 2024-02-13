#!/bin/bash

# 尝试获取当前的 Git 提交 ID 的简短哈希值
COMMIT_ID=$(git rev-parse --short HEAD 2>/dev/null)

# 获取当前的日期，格式为 YYYYMMDD
BUILD_DATE=$(date +%Y%m%d)

# 根据是否能够获取到 COMMIT_ID 来设置 IMAGE_TAG
if [ -n "$COMMIT_ID" ]; then
    NEW_IMAGE_TAG="${BUILD_DATE}_${COMMIT_ID}"
else
    NEW_IMAGE_TAG="${BUILD_DATE}"
fi

# 想要更新或添加的环境变量键名
ENV_VAR="IMAGE_TAG"

# 检查.env文件是否存在
if [ -f ".env" ]; then
    # 检查IMAGE_TAG变量是否存在
    if grep -q "${ENV_VAR}=" .env; then
        # 使用Sed来安全地替换.env文件中的IMAGE_TAG值
        sed -i.bak -e "s/^${ENV_VAR}=.*/${ENV_VAR}=${NEW_IMAGE_TAG}/" .env
        echo "Updated ${ENV_VAR} in .env file."
    else
        # 如果IMAGE_TAG不存在，那么添加它
        # 首先确保.env文件以换行符结尾
        tail -c1 .env | read -r _ || echo "" >> .env
        # 然后添加新的IMAGE_TAG
        echo "${ENV_VAR}=${NEW_IMAGE_TAG}" >> .env
        echo "Added ${ENV_VAR} to .env file."
    fi
else
    # 如果.env文件不存在，那么创建一个并添加IMAGE_TAG
    echo "${ENV_VAR}=${NEW_IMAGE_TAG}" > .env
    echo "Created .env file and added ${ENV_VAR}."
fi