# Makefile for AI Common Platform

.PHONY: help up down restart logs clean test build push

help:
	@echo "AI Common Platform - Makefile"
	@echo ""
	@echo "可用命令:"
	@echo "  make up         启动所有容器"
	@echo "  make down       停止所有容器"
	@echo "  make restart    重启容器"
	@echo "  make logs       查看日志"
	@echo "  make clean      清理数据"
	@echo "  make test       运行测试"
	@echo "  make build      构建镜像"
	@echo "  make ps         显示运行中的容器"
	@echo "  make help       显示帮助信息"

up:
	@echo "启动容器..."
	docker-compose up -d
	@echo "等待服务启动..."
	sleep 10
	@echo "✓ 容器启动完成"
	@echo ""
	@echo "服务地址:"
	@echo "  QA Entry Service: http://localhost:8001"
	@echo "  Prompt Service: http://localhost:8002"
	@echo "  RAG Service: http://localhost:8003"
	@echo "  Agent Service: http://localhost:8004"
	@echo "  Integration Service: http://localhost:8005"
	@echo "  LLM Service: http://localhost:8006"

down:
	@echo "停止容器..."
	docker-compose down
	@echo "✓ 容器已停止"

restart:
	@echo "重启容器..."
	docker-compose restart
	@echo "✓ 容器已重启"

logs:
	docker-compose logs -f

clean:
	@echo "⚠️  这将删除所有数据！"
	@read -p "确认？[y/N] " ans && [ $${ans:-N} = y ] && docker-compose down -v || echo "已取消"

test:
	@echo "运行API测试..."
	python3 scripts/test_api.py

build:
	@echo "构建镜像..."
	docker-compose build

ps:
	docker-compose ps

# 开发相关
dev-qa:
	cd services/qa_entry && python3 -m uvicorn main:app --reload --port 8001

dev-prompt:
	cd services/prompt_service && python3 -m uvicorn main:app --reload --port 8002

dev-rag:
	cd services/rag_service && python3 -m uvicorn main:app --reload --port 8003

dev-agent:
	cd services/agent_service && python3 -m uvicorn main:app --reload --port 8004

dev-integration:
	cd services/integration && python3 -m uvicorn main:app --reload --port 8005

dev-llm:
	cd services/llm_service && python3 -m uvicorn main:app --reload --port 8006
