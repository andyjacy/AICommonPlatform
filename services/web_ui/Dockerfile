FROM python:3.11-slim

WORKDIR /app

# 合并 RUN 命令并缓存依赖安装
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 单独复制 requirements 以利用 Docker 层缓存
COPY requirements.txt .
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# 复制应用代码
COPY main.py .
COPY static/ ./static/

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

CMD ["python", "main.py"]

CMD ["python", "main.py"]
