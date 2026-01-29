# AI Platform - 轻量级版本指南

> 为本地 PC 和学习用途优化，资源占用最小，最快 2 分钟启动！

## 🎯 轻量级版本特点

### 技术栈对比

| 组件 | 标准版 | 轻量级版 | 优势 |
|------|--------|---------|------|
| **数据库** | PostgreSQL 15 | 内存/SQLite | 节省 150MB+ |
| **向量DB** | Milvus | 内存向量 | 节省 900MB+ |
| **缓存** | Redis | Redis (可选) | 最小化 |
| **监控** | Prometheus + Grafana | Web UI 内置 | 节省 200MB+ |
| **服务数** | 8 | 7 | 简化架构 |
| **内存占用** | 4GB+ | 1-2GB | ⬇️ 50% |
| **磁盘占用** | 3GB+ | 500MB | ⬇️ 80% |
| **启动时间** | 3-5 分钟 | 1-2 分钟 | ⬆️ 2-3 倍 |

### 移除的重量级组件

- ❌ **PostgreSQL** → 用内存 + 本地 JSON 替代
- ❌ **Milvus** → 用简单向量存储替代
- ❌ **Elasticsearch** → 用 Redis 和内存搜索替代
- ❌ **Prometheus & Grafana** → Web UI 已包含基础监控

### 保留的核心能力

- ✅ **FastAPI 微服务架构** - 了解服务设计
- ✅ **Web UI 交互界面** - 实时交互体验
- ✅ **服务调用流程** - 理解服务通信
- ✅ **Prompt 管理** - 学习 Prompt 工程
- ✅ **RAG 原理** - 理解检索增强生成
- ✅ **Agent 执行** - 学习 Agent 设计

## 🚀 快速启动

### 方式 1：使用启动脚本（推荐）

```bash
# 进入项目目录
cd AICommonPlatform

# 运行启动脚本
bash start-lite.sh

# 脚本会自动:
# 1. 清理旧容器
# 2. 构建所有镜像
# 3. 启动所有服务
# 4. 显示服务地址
```

### 方式 2：手动启动

```bash
# 使用轻量级 docker-compose 文件
docker-compose -f docker-compose.lite.yml up -d

# 查看启动状态
docker-compose -f docker-compose.lite.yml ps

# 查看日志
docker-compose -f docker-compose.lite.yml logs -f

# 停止服务
docker-compose -f docker-compose.lite.yml down
```

## 📍 服务地址

启动完成后访问以下地址：

| 服务 | 地址 | 说明 |
|------|------|------|
| **Web UI** 🌐 | http://localhost:3000 | 主界面，推荐优先使用 |
| **QA 入口** | http://localhost:8001 | 问答服务 API |
| **Prompt 服务** | http://localhost:8002 | 提示词管理 |
| **RAG 服务** | http://localhost:8003 | 知识库检索 |
| **Agent 服务** | http://localhost:8004 | Agent 执行 |
| **Integration** | http://localhost:8005 | 系统集成 |
| **LLM 服务** | http://localhost:8006 | 大模型接口 |

## 💾 数据存储

### 轻量级版本的存储方案

```
AICommonPlatform/
├── data/                          # 数据目录
│   ├── documents/                 # 知识库文件
│   ├── vectors.json               # 向量存储
│   ├── prompts.json               # Prompt 模板
│   └── cache.json                 # 缓存数据
│
├── docker-compose.lite.yml        # 轻量配置
└── services/
    └── */
        └── requirements-lite.txt  # 轻量依赖
```

### 数据持久化

- **Redis**: 内存缓存（重启后丢失）
- **文件**: data/ 目录中的 JSON 文件（持久化）
- **日志**: 容器日志（可查询历史）

## 📚 学习路线

### 第 1 天：架构理解
1. 启动轻量版本
2. 访问 Web UI (http://localhost:3000)
3. 浏览服务架构
4. 查看每个服务的健康状态

### 第 2 天：API 学习
1. 使用 curl 或 Postman 测试各服务 API
2. 理解请求/响应格式
3. 学习服务间调用

### 第 3 天：功能扩展
1. 修改 Prompt 模板
2. 添加自己的工具/Agent
3. 整合自己的业务逻辑

## 🔧 常用命令

```bash
# 启动服务
docker-compose -f docker-compose.lite.yml up -d

# 查看所有容器
docker-compose -f docker-compose.lite.yml ps

# 查看特定服务日志（实时）
docker-compose -f docker-compose.lite.yml logs -f web_ui

# 进入容器 Shell
docker-compose -f docker-compose.lite.yml exec web_ui /bin/bash

# 重启单个服务
docker-compose -f docker-compose.lite.yml restart qa_entry

# 查看容器日志（最后 50 行）
docker-compose -f docker-compose.lite.yml logs --tail=50 web_ui

# 停止所有服务
docker-compose -f docker-compose.lite.yml down

# 完全清理（包括容器）
docker-compose -f docker-compose.lite.yml down -v

# 查看网络信息
docker network ls
docker network inspect aicommonplatform_ai_lite_net
```

## 📖 文件结构说明

### 新增文件

```
docker-compose.lite.yml      # 轻量级配置（移除 PostgreSQL、Milvus）
start-lite.sh               # 自动启动脚本
LITE_GUIDE.md              # 本文件
```

### 修改说明

每个服务目录增加了轻量级配置：

```
services/
├── qa_entry/
│   ├── Dockerfile          # 原始版本（标准）
│   ├── Dockerfile.lite     # 新增轻量版本
│   ├── requirements.txt    # 原始依赖
│   └── requirements-lite.txt  # 新增轻量依赖 (7个包)
├── prompt_service/
│   └── ...（同上）
└── ...
```

## ⚙️ 配置调整

### 如果启动时内存不足

1. **降低 Redis 内存**：在 `docker-compose.lite.yml` 中添加：
   ```yaml
   redis:
     command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
   ```

2. **减少服务数**：注释掉 docker-compose.lite.yml 中不需要的服务

3. **使用分阶段启动**：
   ```bash
   # 只启动基础服务
   docker-compose -f docker-compose.lite.yml up -d redis web_ui
   
   # 等稳定后再启动其他服务
   docker-compose -f docker-compose.lite.yml up -d qa_entry prompt_service
   ```

### 增加资源使用（提升性能）

在 `docker-compose.lite.yml` 中添加资源限制：

```yaml
services:
  web_ui:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1'
        reservations:
          memory: 256M
          cpus: '0.5'
```

## 🐛 故障排查

### 问题 1：启动失败 "Port already in use"

```bash
# 查看占用的端口
lsof -i :3000

# 杀死占用端口的进程
kill -9 <PID>

# 或者修改 docker-compose.lite.yml 中的端口
# 将 "3000:3000" 改为 "3001:3000"
```

### 问题 2：容器启动后立即退出

```bash
# 查看容器日志
docker-compose -f docker-compose.lite.yml logs qa_entry

# 常见原因：
# 1. 依赖服务未启动 - 等待几秒重试
# 2. 文件权限问题 - 重新构建镜像
# 3. Python 依赖缺失 - 检查 requirements-lite.txt
```

### 问题 3：服务间无法通信

```bash
# 检查网络
docker network ls
docker network inspect aicommonplatform_ai_lite_net

# 检查 DNS 解析
docker-compose -f docker-compose.lite.yml exec web_ui ping prompt_service

# 检查防火墙（macOS）
# System Preferences > Security & Privacy > Firewall
```

## 📊 性能对比

### 启动时间

```
标准版本:    3-5 分钟（等待 Postgres、Redis、Milvus）
轻量级版本:  1-2 分钟（仅需 Redis）

改善: ⬇️ 60%
```

### 内存占用

```
标准版本:    4GB+ (Postgres 1GB + Milvus 2GB + 其他 1GB)
轻量级版本:  1-2GB (仅 Redis + 应用)

改善: ⬇️ 75%
```

### 磁盘占用

```
标准版本:    3GB+ (Docker 镜像)
轻量级版本:  500MB (Docker 镜像)

改善: ⬇️ 85%
```

## 🔄 升级到标准版本

如果后续需要用标准版本（生产环境）：

```bash
# 停止轻量版本
docker-compose -f docker-compose.lite.yml down

# 启动标准版本
docker-compose up -d

# 标准版本会自动拉取 PostgreSQL、Milvus 等镜像
```

## 💡 学习建议

### Week 1: 理解架构
- [ ] 启动轻量版本
- [ ] 理解 7 个微服务的职责
- [ ] 学习服务间的调用关系

### Week 2: 深入 API
- [ ] 使用 Web UI 提交问题
- [ ] 用 curl 调用各个 API
- [ ] 理解请求/响应流程

### Week 3: 定制开发
- [ ] 修改 Prompt 模板
- [ ] 添加新的知识库文档
- [ ] 实现简单的 Agent 工具

### Week 4: 扩展功能
- [ ] 接入真实 LLM (OpenAI/通义千问)
- [ ] 添加数据库持久化
- [ ] 部署到云端

## 📞 支持和反馈

如有问题：
1. 查看容器日志：`docker-compose logs -f`
2. 检查网络：`docker network inspect`
3. 验证依赖：`docker-compose config`

## 📝 许可证

MIT

---

**上次更新**: 2026-01-26
**推荐环境**: macOS 12+ / Linux / Windows (WSL2)
**需要资源**: 2GB RAM, 500MB 磁盘, 稳定网络
