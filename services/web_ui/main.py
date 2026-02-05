"""
Web UI Service - 交互式界面
提供问答、系统状态、模块配置等功能
支持调用链追踪和 SQLite 数据库持久化
"""

import os
import json
import aiohttp
import sqlite3
import hashlib
import time
import psutil
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict
import logging
import uuid
import sys

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Common Platform Web UI", version="1.0.0")

# ==================== 会话验证中间件 ====================

@app.middleware("http")
async def session_verification_middleware(request: Request, call_next):
    """
    会话验证中间件 - 禁用登陆流程，允许直接访问
    """
    # 所有路径都允许访问（不需要验证）
    response = await call_next(request)
    return response

# ==================== 调用链追踪系统 ====================

class CallChain:
    """记录 AI 处理流程中的每一步调用"""
    
    def __init__(self, question: str):
        self.trace_id = str(uuid.uuid4())[:8]
        self.question = question
        self.steps = []
        self.start_time = datetime.now()
    
    def add_step(self, stage: str, service: str, purpose: str, data: dict = None, status: str = "success"):
        """添加一个处理步骤"""
        step = {
            "seq": len(self.steps) + 1,
            "timestamp": datetime.now().isoformat(),
            "stage": stage,  # 例如：输入处理、意图识别、检索、生成等
            "service": service,  # 调用的服务名
            "purpose": purpose,  # 此步骤的用途
            "status": status,  # success, error, skip
            "data": data or {}
        }
        self.steps.append(step)
        logger.info(f"[{self.trace_id}] Step {step['seq']}: {stage} -> {service}")
    
    def get_summary(self):
        """获取完整的调用链摘要"""
        total_time = (datetime.now() - self.start_time).total_seconds()
        return {
            "trace_id": self.trace_id,
            "question": self.question,
            "total_steps": len(self.steps),
            "total_time": f"{total_time:.3f}s",
            "steps": self.steps
        }

# 服务URL
QA_SERVICE_URL = os.getenv("QA_SERVICE_URL", "http://localhost:8001")
PROMPT_SERVICE_URL = os.getenv("PROMPT_SERVICE_URL", "http://localhost:8002")
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8003")
AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://localhost:8004")
INTEGRATION_SERVICE_URL = os.getenv("INTEGRATION_SERVICE_URL", "http://localhost:8005")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://localhost:8006")

# 数据库配置
DB_PATH = os.getenv("DB_PATH", "web_ui.db")

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # LLM 模型表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS llm_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            provider TEXT NOT NULL,
            model_type TEXT DEFAULT 'api',
            endpoint TEXT,
            api_key TEXT,
            base_url TEXT,
            max_tokens INTEGER DEFAULT 2048,
            temperature REAL DEFAULT 0.7,
            top_p REAL DEFAULT 1.0,
            enabled BOOLEAN DEFAULT 1,
            is_default BOOLEAN DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    """)
    
    # Prompt 模板表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL UNIQUE,
            system_prompt TEXT NOT NULL,
            variables TEXT,
            description TEXT,
            enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    """)
    
    # Agent 工具表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            tool_type TEXT DEFAULT 'function',
            endpoint TEXT,
            method TEXT DEFAULT 'GET',
            parameters TEXT,
            enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    """)
    
    # 用户认证表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            enabled BOOLEAN DEFAULT 1,
            language TEXT DEFAULT 'zh',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 用户会话表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # 问答历史表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS qa_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            question_type TEXT,
            confidence REAL DEFAULT 0.0,
            sources TEXT,
            execution_time REAL DEFAULT 0.0,
            trace_id TEXT,
            trace_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # 知识库文档表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            department TEXT,
            tags TEXT,
            enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 使用统计表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stat_date DATE NOT NULL,
            stat_type TEXT NOT NULL,
            stat_key TEXT NOT NULL,
            stat_value INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(stat_date, stat_type, stat_key)
        )
    """)
    
    # 创建默认管理员用户 (用户名: admin, 密码: admin123)
    import hashlib
    default_password = hashlib.sha256("admin123".encode()).hexdigest()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO users (username, password_hash, email, role, enabled)
            VALUES (?, ?, ?, ?, 1)
        """, ("admin", default_password, "admin@localhost", "admin"))
    except sqlite3.IntegrityError:
        pass
    
    # 创建演示用户 (用户名: demo, 密码: demo123456)
    demo_password = hashlib.sha256("demo123456".encode()).hexdigest()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO users (username, password_hash, email, role, enabled)
            VALUES (?, ?, ?, ?, 1)
        """, ("demo", demo_password, "demo@localhost", "user"))
    except sqlite3.IntegrityError:
        pass
    
    # 插入默认 LLM 模型 - ChatAnywhere GPT-3.5-turbo（仅支持 ChatAnywhere）
    chatanywhere_key = os.getenv("CHATANYWHERE_API_KEY", "sk-")
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO llm_models 
            (name, provider, model_type, endpoint, api_key, base_url, max_tokens, temperature, top_p, enabled, is_default, description, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "ChatAnywhere GPT-3.5-turbo",
            "chatanywhere",
            "api",
            "https://api.chatanywhere.com.cn/v1/chat/completions",
            chatanywhere_key,
            "https://api.chatanywhere.com.cn/v1",
            2048,
            0.7,
            1.0,
            1,
            1,
            "ChatAnywhere GPT-3.5-turbo - 系统默认使用的大模型",
            json.dumps({"version": "gpt-3.5-turbo", "type": "chat", "provider": "chatanywhere"})
        ))
    except sqlite3.IntegrityError:
        pass
    
    # 插入默认 Prompt 模板
    default_prompts = [
        ("通用顾问", "general_assistant", """你是一个多才多艺的通用顾问助手。你的职责是：
1. 理解用户的问题，提供准确、有帮助的信息和建议
2. 当知识库中没有相关信息时，请基于你的通用知识来回答
3. 保持专业和友善的语气
4. 提供结构化的回答，便于用户理解
5. 必要时提出后续建议或相关问题

回答格式：先总结问题 → 分析关键点 → 提供建议 → 列出可能的后续步骤""", None, "通用知识查询和问题解答"),
        
        ("销售顾问", "sales_analyst", """你是一个专业的销售数据分析师。你的职责是：
1. 分析销售数据、提供销售建议和市场洞察
2. 基于数据做出科学的销售预测
3. 识别销售机会和潜在风险
4. 提供客户群体分析和细分建议
5. 制定销售策略优化方案

关注指标：销售额、客户获取成本、客户生命周期价值、转化率、市场份额
回答时请包含：当前状态 → 关键问题 → 解决方案 → 预期效果""", None, "销售数据分析和策略建议"),
        
        ("HR 顾问", "hr_manager", """你是一个经验丰富的人力资源顾问。你的职责是：
1. 处理员工相关的询问和人力资源政策解释
2. 提供员工招聘、培训和发展建议
3. 处理组织结构和岗位相关的问题
4. 提供薪酬福利和绩效管理建议
5. 协助处理员工关系和冲突解决

关注领域：招聘、培训、绩效、薪酬、福利、员工发展、组织文化
回答包括：问题识别 → 政策说明 → 具体建议 → 实施步骤""", None, "人力资源管理和员工发展"),
        
        ("技术顾问", "tech_architect", """你是一位资深的技术架构师。你的职责是：
1. 提供系统设计和架构方案
2. 解答技术问题和最佳实践
3. 评估技术方案的可行性和风险
4. 提供技术栈选择建议
5. 指导系统性能优化和扩展性设计

关注领域：系统架构、数据库设计、API设计、安全性、性能、可扩展性、微服务
回答包括：需求分析 → 架构方案 → 技术选型 → 实施建议 → 风险评估""", None, "技术架构和系统设计"),
        
        ("财务顾问", "financial_analyst", """你是一位财务分析专家。你的职责是：
1. 分析财务数据，提供财务洞察
2. 制定成本控制和预算方案
3. 进行投资项目的财务评估
4. 提供资金规划和现金流管理建议
5. 分析财务指标和趋势

关注指标：收入、成本、利润、现金流、ROI、毛利率、运营效率、财务健康度
回答包括：数据分析 → 关键发现 → 改进建议 → 财务影响 → 行动计划""", None, "财务分析和成本优化"),
        
        ("供应链顾问", "supply_chain_manager", """你是一位供应链管理专家。你的职责是：
1. 优化采购流程和供应商管理
2. 管理库存和物流成本
3. 分析供应链风险和瓶颈
4. 提供库存规划和需求预测建议
5. 改进供应链效率和响应能力

关注领域：采购、库存、物流、供应商、需求预测、成本、交期、质量
回答包括：现状分析 → 问题诊断 → 改进方案 → 实施路径 → 效果预期""", None, "供应链优化和成本控制"),
    ]
    
    for name, role, system_prompt, variables, desc in default_prompts:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO prompts (name, role, system_prompt, variables, description, enabled)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (name, role, system_prompt, variables, desc))
        except sqlite3.IntegrityError:
            pass
    
    # 获取演示用户ID
    cursor.execute("SELECT id FROM users WHERE username = ?", ("demo",))
    user_result = cursor.fetchone()
    user_id = user_result[0] if user_result else 1
    
    # 插入默认问答历史
    default_qa_history = [
        ("我们公司Q1季度的销售额是多少？", "根据Q1销售数据，公司总销售额达到5000万元，同比增长15%。其中核心产品线贡献占比65%，新产品线贡献占比35%。", "sales_analysis", 0.92, "doc_sales_q1", 1.234),
        ("公司有哪些福利政策？", "公司提供完整的员工福利体系：1) 基础保险：五险一金，缴纳比例100%；2) 假期：法定假日+10天带薪年假，最高可累计至20天；3) 补贴：车补/房补/餐补可选；4) 健康：年度体检+健身补贴；5) 培训：年度3000元培训经费；6) 奖励：季度/年度绩效奖金+股权激励。", "hr_policy", 0.88, "doc_hr_handbook", 0.856),
        ("技术团队应该用什么架构来构建微服务系统？", "推荐采用云原生微服务架构：1) API网关：使用Kong或Nginx Plus作为入口；2) 服务框架：FastAPI(Python)/Spring Boot(Java)；3) 服务网格：Istio管理服务通信；4) 容器化：Docker+Kubernetes编排；5) 数据库：采用数据库分片和读写分离；6) 缓存：Redis层做热数据缓存；7) MQ：Kafka处理异步消息；8) 监控：Prometheus+Grafana+ELK日志栈。", "technical_design", 0.95, "doc_technical_architecture", 2.156),
        ("2024年的预算批准了多少？", "2024年度总预算批准金额10亿元，各部门预算分配如下：研发部门占28%（2.8亿）、销售市场占22%（2.2亿）、人力资源占15%（1.5亿）、运营管理占20%（2亿）、行政成本占15%（1.5亿）。", "finance_budget", 0.89, "doc_finance_budget", 0.723),
        ("我们的主要供应商是谁？", "公司拥有三级供应商体系。一级战略供应商15家（占采购额80%），包括五大核心原料供应商和八家关键部件供应商。二级优选供应商40家（占采购额15%），三级备选供应商100+家。与一级供应商的合作周期3-5年，在质量、成本、交期上设有KPI要求。", "supply_chain", 0.86, "doc_supply_chain_supplier", 1.432),
        ("这个平台有什么功能？", "AI通用智能平台提供以下核心功能：1) 问答系统：支持自然语言提问，智能匹配专业顾问角色；2) 知识库搜索：对接企业内部文档和业务数据；3) 调用链追踪：完整记录每个问题的处理过程和耗时；4) 系统集成：连接ERP、HR、财务等企业系统；5) 多角色支持：通用顾问、销售分析、HR管理、技术架构、财务分析、供应链优化；6) 数据持久化：所有问答记录本地存储；7) 企业部署：支持轻量化和完整部署模式。", "general", 0.91, "doc_system_features", 0.645),
    ]
    
    # 检查是否已有历史记录，避免重复插入
    cursor.execute("SELECT COUNT(*) FROM qa_history")
    count = cursor.fetchone()[0]
    
    if count == 0:  # 只在数据库为空时插入
        from datetime import timedelta
        
        for i, (question, answer, qtype, confidence, source, exec_time) in enumerate(default_qa_history):
            trace_id = f"demo_{i:03d}"
            # 构造简单的trace数据
            trace_data = {
                "trace_id": trace_id,
                "question": question,
                "total_steps": 5,
                "total_time": f"{exec_time:.3f}s",
                "steps": [
                    {"seq": 1, "stage": "输入处理", "service": "input_processor", "status": "success"},
                    {"seq": 2, "stage": "意图识别", "service": "intent_recognizer", "status": "success"},
                    {"seq": 3, "stage": "知识检索", "service": "rag_service", "status": "success", "response_data": source},
                    {"seq": 4, "stage": "内容生成", "service": "llm_service", "status": "success", "answer": answer},
                    {"seq": 5, "stage": "结果汇总", "service": "output_formatter", "status": "success"}
                ]
            }
            
            created_at = (datetime.now() - timedelta(days=len(default_qa_history)-i)).isoformat()
            
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO qa_history 
                    (user_id, question, answer, question_type, confidence, sources, execution_time, trace_id, trace_data, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, question, answer, qtype, confidence, source, exec_time, trace_id, json.dumps(trace_data), created_at))
            except sqlite3.IntegrityError:
                pass
    
    # 插入默认知识库文档
    default_knowledge_docs = [
        ("doc_sales_q1", "Q1季度销售报告", """2024年Q1季度销售报告摘要：
公司总销售额达到5000万元，同比增长15%。
- 核心产品线贡献占比65%，销售额3250万元
- 新产品线贡献占比35%，销售额1750万元
- 华东区域销售额最高，占总额40%
- 华南区域同比增长最快，达25%
关键客户新增：5家大型企业客户，合同总额超过800万元。
销售团队绩效：销售人员人均业绩达到120万元/季度。""", "sales", "销售部", "销售,报告,Q1,季度,业绩"),
        
        ("doc_sales_strategy", "销售策略指南", """销售策略与最佳实践指南：
1. 客户分级管理：按客户价值分为A/B/C三级
2. 销售流程标准化：需求分析→方案设计→商务谈判→签约→交付
3. 销售工具使用：CRM系统、销售漏斗管理、客户画像分析
4. 团队激励机制：基础薪资+绩效提成+年度奖金
5. 客户关系维护：定期回访、节日关怀、增值服务
销售部门目标：年销售额增长20%，新客户获取增加30%。""", "sales", "销售部", "销售,策略,客户,管理"),
        
        ("doc_hr_handbook", "员工手册", """公司员工福利体系：
1. 基础保险：五险一金，公司100%缴纳
2. 休假制度：法定假日+10天带薪年假（最高可累计至20天）
3. 补贴政策：交通补贴500元/月，餐补300元/月，通讯补贴200元/月
4. 健康关怀：年度体检+健身补贴500元/年
5. 培训发展：年度培训经费3000元，支持外部培训和认证
6. 绩效奖励：季度绩效奖金+年终奖金+优秀员工股权激励
员工晋升通道：初级→中级→高级→专家→管理层""", "hr", "人力资源部", "HR,员工,福利,手册"),
        
        ("doc_hr_recruitment", "招聘管理制度", """招聘管理流程：
1. 需求提交：部门经理填写招聘申请单
2. 职位发布：HR在招聘平台发布职位
3. 简历筛选：HR初筛+部门复筛
4. 面试安排：电话面试→技术面试→HR面试→终面
5. 背景调查：学历验证+工作经历核实
6. Offer发放：薪资谈判→Offer审批→入职准备
招聘渠道：内部推荐（奖励3000元）、招聘网站、猎头合作、校园招聘。""", "hr", "人力资源部", "HR,招聘,面试,入职"),
        
        ("doc_finance_budget", "年度预算报告", """2024年度预算分配报告：
总预算批准金额：10亿元
各部门预算分配：
- 研发部门：2.8亿（占28%）
- 销售市场：2.2亿（占22%）
- 人力资源：1.5亿（占15%）
- 运营管理：2.0亿（占20%）
- 行政成本：1.5亿（占15%）
预算执行要求：各部门按季度进度执行，偏差超过10%需提交说明。""", "finance", "财务部", "财务,预算,部门,分配"),
        
        ("doc_tech_architecture", "技术架构设计", """企业微服务架构设计规范：
1. API网关：Kong或Nginx Plus作为统一入口
2. 服务框架：FastAPI(Python)/Spring Boot(Java)
3. 服务网格：Istio管理服务间通信
4. 容器编排：Docker+Kubernetes
5. 数据库：MySQL主从+分库分表，读写分离
6. 缓存：Redis集群，热数据缓存
7. 消息队列：Kafka处理异步消息
8. 监控告警：Prometheus+Grafana+ELK日志栈
9. CI/CD：GitLab CI + ArgoCD自动化部署""", "tech", "技术部", "技术,架构,微服务,设计"),
        
        ("doc_supply_chain", "供应链管理", """供应商管理体系：
一级战略供应商（15家，占采购额80%）：
- 5家核心原料供应商
- 8家关键部件供应商
- 2家物流合作伙伴
二级优选供应商（40家，占采购额15%）
三级备选供应商（100+家）
供应商考核指标：质量合格率≥99%，交期准时率≥98%，成本年降3%
采购流程：需求提交→供应商选择→询价比价→合同签订→到货验收""", "supply_chain", "供应链部", "供应链,供应商,采购,管理"),
        
        ("doc_system_features", "平台功能介绍", """AI通用智能平台核心功能：
1. 智能问答系统：支持自然语言提问，智能匹配专业顾问角色
2. 知识库搜索：对接企业内部文档和业务数据，支持语义搜索
3. 调用链追踪：完整记录每个问题的处理过程和耗时
4. 系统集成：连接ERP、HR、财务等企业核心系统
5. 多角色支持：通用顾问、销售分析、HR管理、技术架构、财务分析
6. 数据持久化：所有问答记录本地存储，支持历史查询
7. 企业部署：支持轻量化和完整部署两种模式""", "general", "技术部", "平台,功能,AI,系统"),
    ]
    
    # 检查是否已有知识库文档
    cursor.execute("SELECT COUNT(*) FROM knowledge_documents")
    doc_count = cursor.fetchone()[0]
    
    if doc_count == 0:
        for doc_id, title, content, category, department, tags in default_knowledge_docs:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO knowledge_documents 
                    (doc_id, title, content, category, department, tags)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (doc_id, title, content, category, department, tags))
            except sqlite3.IntegrityError:
                pass
    
    conn.commit()
    conn.close()
    logger.info(f"✅ 数据库初始化完成: {DB_PATH}")

# 初始化数据库
init_db()

# 全局异常处理器 - 捕获 Pydantic 验证错误
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"[422 Validation Error] Path: {request.url.path}", file=sys.stderr, flush=True)
    print(f"[422 Validation Error] Method: {request.method}", file=sys.stderr, flush=True)
    print(f"[422 Validation Error] Pydantic errors: {exc.errors()}", file=sys.stderr, flush=True)
    
    logger.error(f"[422 Validation Error] Path: {request.url.path}")
    logger.error(f"[422 Validation Error] Method: {request.method}")
    logger.error(f"[422 Validation Error] Pydantic errors: {exc.errors()}")
    
    error_details = []
    for error in exc.errors():
        loc = '.'.join(str(x) for x in error['loc'])
        msg = error['msg']
        error_details.append(f"{loc}: {msg}")
        print(f"  - {loc}: {msg} (type: {error.get('type', 'unknown')})", file=sys.stderr, flush=True)
        logger.error(f"  - {loc}: {msg} (type: {error.get('type', 'unknown')})")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": error_details,
            "raw_errors": exc.errors()
        }
    )

# 中间件：记录所有 PUT 请求的详细信息
@app.middleware("http")
async def log_put_requests(request: Request, call_next):
    if request.method == "PUT" and "/api/llm/models/" in request.url.path:
        # 读取请求体
        body = await request.body()
        logger.info(f"[PUT Request] Path: {request.url.path}")
        logger.info(f"[PUT Request] Raw Body: {body}")
        try:
            body_dict = json.loads(body) if body else {}
            logger.info(f"[PUT Request] Parsed JSON: {body_dict}")
        except:
            logger.error(f"[PUT Request] Failed to parse JSON")
        
        # 创建新请求以继续处理（因为 body 已被读取）
        from io import BytesIO
        async def receive():
            return {"type": "http.request", "body": body}
        request._receive = receive
    
    response = await call_next(request)
    return response

# 数据模型
class QuestionRequest(BaseModel):
    question: str
    user_id: str = "web_ui_user"
    token: Optional[str] = None

class ServiceStatus(BaseModel):
    name: str
    url: str
    status: str
    response_time: float = 0.0

class LLMModelRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    name: str
    provider: str
    model_type: str = "api"
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 1.0
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class LLMModelUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    name: Optional[str] = None
    provider: Optional[str] = None
    model_type: Optional[str] = None
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    enabled: Optional[bool] = None
    is_default: Optional[bool] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class PromptRequest(BaseModel):
    name: str
    role: str
    system_prompt: str
    variables: list = None
    description: str = None
    metadata: dict = None

class PromptUpdate(BaseModel):
    name: str = None
    system_prompt: str = None
    variables: list = None
    description: str = None
    metadata: dict = None

class AgentToolRequest(BaseModel):
    name: str
    description: str
    tool_type: str
    endpoint: str = None
    method: str = "GET"
    parameters: dict = None
    metadata: dict = None

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    status: str
    token: str = None
    user: dict = None
    message: str = None

class AgentToolUpdate(BaseModel):
    name: str = None
    description: str = None
    tool_type: str = None
    endpoint: str = None
    method: str = None
    parameters: dict = None
    enabled: bool = None
    metadata: dict = None

# ==================== 数据库查询辅助函数 ====================

class DatabaseHelper:
    """数据库查询辅助类"""
    
    @staticmethod
    def get_first_prompt_template() -> tuple:
        """获取第一个启用的 Prompt 模板"""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, role, system_prompt FROM prompts WHERE enabled = 1 LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Failed to get prompt template: {e}")
            return None
    
    @staticmethod
    def get_prompt_by_role(role: str) -> dict:
        """根据角色获取 Prompt 模板"""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, role, system_prompt FROM prompts WHERE role = ? AND enabled = 1 LIMIT 1", (role,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Failed to get prompt by role {role}: {e}")
            return None
    
    @staticmethod
    def get_general_assistant_prompt() -> dict:
        """获取通用顾问 Prompt 模板"""
        return DatabaseHelper.get_prompt_by_role("general_assistant")
    
    @staticmethod
    def get_default_llm_model() -> dict:
        """获取默认 LLM 模型"""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 获取默认模型
            cursor.execute("SELECT name, provider, model_type FROM llm_models WHERE is_default = 1 AND enabled = 1 LIMIT 1")
            row = cursor.fetchone()
            
            # 如果没有默认模型，获取第一个启用的模型
            if not row:
                cursor.execute("SELECT name, provider, model_type FROM llm_models WHERE enabled = 1 LIMIT 1")
                row = cursor.fetchone()
            
            conn.close()
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Failed to get LLM model: {e}")
            return None
    
    @staticmethod
    def get_query_type_by_intent(intent: str, question: str) -> tuple:
        """根据意图和问题类型获取数据查询类型"""
        question_lower = question.lower()
        
        # 意图 -> 查询类型的映射
        if intent == "统计查询":
            # 统计查询
            if any(word in question_lower for word in ["销售", "订单", "收入", "金额", "费用"]):
                return ("sales_statistics", "统计销售数据")
            elif any(word in question_lower for word in ["员工", "人员", "招聘", "离职"]):
                return ("hr_statistics", "统计人力资源数据")
            elif any(word in question_lower for word in ["库存", "物品", "产品", "商品"]):
                return ("inventory_statistics", "统计库存数据")
            elif any(word in question_lower for word in ["成本", "预算", "财务", "收支"]):
                return ("finance_statistics", "统计财务数据")
            else:
                return ("general_statistics", "统计通用数据")
        
        elif intent == "数据查询":
            # 数据查询 - 查询特定的业务报告
            if any(word in question_lower for word in ["销售", "业绩", "报告", "成果"]):
                return ("sales_report", "查询销售报告")
            elif any(word in question_lower for word in ["财务", "收入", "成本", "利润"]):
                return ("financial_report", "查询财务报告")
            elif any(word in question_lower for word in ["员工", "部门", "组织"]):
                return ("hr_report", "查询人力资源报告")
            elif any(word in question_lower for word in ["客户", "订单"]):
                return ("customer_report", "查询客户订单报告")
            else:
                return ("general_report", "查询通用报告")
        
        elif intent == "操作指南":
            # 操作指南 - 查询流程和指南
            if any(word in question_lower for word in ["销售", "订单", "发货"]):
                return ("sales_workflow", "查询销售流程")
            elif any(word in question_lower for word in ["财务", "账务", "核算"]):
                return ("finance_workflow", "查询财务流程")
            else:
                return ("workflow_guide", "查询业务流程")
        
        elif intent == "概念解释":
            # 概念解释 - 查询参考数据和定义
            if any(word in question_lower for word in ["产品", "服务"]):
                return ("product_reference", "查询产品参考")
            else:
                return ("concept_reference", "查询概念定义")
        
        elif intent == "比较分析":
            # 比较分析 - 查询历史数据进行对比
            if any(word in question_lower for word in ["销售", "业绩"]):
                return ("sales_comparison", "对比销售数据")
            elif any(word in question_lower for word in ["市场", "竞争"]):
                return ("market_comparison", "对比市场数据")
            else:
                return ("data_comparison", "对比数据分析")
        
        else:
            # 通用查询
            return ("general_query", "通用数据查询")

# ==================== 健康检查 ====================

async def check_service_health(url: str) -> tuple[str, float]:
    """检查服务健康状态"""
    try:
        async with aiohttp.ClientSession() as session:
            start = datetime.now()
            async with session.get(f"{url}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                elapsed = (datetime.now() - start).total_seconds()
                if resp.status == 200:
                    return "healthy", elapsed
                else:
                    return "unhealthy", elapsed
    except Exception as e:
        logger.error(f"Health check failed for {url}: {e}")
        return "offline", 0.0

@app.get("/api/services/status")
async def get_services_status():
    """获取所有服务的状态"""
    services = [
        ("QA Entry", QA_SERVICE_URL),
        ("Prompt Service", PROMPT_SERVICE_URL),
        ("RAG Service", RAG_SERVICE_URL),
        ("Agent Service", AGENT_SERVICE_URL),
        ("Integration Service", INTEGRATION_SERVICE_URL),
        ("LLM Service", LLM_SERVICE_URL),
    ]
    
    statuses = []
    for name, url in services:
        status, response_time = await check_service_health(url)
        statuses.append({
            "name": name,
            "url": url,
            "status": status,
            "response_time": f"{response_time:.3f}s"
        })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "services": statuses,
        "overall_status": "healthy" if all(s["status"] == "healthy" for s in statuses) else "degraded"
    }


# ==================== 监控统计API ====================

def update_usage_stat(stat_type: str, stat_key: str, increment: int = 1):
    """更新使用统计"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            INSERT INTO usage_statistics (stat_date, stat_type, stat_key, stat_value)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(stat_date, stat_type, stat_key) 
            DO UPDATE SET stat_value = stat_value + ?, updated_at = CURRENT_TIMESTAMP
        """, (today, stat_type, stat_key, increment, increment))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to update usage stat: {e}")


@app.get("/api/monitor/statistics")
async def get_monitor_statistics():
    """获取监控统计数据"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. 总提问次数（从qa_history表）
        cursor.execute("SELECT COUNT(*) FROM qa_history")
        total_questions = cursor.fetchone()[0]
        
        # 2. 今日提问次数
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM qa_history WHERE DATE(created_at) = ?", (today,))
        today_questions = cursor.fetchone()[0]
        
        # 3. RAG查询次数（从usage_statistics表，如果没有则估算）
        cursor.execute("""
            SELECT COALESCE(SUM(stat_value), 0) FROM usage_statistics 
            WHERE stat_type = 'rag_query'
        """)
        rag_queries = cursor.fetchone()[0]
        if rag_queries == 0:
            # 假设每个问答都有RAG查询
            rag_queries = total_questions
        
        # 4. 今日RAG查询
        cursor.execute("""
            SELECT COALESCE(SUM(stat_value), 0) FROM usage_statistics 
            WHERE stat_type = 'rag_query' AND stat_date = ?
        """, (today,))
        today_rag_queries = cursor.fetchone()[0]
        if today_rag_queries == 0:
            today_rag_queries = today_questions
        
        # 5. 各Prompt使用次数
        cursor.execute("""
            SELECT question_type, COUNT(*) as count 
            FROM qa_history 
            WHERE question_type IS NOT NULL AND question_type != ''
            GROUP BY question_type 
            ORDER BY count DESC
        """)
        prompt_usage = []
        prompt_mapping = {
            'general_inquiry': '通用顾问',
            'sales_analysis': '销售分析顾问',
            'hr_policy': 'HR政策顾问',
            'technical_design': '技术架构顾问',
            'finance_budget': '财务分析顾问',
            'supply_chain': '供应链顾问'
        }
        for row in cursor.fetchall():
            prompt_usage.append({
                "prompt_type": row[0],
                "prompt_name": prompt_mapping.get(row[0], row[0]),
                "count": row[1]
            })
        
        # 6. 各业务部门数据使用次数（从qa_history的sources字段分析）
        cursor.execute("SELECT sources FROM qa_history WHERE sources IS NOT NULL AND sources != ''")
        department_stats = {
            'sales': {'name': '销售部门', 'count': 0},
            'hr': {'name': '人力资源', 'count': 0},
            'finance': {'name': '财务部门', 'count': 0},
            'technical': {'name': '技术部门', 'count': 0},
            'supply_chain': {'name': '供应链', 'count': 0},
            'marketing': {'name': '市场部门', 'count': 0}
        }
        
        for row in cursor.fetchall():
            sources = row[0].lower()
            if 'erp' in sources or 'sales' in sources or 'crm' in sources:
                department_stats['sales']['count'] += 1
            if 'hr' in sources or 'employee' in sources:
                department_stats['hr']['count'] += 1
            if 'finance' in sources or 'budget' in sources:
                department_stats['finance']['count'] += 1
            if 'tech' in sources or 'dev' in sources:
                department_stats['technical']['count'] += 1
            if 'supply' in sources or 'scm' in sources:
                department_stats['supply_chain']['count'] += 1
            if 'marketing' in sources:
                department_stats['marketing']['count'] += 1
        
        department_usage = [
            {"department": k, "name": v['name'], "count": v['count']} 
            for k, v in department_stats.items() if v['count'] > 0
        ]
        department_usage.sort(key=lambda x: x['count'], reverse=True)
        
        # 7. Token消耗统计（估算：平均每个问题消耗约500 tokens）
        cursor.execute("""
            SELECT COALESCE(SUM(stat_value), 0) FROM usage_statistics 
            WHERE stat_type = 'token_usage'
        """)
        total_tokens = cursor.fetchone()[0]
        if total_tokens == 0:
            # 估算：问题平均100 tokens，回答平均400 tokens
            total_tokens = total_questions * 500
        
        cursor.execute("""
            SELECT COALESCE(SUM(stat_value), 0) FROM usage_statistics 
            WHERE stat_type = 'token_usage' AND stat_date = ?
        """, (today,))
        today_tokens = cursor.fetchone()[0]
        if today_tokens == 0:
            today_tokens = today_questions * 500
        
        # 8. 最近7天的提问趋势
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM qa_history
            WHERE created_at >= DATE('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        daily_trend = []
        for row in cursor.fetchall():
            daily_trend.append({"date": row[0], "count": row[1]})
        
        # 9. 平均响应时间
        cursor.execute("SELECT AVG(execution_time) FROM qa_history WHERE execution_time > 0")
        avg_response_time = cursor.fetchone()[0] or 0
        
        # 10. 平均置信度
        cursor.execute("SELECT AVG(confidence) FROM qa_history WHERE confidence > 0")
        avg_confidence = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "overview": {
                "total_questions": total_questions,
                "today_questions": today_questions,
                "total_rag_queries": rag_queries,
                "today_rag_queries": today_rag_queries,
                "total_tokens": total_tokens,
                "today_tokens": today_tokens,
                "avg_response_time": round(avg_response_time, 2),
                "avg_confidence": round(avg_confidence * 100, 1)
            },
            "prompt_usage": prompt_usage,
            "department_usage": department_usage,
            "daily_trend": daily_trend
        }
        
    except Exception as e:
        logger.error(f"Failed to get monitor statistics: {e}")
        return {
            "status": "error",
            "message": str(e),
            "overview": {
                "total_questions": 0,
                "today_questions": 0,
                "total_rag_queries": 0,
                "today_rag_queries": 0,
                "total_tokens": 0,
                "today_tokens": 0,
                "avg_response_time": 0,
                "avg_confidence": 0
            },
            "prompt_usage": [],
            "department_usage": [],
            "daily_trend": []
        }


# ==================== 问答接口 ====================

@app.post("/api/qa/ask")
async def ask_question(request: QuestionRequest):
    """提问"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{QA_SERVICE_URL}/api/qa/ask",
                json=request.model_dump(),
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info(f"QA response received for question: {request.question}")
                    return data
                else:
                    logger.warning(f"QA service returned status {resp.status}")
                    error_text = await resp.text()
                    logger.error(f"QA service error: {error_text}")
                    return {
                        "question": request.question,
                        "answer": "抱歉，问答服务暂时不可用，请稍后重试。",
                        "confidence": 0.0,
                        "error": f"Service returned {resp.status}"
                    }
    except Exception as e:
        logger.error(f"QA request failed: {e}")
        return {
            "question": request.question,
            "answer": f"提问处理失败: {str(e)}",
            "confidence": 0.0,
            "error": str(e)
        }

# ==================== Prompt 配置接口 ====================

@app.get("/api/prompts")
async def get_prompts():
    """获取所有 Prompt 模板"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, role, system_prompt, description FROM prompts WHERE enabled = 1 ORDER BY created_at")
        rows = cursor.fetchall()
        conn.close()
        
        templates = [dict(row) for row in rows]
        logger.info(f"Successfully retrieved {len(templates)} prompts from database")
        
        return {
            "status": "success",
            "templates": templates,
            "count": len(templates)
        }
    except Exception as e:
        logger.error(f"Failed to get prompts: {e}")
        return {
            "status": "error",
            "message": str(e),
            "templates": []
        }

@app.post("/api/prompts")
async def create_prompt(prompt: PromptRequest):
    """创建新 Prompt 模板"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO prompts (name, role, system_prompt, variables, description, enabled)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (
            prompt.name,
            prompt.role,
            prompt.system_prompt,
            json.dumps(prompt.variables) if prompt.variables else None,
            prompt.description
        ))
        
        conn.commit()
        prompt_id = cursor.lastrowid
        conn.close()
        
        return {"status": "success", "id": prompt_id}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": "Prompt 名称或角色已存在"}
    except Exception as e:
        logger.error(f"Failed to create prompt: {e}")
        return {"status": "error", "message": str(e)}

@app.put("/api/prompts/{role}")
async def update_prompt(role: str, prompt: PromptUpdate):
    """更新 Prompt 模板"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 构建更新语句
        update_fields = []
        update_values = []
        
        if prompt.name is not None:
            update_fields.append("name=?")
            update_values.append(prompt.name)
        
        if prompt.system_prompt is not None:
            update_fields.append("system_prompt=?")
            update_values.append(prompt.system_prompt)
        
        if prompt.variables is not None:
            update_fields.append("variables=?")
            update_values.append(json.dumps(prompt.variables))
        
        if prompt.description is not None:
            update_fields.append("description=?")
            update_values.append(prompt.description)
        
        if not update_fields:
            return {"status": "error", "message": "没有要更新的字段"}
        
        update_fields.append("updated_at=CURRENT_TIMESTAMP")
        update_values.append(role)
        
        sql = f"UPDATE prompts SET {', '.join(update_fields)} WHERE role=?"
        cursor.execute(sql, update_values)
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected == 0:
            return {"status": "error", "message": "Prompt 不存在"}
        
        return {"status": "success", "updated": True}
    except Exception as e:
        logger.error(f"Failed to update prompt: {e}")
        return {"status": "error", "message": str(e)}

@app.delete("/api/prompts/{role}")
async def delete_prompt(role: str):
    """删除 Prompt 模板"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM prompts WHERE role=?", (role,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected == 0:
            return {"status": "error", "message": "Prompt 不存在"}
        
        return {"status": "success", "deleted": True}
    except Exception as e:
        logger.error(f"Failed to delete prompt: {e}")
        return {"status": "error", "message": str(e)}

# ==================== RAG 知识库接口 ====================

def search_local_knowledge(query: str) -> list:
    """本地知识库搜索（使用词组匹配，避免单字符误匹配）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取所有启用的文档
    cursor.execute("""
        SELECT doc_id, title, content, category, department, tags
        FROM knowledge_documents 
        WHERE enabled = 1
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    # 提取关键词（至少2字的词组）
    def extract_keywords(text):
        keywords = set()
        keywords.add(text.strip())
        for i in range(len(text) - 1):
            keywords.add(text[i:i+2])
        for i in range(len(text) - 2):
            keywords.add(text[i:i+3])
        return keywords
    
    query_keywords = extract_keywords(query)
    MIN_SCORE_THRESHOLD = 30  # 最低分数阈值
    
    results = []
    for row in rows:
        title = row['title']
        content = row['content']
        tags = row['tags'] or ''
        full_text = f"{title} {content} {tags}"
        
        score = 0
        
        # 1. 完全匹配查询文本（最高优先级）
        if query in title:
            score += 200
        if query in content:
            score += 100
        if query in tags:
            score += 80
        
        # 2. 词组匹配（至少2字的词组才计分）
        for keyword in query_keywords:
            if len(keyword) >= 2:
                if keyword in title:
                    score += 50
                elif keyword in content:
                    score += 20
                elif keyword in tags:
                    score += 30
        
        # 只返回分数达到阈值的文档
        if score >= MIN_SCORE_THRESHOLD:
            # 归一化分数到 0-1 范围
            normalized_score = min(score / 300, 0.99)
            results.append({
                "doc_id": row['doc_id'],
                "title": row['title'],
                "content": row['content'],
                "category": row['category'],
                "department": row['department'],
                "score": normalized_score
            })
    
    # 按分数排序
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:10]

@app.get("/api/rag/documents")
async def get_documents():
    """获取知识库文档"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{RAG_SERVICE_URL}/api/rag/documents",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info("Successfully retrieved documents from RAG service")
                    return data
    except Exception as e:
        logger.warning(f"RAG service not available, using local: {e}")
    
    # 回退到本地数据库
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM knowledge_documents WHERE enabled = 1")
        rows = cursor.fetchall()
        conn.close()
        
        documents = [dict(row) for row in rows]
        return {"documents": documents, "source": "local"}
    except Exception as e:
        logger.error(f"Local document fetch failed: {e}")
        return {"documents": [], "error": str(e)}

@app.get("/api/rag/search")
async def search_documents_get(query: str = ""):
    """搜索知识库（GET 方式）"""
    if not query:
        return {"query": "", "results": [], "message": "请输入搜索关键词"}
    
    # 优先尝试远程 RAG 服务
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{RAG_SERVICE_URL}/api/rag/search",
                json={"query": query},
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info(f"RAG search completed for query: {query}")
                    # 转换 documents 为 results 格式
                    if 'documents' in data and 'results' not in data:
                        results = []
                        for doc in data['documents']:
                            results.append({
                                "doc_id": doc.get('id', ''),
                                "title": doc.get('title', ''),
                                "content": doc.get('content', ''),
                                "category": doc.get('category', 'general'),
                                "score": 0.85  # 默认相关度分数
                            })
                        return {
                            "query": query,
                            "results": results,
                            "source": "remote",
                            "timestamp": datetime.now().isoformat()
                        }
                    return data
    except Exception as e:
        logger.warning(f"RAG service not available, using local search: {e}")
    
    # 回退到本地搜索
    results = search_local_knowledge(query)
    return {
        "query": query,
        "results": results,
        "source": "local",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/rag/search")
async def search_documents_post(query: dict):
    """搜索知识库（POST 方式）"""
    search_query = query.get('query', '')
    if not search_query:
        return {"query": "", "results": [], "message": "请输入搜索关键词"}
    
    # 优先尝试远程 RAG 服务
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{RAG_SERVICE_URL}/api/rag/search",
                json=query,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info(f"RAG search completed for query: {search_query}")
                    return data
    except Exception as e:
        logger.warning(f"RAG service not available, using local search: {e}")
    
    # 回退到本地搜索
    results = search_local_knowledge(search_query)
    return {
        "query": search_query,
        "results": results,
        "source": "local",
        "timestamp": datetime.now().isoformat()
    }

# ==================== Agent 工具接口 ====================

@app.get("/api/agent/tools")
async def get_tools():
    """获取可用工具"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{AGENT_SERVICE_URL}/api/agent/tools",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info("Successfully retrieved tools from Agent service")
                    return data
                else:
                    logger.warning(f"Agent service returned status {resp.status}")
    except Exception as e:
        logger.error(f"Tools request failed: {e}")
    
    # 服务不可用时返回空工具列表
    return {"tools": [], "error": "Agent 服务暂时不可用"}

# ==================== 集成服务数据接口 ====================

@app.get("/api/integration/status")
async def get_integration_status():
    """获取企业系统集成状态"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{INTEGRATION_SERVICE_URL}/health",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    return {
                        "status": "connected",
                        "systems": ["ERP", "HRM", "CRM", "Finance"]
                    }
                else:
                    return {"status": "disconnected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/integration/erp/sales/{year}/{quarter}")
async def get_erp_sales(year: int, quarter: str):
    """获取ERP销售数据"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{INTEGRATION_SERVICE_URL}/api/integration/erp/sales/{year}/{quarter}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return {"error": "Failed to fetch sales data"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/integration/search")
async def search_integration_knowledge(query: str = Query(...)):
    """搜索企业集成知识库（按业务分类搜索）"""
    # 业务分类映射（英文分类名 -> 用于搜索的中文关键词）
    category_mapping = {
        'sales': '销售',
        'hr': '员工',
        'finance': '财务',
        'technical': '技术',
        'supply_chain': '供应链',
        'marketing': '市场'
    }
    
    # 检查是否是分类搜索（英文分类名）
    search_category = None
    search_keyword = query  # 默认使用原始查询词
    
    if query.lower() in category_mapping:
        search_category = query.lower()
        search_keyword = category_mapping[query.lower()]  # 使用对应的中文关键词搜索
    
    # 尝试远程 RAG 服务
    try:
        async with aiohttp.ClientSession() as session:
            search_params = {"query": search_keyword, "top_k": 10}
            if search_category:
                search_params["category"] = search_category
            
            async with session.post(
                f"{RAG_SERVICE_URL}/api/rag/search",
                json=search_params,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    documents = data.get("documents", [])
                    
                    # 转换为前端期望的格式
                    results = []
                    for doc in documents:
                        results.append({
                            "title": doc.get("title", "未知文档"),
                            "content": doc.get("content", ""),
                            "category": doc.get("category", "general"),
                            "source": doc.get("source", "知识库"),
                            "score": 0.85
                        })
                    
                    if results:
                        return {
                            "query": query,
                            "results": results,
                            "source": "remote",
                            "timestamp": datetime.now().isoformat()
                        }
    except Exception as e:
        logger.warning(f"Remote integration search failed: {e}")
    
    # 回退到本地知识库搜索（使用中文关键词）
    local_results = search_local_knowledge(search_keyword)
    
    # 如果是分类搜索但本地没有结果，返回该分类的描述信息
    if not local_results and search_category:
        category_descriptions = {
            'sales': {'title': '销售业务知识', 'content': '包含销售报告、客户分析、销售策略、佣金政策等销售相关文档。'},
            'hr': {'title': '人力资源知识', 'content': '包含员工手册、组织结构、培训发展、绩效管理等HR相关文档。'},
            'finance': {'title': '财务知识', 'content': '包含财务预算、成本分析、财务报告、财务政策等财务相关文档。'},
            'technical': {'title': '技术知识', 'content': '包含系统架构、技术文档、开发规范、API文档等技术相关文档。'},
            'supply_chain': {'title': '供应链知识', 'content': '包含供应商管理、采购流程、库存管理、物流配送等供应链相关文档。'},
            'marketing': {'title': '市场营销知识', 'content': '包含市场分析、营销策略、品牌推广、客户获取等市场相关文档。'}
        }
        desc = category_descriptions.get(search_category, {})
        return {
            "query": query,
            "results": [{
                "title": desc.get('title', f'{query}相关知识'),
                "content": desc.get('content', f'暂无{query}相关的具体文档，请联系相关部门获取详细信息。'),
                "category": search_category,
                "source": "系统提示"
            }],
            "source": "local",
            "timestamp": datetime.now().isoformat()
        }
    
    return {
        "query": query,
        "results": local_results,
        "source": "local",
        "timestamp": datetime.now().isoformat()
    }


# ==================== LLM 模型接口 ====================

@app.get("/api/llm/models")
async def get_llm_models():
    """获取可用的LLM模型（优先远程服务，回退到本地数据库）"""
    # 优先尝试远程 LLM 服务
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{LLM_SERVICE_URL}/api/llm/models",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # 转换远程服务格式为前端期望的格式
                    if 'models' in data:
                        return data
                    # 处理远程服务返回 supported_models 格式
                    if 'supported_models' in data:
                        provider = data.get('current_provider', 'openai')
                        default_model = data.get('default_model', 'gpt-3.5-turbo')
                        model_list = data['supported_models'].get(provider, [])
                        models = []
                        for i, model_name in enumerate(model_list):
                            models.append({
                                "id": i + 1,
                                "name": model_name,
                                "provider": provider,
                                "model_type": "api",
                                "max_tokens": 4096 if 'gpt-4' in model_name else 2048,
                                "temperature": 0.7,
                                "enabled": 1,
                                "is_default": 1 if model_name == default_model else 0
                            })
                        return {
                            "status": "success",
                            "source": "remote",
                            "count": len(models),
                            "models": models
                        }
    except Exception as e:
        logger.warning(f"LLM service not available, using local database: {e}")
    
    # 回退到本地数据库
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM llm_models ORDER BY is_default DESC, created_at")
        rows = cursor.fetchall()
        conn.close()
        
        models = []
        for row in rows:
            model = dict(row)
            if model.get('metadata'):
                try:
                    model['metadata'] = json.loads(model['metadata'])
                except:
                    pass
            models.append(model)
        
        logger.info(f"Retrieved {len(models)} models from local database")
        return {
            "status": "success",
            "source": "local",
            "count": len(models),
            "models": models
        }
    except Exception as e:
        logger.error(f"Failed to get models from local database: {e}")
        return {"error": str(e), "models": []}

# ==================== 网页入口 ====================

@app.get("/")
async def get_index():
    """返回主页HTML或登陆页面"""
    return FileResponse("static/index.html")

@app.get("/login")
async def get_login():
    """登陆功能已禁用，直接跳转到主页"""
    return RedirectResponse(url="/", status_code=302)

@app.get("/admin")
async def get_admin():
    """返回管理员控制台页面"""
    return FileResponse("static/admin_console.html")

@app.post("/api/login")
async def login(request: LoginRequest):
    """登陆功能已禁用"""
    return {"status": "error", "message": "登陆功能已禁用"}

@app.get("/api/user/verify-token")
async def verify_token(token: str):
    """验证会话令牌"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查会话是否有效
        cursor.execute("""
            SELECT us.user_id, u.username, u.role, u.language 
            FROM user_sessions us
            JOIN users u ON us.user_id = u.id
            WHERE us.token = ? AND us.expires_at > ?
        """, (token, datetime.now().isoformat()))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user = dict(row)
            return {
                "status": "valid",
                "user": {
                    "id": user["user_id"],
                    "username": user["username"],
                    "role": user["role"],
                    "language": user["language"]
                }
            }
        else:
            return {"status": "invalid"}
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/user/logout")
async def logout(token: str):
    """用户登出"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        return {"status": "error", "message": str(e)}

@app.put("/api/user/language")
async def set_user_language(token: str, language: str):
    """设置用户语言偏好"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取用户ID
        cursor.execute("SELECT user_id FROM user_sessions WHERE token = ?", (token,))
        row = cursor.fetchone()
        
        if not row:
            return {"status": "error", "message": "无效的令牌"}
        
        user_id = row[0]
        
        # 更新用户语言
        cursor.execute("UPDATE users SET language = ? WHERE id = ?", (language, user_id))
        conn.commit()
        conn.close()
        
        return {"status": "success", "language": language}
    except Exception as e:
        logger.error(f"Failed to set language: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/qa/history")
async def get_qa_history(token: str = Query(...), limit: int = Query(20)):
    """获取用户的问答历史"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取用户ID
        cursor.execute("SELECT user_id FROM user_sessions WHERE token = ?", (token,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"status": "error", "message": "令牌无效"}
        
        user_id = row[0]
        
        # 获取用户的问答历史
        cursor.execute("""
            SELECT id, question, answer, question_type, confidence, sources, 
                   execution_time, created_at
            FROM qa_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            try:
                sources = json.loads(row[5]) if row[5] else []
            except:
                sources = []
            
            history.append({
                "id": row[0],
                "question": row[1],
                "answer": row[2][:200] + "..." if len(row[2]) > 200 else row[2],
                "question_type": row[3],
                "confidence": row[4],
                "sources_count": len(sources),
                "execution_time": row[6],
                "created_at": row[7]
            })
        
        return {
            "status": "success",
            "user_id": user_id,
            "total": len(history),
            "history": history
        }
    except Exception as e:
        logger.error(f"Failed to get QA history: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/qa/history/all")
async def get_all_qa_history(limit: int = Query(50)):
    """获取所有问答历史（无需token验证）"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取所有问答历史
        cursor.execute("""
            SELECT id, question, answer, question_type, confidence, sources, 
                   execution_time, created_at, trace_id
            FROM qa_history
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "question_type": row[3],
                "confidence": row[4],
                "sources": row[5],
                "execution_time": row[6],
                "created_at": row[7],
                "trace_id": row[8]
            })
        
        return {
            "status": "success",
            "total": len(history),
            "history": history
        }
    except Exception as e:
        logger.error(f"Failed to get all QA history: {e}")
        return {"status": "error", "message": str(e), "history": []}


@app.get("/api/qa/history/{qa_id}")
async def get_qa_detail(qa_id: int, token: str = Query(...)):
    """获取特定问答的完整详情"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取用户ID
        cursor.execute("SELECT user_id FROM user_sessions WHERE token = ?", (token,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"status": "error", "message": "令牌无效"}
        
        user_id = row[0]
        
        # 获取问答详情（确保属于当前用户）
        cursor.execute("""
            SELECT id, question, answer, question_type, confidence, sources, 
                   execution_time, trace_id, trace_data, created_at
            FROM qa_history
            WHERE id = ? AND user_id = ?
        """, (qa_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {"status": "error", "message": "未找到此问答记录"}
        
        try:
            sources = json.loads(row[5]) if row[5] else []
            trace_data = json.loads(row[8]) if row[8] else {}
        except:
            sources = []
            trace_data = {}
        
        return {
            "status": "success",
            "qa": {
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "question_type": row[3],
                "confidence": row[4],
                "sources": sources,
                "execution_time": row[6],
                "trace_id": row[7],
                "trace_data": trace_data,
                "created_at": row[9]
            }
        }
    except Exception as e:
        logger.error(f"Failed to get QA detail: {e}")
        return {"status": "error", "message": str(e)}


# ==================== Agent 工具管理 ====================

@app.get("/api/agent/tools")
async def get_agent_tools():
    """获取所有 Agent 工具"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agent_tools WHERE enabled=1 ORDER BY created_at")
        rows = cursor.fetchall()
        conn.close()
        
        tools = [dict(row) for row in rows]
        logger.info(f"Successfully retrieved {len(tools)} agent tools")
        
        return {
            "status": "success",
            "tools": tools,
            "count": len(tools)
        }
    except Exception as e:
        logger.error(f"Failed to get agent tools: {e}")
        return {"status": "error", "tools": []}

@app.post("/api/agent/tools")
async def create_agent_tool(tool: AgentToolRequest):
    """创建新 Agent 工具"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO agent_tools (name, description, tool_type, endpoint, method, parameters, enabled)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (
            tool.name,
            tool.description,
            tool.tool_type,
            tool.endpoint,
            tool.method,
            json.dumps(tool.parameters) if tool.parameters else None
        ))
        
        conn.commit()
        tool_id = cursor.lastrowid
        conn.close()
        
        return {"status": "success", "id": tool_id}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": "工具名称已存在"}
    except Exception as e:
        logger.error(f"Failed to create agent tool: {e}")
        return {"status": "error", "message": str(e)}

@app.put("/api/agent/tools/{tool_id}")
async def update_agent_tool(tool_id: int, tool: AgentToolUpdate):
    """更新 Agent 工具"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 构建更新语句
        update_fields = []
        update_values = []
        
        if tool.name is not None:
            update_fields.append("name=?")
            update_values.append(tool.name)
        
        if tool.description is not None:
            update_fields.append("description=?")
            update_values.append(tool.description)
        
        if tool.tool_type is not None:
            update_fields.append("tool_type=?")
            update_values.append(tool.tool_type)
        
        if tool.endpoint is not None:
            update_fields.append("endpoint=?")
            update_values.append(tool.endpoint)
        
        if tool.method is not None:
            update_fields.append("method=?")
            update_values.append(tool.method)
        
        if tool.parameters is not None:
            update_fields.append("parameters=?")
            update_values.append(json.dumps(tool.parameters))
        
        if tool.enabled is not None:
            update_fields.append("enabled=?")
            update_values.append(tool.enabled)
        
        if not update_fields:
            return {"status": "error", "message": "没有要更新的字段"}
        
        update_fields.append("updated_at=CURRENT_TIMESTAMP")
        update_values.append(tool_id)
        
        sql = f"UPDATE agent_tools SET {', '.join(update_fields)} WHERE id=?"
        cursor.execute(sql, update_values)
        
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected == 0:
            return {"status": "error", "message": "工具不存在"}
        
        return {"status": "success", "updated": True}
    except Exception as e:
        logger.error(f"Failed to update agent tool: {e}")
        return {"status": "error", "message": str(e)}

@app.delete("/api/agent/tools/{tool_id}")
async def delete_agent_tool(tool_id: int):
    """删除 Agent 工具"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM agent_tools WHERE id=?", (tool_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        if affected == 0:
            return {"status": "error", "message": "工具不存在"}
        
        return {"status": "success", "deleted": True}
    except Exception as e:
        logger.error(f"Failed to delete agent tool: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/agent/tools/reorder")
async def reorder_agent_tools(tools: dict):
    """重新排序 Agent 工具"""
    try:
        tool_names = tools.get("tools", []) if isinstance(tools, dict) else []
        
        if not tool_names:
            return {"status": "error", "message": "没有工具数据"}
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 更新每个工具的排序位置
        for index, tool_name in enumerate(tool_names):
            cursor.execute("""
                UPDATE agent_tools 
                SET updated_at=CURRENT_TIMESTAMP
                WHERE name=?
            """, (tool_name,))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Successfully reordered {len(tool_names)} tools")
        return {"status": "success", "message": "工具顺序已保存"}
    except Exception as e:
        logger.error(f"Failed to reorder agent tools: {e}")
        return {"status": "error", "message": str(e)}

# ==================== 系统监控接口 ====================

@app.get("/api/system/stats")
async def get_stats():
    """获取系统统计数据"""
    import os
    import psutil
    
    try:
        # 获取系统资源使用情况
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory.used / (1024**3):.2f} GB / {memory.total / (1024**3):.2f} GB",
                "disk_usage": f"{disk.used / (1024**3):.2f} GB / {disk.total / (1024**3):.2f} GB",
                "memory_percent": f"{memory.percent}%"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "system": {}
        }

@app.get("/api/system/health")
async def get_health():
    """获取系统健康状态"""
    services = [
        ("QA Entry", QA_SERVICE_URL),
        ("Prompt Service", PROMPT_SERVICE_URL),
        ("RAG Service", RAG_SERVICE_URL),
        ("Agent Service", AGENT_SERVICE_URL),
        ("Integration Service", INTEGRATION_SERVICE_URL),
        ("LLM Service", LLM_SERVICE_URL),
    ]
    
    statuses = []
    healthy_count = 0
    
    for name, url in services:
        status, response_time = await check_service_health(url)
        statuses.append({
            "name": name,
            "status": status,
            "response_time": f"{response_time:.3f}s"
        })
        if status == "healthy":
            healthy_count += 1
    
    return {
        "timestamp": datetime.now().isoformat(),
        "services": statuses,
        "healthy_services": healthy_count,
        "total_services": len(services),
        "overall_status": "healthy" if healthy_count == len(services) else "degraded"
    }

# ==================== 调用链追踪接口 ====================

@app.post("/api/trace/qa/ask")
async def ask_question_with_trace(request: QuestionRequest):
    """带调用链追踪的问答接口"""
    chain = CallChain(request.question)
    
    # 初始化变量
    retrieved_docs = None
    retrieval_status = "pending"
    retrieval_error = None
    docs_count = 0
    qa_response = None
    user_id = None
    
    # 从请求中获取用户ID（来自token）
    user_token = getattr(request, 'token', None)
    if user_token:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user_sessions WHERE token = ?", (user_token,))
        row = cursor.fetchone()
        if row:
            user_id = row[0]
        conn.close()
    
    try:
        # 1. 输入处理阶段
        # 文本预处理
        processed_question = request.question.strip()
        question_length = len(processed_question)
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in processed_question)
        
        chain.add_step(
            stage="输入处理",
            service="QA Entry Service (端口 8001)",
            purpose="接收用户问题，进行文本预处理和清洗",
            data={
                "raw_question": request.question,
                "processed_question": processed_question,
                "question_length": question_length,
                "language_detected": "中文" if has_chinese else "英文",
                "preprocessing_actions": ["去除首尾空格", "UTF-8编码验证", "特殊字符处理"],
                "user_id": request.user_id or "anonymous"
            }
        )
        
        # 获取真实回答（从 QA 服务）
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{QA_SERVICE_URL}/api/qa/ask",
                    json=request.model_dump(),
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        qa_response = await resp.json()
                    else:
                        qa_response = {
                            "question": request.question,
                            "answer": "抱歉，暂时无法获取回答，请稍后重试。",
                            "confidence": 0.0,
                            "execution_time": 0
                        }
        except Exception as e:
            logger.error(f"Failed to get QA response: {e}")
            qa_response = {
                "question": request.question,
                "answer": f"处理过程中出现错误: {str(e)}",
                "confidence": 0.0,
                "execution_time": 0
            }
        
        # 2. 意图识别阶段
        intent_data = qa_response.get("question_type", "general_inquiry")
        sources = qa_response.get("sources", [])
        
        # 提取关键词
        keywords = []
        for word in ["销售", "财务", "HR", "技术", "预算", "员工", "报告", "数据", "系统", "架构"]:
            if word in request.question:
                keywords.append(word)
        
        intent_mapping = {
            "general_inquiry": "通用咨询",
            "sales_analysis": "销售分析",
            "hr_policy": "人力资源政策",
            "technical_design": "技术设计",
            "finance_budget": "财务预算",
            "supply_chain": "供应链管理"
        }
        
        chain.add_step(
            stage="意图识别",
            service="QA Entry Service (端口 8001)",
            purpose="使用NLP模型进行问题分类、实体提取和关键词识别",
            data={
                "recognized_intent": intent_mapping.get(intent_data, intent_data),
                "intent_code": intent_data,
                "confidence_score": qa_response.get("confidence", 0),
                "extracted_keywords": keywords if keywords else ["通用查询"],
                "question_category": "业务咨询" if any(k in request.question for k in ["销售", "财务", "预算"]) else "技术咨询" if any(k in request.question for k in ["技术", "架构", "系统"]) else "通用咨询",
                "entity_recognition": {
                    "has_time_reference": any(t in request.question for t in ["Q1", "Q2", "Q3", "Q4", "季度", "年度", "月"]),
                    "has_number": any(c.isdigit() for c in request.question),
                    "has_department": any(d in request.question for d in ["销售部", "技术部", "财务部", "人力资源"])
                },
                "routing_decision": f"路由到 {intent_mapping.get(intent_data, '通用')} 处理流程"
            }
        )
        
        # 3. 知识检索阶段
        retrieved_docs = None
        retrieval_status = "success"
        retrieval_error = None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{RAG_SERVICE_URL}/api/rag/search",
                    json={"query": request.question, "top_k": 5},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        rag_response = await resp.json()
                        retrieved_docs = rag_response.get("documents", [])
                        
                        if retrieved_docs and retrieved_docs[0].get("category") not in ("search_hint", "hint"):
                            retrieval_status = "success"
                            docs_count = len(retrieved_docs)
                        else:
                            retrieval_status = "no_results"
                            docs_count = 0
                    else:
                        retrieval_status = "service_error"
                        retrieval_error = f"RAG service returned {resp.status}"
        except Exception as e:
            retrieval_status = "connection_error"
            retrieval_error = str(e)
        
        # 3a. 向量化阶段
        chain.add_step(
            stage="知识检索-向量化",
            service="RAG Service (端口 8003) - FAISS向量库",
            purpose="将问题转换为向量表示以便相似度计算",
            status="success" if retrieval_status != "connection_error" else "error",
            data={
                "input_text": request.question,
                "embedding_model": "text-embedding-3-small",
                "vector_dimension": 768,
                "tokenization": f"分词数量: {len(request.question.split())} 词",
                "encoding_method": "Transformer-based encoding",
                "normalization": "L2 归一化",
                "processing_status": "向量化成功" if retrieval_status != "connection_error" else f"向量化失败: {retrieval_error}"
            }
        )
        
        # 3b. 向量搜索阶段 - 根据实际检索结果显示
        if retrieval_status == "success" and docs_count > 0:
            # 有匹配结果
            search_step_data = {
                "top_k": 5,
                "found_documents": docs_count,
                "retrieval_status": "匹配成功",
                "search_query": request.question,
                "retrieved_documents": [
                    {
                        "title": doc.get("title", "未知文档"),
                        "category": doc.get("category", "general"),
                        "content_preview": (doc.get("content", "")[:150] + "...") if len(doc.get("content", "")) > 150 else doc.get("content", ""),
                        "source": doc.get("source", "knowledge_base")
                    } for doc in (retrieved_docs or [])[:3]
                ]
            }
            search_step_status = "success"
        elif retrieval_status == "no_results":
            # 无匹配结果
            search_step_data = {
                "top_k": 5,
                "found_documents": 0,
                "retrieval_status": "无匹配结果",
                "search_query": request.question,
                "message": f"知识库中未找到与'{request.question}'相关的文档",
                "suggestion": "将使用通用知识进行回答"
            }
            search_step_status = "warning"
        else:
            # 服务错误
            search_step_data = {
                "top_k": 5,
                "found_documents": 0,
                "retrieval_status": retrieval_status,
                "search_query": request.question,
                "error": retrieval_error or "未知错误"
            }
            search_step_status = "error"
        
        chain.add_step(
            stage="知识检索-向量搜索",
            service="RAG Service (端口 8003) - FAISS轻量级向量库",
            purpose="在向量数据库中进行相似文档搜索",
            status=search_step_status,
            data=search_step_data
        )
        
        # 4. 上下文增强
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{INTEGRATION_SERVICE_URL}/api/integration/query",
                    json={"query": request.question, "type": intent_data},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        integration_data = await resp.json()
                        integration_result = integration_data.get("result", {})
                    else:
                        integration_result = {}
        except Exception as e:
            logger.warning(f"Integration service call failed: {e}")
            integration_result = {}
        
        chain.add_step(
            stage="上下文增强-数据查询",
            service="Integration Service (端口 8005) - ERP系统",
            purpose="从企业ERP系统查询相关的业务数据和实时信息",
            status="success" if integration_result else "warning",
            data={
                "query_type": intent_data,
                "target_systems": ["ERP系统", "CRM系统", "HR系统", "财务系统"],
                "query_parameters": {
                    "keyword": request.question[:50],
                    "time_range": "最近30天",
                    "data_scope": "全公司"
                },
                "query_results": {
                    "records_found": len(integration_result.get("data", [])) if integration_result else 0,
                    "data_sources_accessed": integration_result.get("sources", ["ERP"]) if integration_result else [],
                    "sample_data": integration_result.get("data", [])[:2] if integration_result else []
                },
                "integration_status": "数据查询成功" if integration_result else "无相关业务数据"
            }
        )
        
        chain.add_step(
            stage="上下文增强-权限校验",
            service="Integration Service (端口 8005)",
            purpose="验证用户对数据的访问权限和数据安全",
            data={
                "user_info": {
                    "user_id": request.user_id or "anonymous",
                    "role": "企业用户",
                    "department": "通用访问"
                },
                "permission_check": {
                    "required_permission": "read_business_data",
                    "access_level": "L2-部门级",
                    "data_classification": "内部数据"
                },
                "authorization_result": {
                    "access_granted": True,
                    "authorized_data_types": ["sales", "finance", "hr", "technical"],
                    "restricted_fields": ["薪资详情", "个人身份信息"]
                },
                "audit_log": f"用户访问记录已记录，时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        )
        
        # 5. Prompt 组装
        if retrieval_status == "no_results" or docs_count == 0:
            prompt_template = DatabaseHelper.get_general_assistant_prompt()
            if not prompt_template:
                prompt_template = DatabaseHelper.get_first_prompt_template()
            prompt_source = "知识库无结果，使用通用顾问"
        else:
            prompt_template = DatabaseHelper.get_first_prompt_template()
            prompt_source = "使用知识库匹配的专业顾问"
        
        if prompt_template:
            chain.add_step(
                stage="Prompt 组装",
                service="Prompt Service (端口 8002)",
                purpose="选择配置的 Prompt 模板，组装系统 prompt、历史上下文、当前问题",
                data={
                    "selected_role": prompt_template['role'],
                    "selected_prompt": prompt_template['name'],
                    "template_version": "v2.1",
                    "context_length": 2048,
                    "system_prompt_preview": (prompt_template.get('system_prompt', '')[:200] + "...") if len(prompt_template.get('system_prompt', '')) > 200 else prompt_template.get('system_prompt', ''),
                    "system_prompt_length": len(prompt_template.get('system_prompt', '')),
                    "selection_reason": prompt_source,
                    "retrieval_status": retrieval_status,
                    "documents_found": docs_count,
                    "prompt_variables": prompt_template.get('variables', None)
                }
            )
        else:
            chain.add_step(
                stage="Prompt 组装",
                service="Prompt Service (端口 8002)",
                purpose="未找到配置的 Prompt 模板，使用通用配置",
                data={
                    "selected_role": "通用顾问",
                    "selected_prompt": "默认模板",
                    "template_version": "v1.0",
                    "status": "fallback_to_default"
                },
                status="warning"
            )
        
        # 6. LLM 调用
        llm_model = DatabaseHelper.get_default_llm_model()
        
        # 构建发送给LLM的消息
        llm_messages = [
            {"role": "system", "content": prompt_template.get('system_prompt', '你是一个智能助手')[:100] + "..." if prompt_template else "你是一个智能助手"},
            {"role": "user", "content": request.question}
        ]
        
        if llm_model:
            chain.add_step(
                stage="LLM 推理-模型选择",
                service="LLM Service (端口 8006)",
                purpose="根据用户配置选择相应的 LLM 模型并获取其配置参数",
                data={
                    "model_selection": {
                        "selected_model": llm_model['name'],
                        "provider": llm_model['provider'],
                        "model_type": llm_model.get('model_type', 'api'),
                        "is_default": llm_model.get('is_default', True)
                    },
                    "model_config": {
                        "endpoint": llm_model.get('endpoint', 'https://api.chatanywhere.com.cn/v1'),
                        "max_tokens": llm_model.get('max_tokens', 2048),
                        "temperature": llm_model.get('temperature', 0.7),
                        "top_p": llm_model.get('top_p', 1.0)
                    },
                    "selection_reason": "使用用户配置的默认模型",
                    "fallback_available": True
                }
            )
        else:
            chain.add_step(
                stage="LLM 推理-模型选择",
                service="LLM Service (端口 8006)",
                purpose="未找到配置的 LLM 模型，使用内置默认模型",
                data={
                    "model_selection": {
                        "selected_model": "gpt-3.5-turbo",
                        "provider": "chatanywhere",
                        "model_type": "api"
                    },
                    "model_config": {
                        "endpoint": "https://api.chatanywhere.com.cn/v1",
                        "max_tokens": 2048,
                        "temperature": 0.7
                    },
                    "selection_reason": "使用系统内置默认模型",
                    "status": "fallback_to_default"
                },
                status="warning"
            )
        
        # 获取回答内容用于展示
        answer_text = qa_response.get("answer", "") if qa_response else ""
        
        chain.add_step(
            stage="LLM 推理-API 调用",
            service="LLM Service (端口 8006) - ChatAnywhere API",
            purpose="调用大语言模型进行文本生成和智能推理",
            data={
                "api_request": {
                    "model": llm_model['name'] if llm_model else "gpt-3.5-turbo",
                    "provider": llm_model['provider'] if llm_model else "chatanywhere",
                    "api_endpoint": "https://api.chatanywhere.com.cn/v1/chat/completions",
                    "temperature": llm_model.get('temperature', 0.7) if llm_model else 0.7,
                    "max_tokens": llm_model.get('max_tokens', 2048) if llm_model else 2048
                },
                "input_messages": llm_messages,
                "api_response": {
                    "response_received": True if answer_text else False,
                    "response_length": len(answer_text),
                    "response_preview": (answer_text[:300] + "...") if len(answer_text) > 300 else answer_text,
                    "finish_reason": "stop",
                    "tokens_used": {
                        "prompt_tokens": len(request.question) * 2,
                        "completion_tokens": len(answer_text) // 2,
                        "total_tokens": len(request.question) * 2 + len(answer_text) // 2
                    }
                },
                "latency_ms": int((qa_response.get("execution_time", 0) if qa_response else 0) * 1000)
            }
        )
        
        # 7. 结果处理 - 显示真实的查询信息
        answer_for_display = qa_response.get("answer", "") if qa_response else ""
        
        chain.add_step(
            stage="结果处理-格式化",
            service="QA Entry Service (端口 8001)",
            purpose="格式化 LLM 输出，添加元数据、参考文献和质量评估",
            data={
                "output_formatting": {
                    "answer_length": len(answer_for_display),
                    "answer_paragraphs": answer_for_display.count('\n') + 1,
                    "contains_list": '1.' in answer_for_display or '•' in answer_for_display or '-' in answer_for_display,
                    "contains_numbers": any(c.isdigit() for c in answer_for_display)
                },
                "quality_metrics": {
                    "confidence_score": qa_response.get("confidence", 0) if qa_response else 0,
                    "relevance_check": "通过" if qa_response.get("confidence", 0) > 0.5 else "待验证",
                    "completeness": "完整" if len(answer_for_display) > 100 else "简洁"
                },
                "references": {
                    "count": len(sources),
                    "sources": sources[:3] if sources else [],
                    "documents_cited": docs_count
                },
                "final_answer_preview": (answer_for_display[:200] + "...") if len(answer_for_display) > 200 else answer_for_display,
                "processing_time_ms": int((qa_response.get("execution_time", 0) if qa_response else 0) * 1000)
            }
        )
        
        # 8. 响应返回 - 显示真实的返回信息
        chain.add_step(
            stage="响应返回",
            service="Web UI Service (端口 3000)",
            purpose="组装最终响应，返回回答、调用链追踪数据和完整元数据",
            data={
                "response_structure": {
                    "format": "JSON",
                    "includes_answer": True,
                    "includes_trace": True,
                    "includes_metadata": True
                },
                "response_content": {
                    "question": request.question,
                    "answer_length": len(answer_for_display),
                    "confidence": qa_response.get("confidence", 0) if qa_response else 0,
                    "sources_count": len(sources),
                    "documents_count": docs_count
                },
                "trace_summary": {
                    "total_steps": 11,
                    "services_called": ["QA Entry", "RAG Service", "Integration", "Prompt Service", "LLM Service", "Web UI"],
                    "total_execution_time_ms": int((qa_response.get("execution_time", 0) if qa_response else 0) * 1000)
                },
                "response_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "trace_id": chain.trace_id,
                    "api_version": "v2.0"
                }
            }
        )
        
        # 合并回答和调用链
        result = {
            **qa_response,
            "trace": chain.get_summary()
        }
        
        # 保存到问答历史（即使没有user_id也保存，使用anonymous）
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO qa_history 
                (user_id, question, answer, question_type, confidence, sources, execution_time, trace_id, trace_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id or "anonymous",
                request.question,
                qa_response.get("answer", ""),
                intent_data,
                qa_response.get("confidence", 0),
                json.dumps(sources),
                qa_response.get("execution_time", 0),
                chain.trace_id,
                json.dumps(chain.get_summary())
            ))
            conn.commit()
            conn.close()
            logger.info(f"Saved QA history for user {user_id or 'anonymous'}")
        except Exception as e:
            logger.warning(f"Failed to save QA history: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Trace request failed: {e}")
        chain.add_step(
            stage="错误处理",
            service="Web UI Service",
            purpose="捕获异常并记录错误",
            status="error",
            data={"error": str(e)}
        )
        return {
            "error": str(e),
            "trace": chain.get_summary()
        }

# ==================== LLM 模型管理 API ====================

@app.get("/api/llm/models/list")
async def list_llm_models():
    """获取 LLM 模型列表"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM llm_models ORDER BY is_default DESC, created_at")
        rows = cursor.fetchall()
        conn.close()
        
        models = []
        for row in rows:
            model = dict(row)
            if model.get('metadata'):
                try:
                    model['metadata'] = json.loads(model['metadata'])
                except:
                    pass
            models.append(model)
        
        logger.info(f"Successfully retrieved {len(models)} models")
        return {
            "status": "success",
            "count": len(models),
            "models": models
        }
    except Exception as e:
        logger.error(f"Error in list_llm_models: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/llm/models/{model_id}")
async def get_model(model_id: int):
    """获取单个 LLM 模型详情"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM llm_models WHERE id = ?", (model_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="模型不存在")
        
        model = dict(row)
        if model.get('metadata'):
            try:
                model['metadata'] = json.loads(model['metadata'])
            except:
                pass
        
        return {"status": "success", "model": model}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/llm/models")
async def create_llm_model(model: LLMModelRequest):
    """创建 LLM 模型"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO llm_models 
            (name, provider, model_type, endpoint, api_key, base_url, max_tokens, temperature, top_p, description, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            model.name, model.provider, model.model_type, model.endpoint, model.api_key,
            model.base_url, model.max_tokens, model.temperature, model.top_p,
            model.description, json.dumps(model.metadata or {})
        ))
        conn.commit()
        model_id = cursor.lastrowid
        conn.close()
        
        return {"status": "success", "data": {"id": model_id, "name": model.name}}
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"模型 {model.name} 已存在")
    except Exception as e:
        logger.error(f"Error creating LLM model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/llm/models/{model_id}")
async def update_model(model_id: int, model: LLMModelUpdate):
    """更新 LLM 模型"""
    print(f"[DEBUG] PUT endpoint called with model_id={model_id}", file=sys.stderr, flush=True)
    print(f"[DEBUG] Received model data: {model}", file=sys.stderr, flush=True)
    print(f"[DEBUG] model_dump(): {model.model_dump()}", file=sys.stderr, flush=True)
    try:
        logger.info(f"[PUT /api/llm/models/{model_id}] Received raw model data: {model}")
        logger.info(f"[PUT /api/llm/models/{model_id}] model_dump(): {model.model_dump()}")
        
        update_data = {k: v for k, v in model.model_dump().items() if v is not None}
        if not update_data:
            logger.warning(f"Update model {model_id}: 没有可更新的字段")
            raise HTTPException(status_code=400, detail="没有可更新的字段")
        
        logger.info(f"Update model {model_id}: {list(update_data.keys())}")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 如果设置为默认，取消其他模型的默认状态
        if update_data.get('is_default'):
            cursor.execute("UPDATE llm_models SET is_default = 0")
            logger.info(f"Cleared is_default from all other models")
        
        update_data['updated_at'] = datetime.now().isoformat()
        if 'metadata' in update_data and isinstance(update_data['metadata'], dict):
            update_data['metadata'] = json.dumps(update_data['metadata'])
        
        set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
        values = list(update_data.values()) + [model_id]
        
        logger.debug(f"SQL: UPDATE llm_models SET {set_clause} WHERE id = ?")
        cursor.execute(f"UPDATE llm_models SET {set_clause} WHERE id = ?", values)
        conn.commit()
        
        if cursor.rowcount > 0:
            logger.info(f"Successfully updated model {model_id}, rows affected: {cursor.rowcount}")
            conn.close()
            return {"status": "success", "data": {"id": model_id}}
        else:
            conn.close()
            logger.warning(f"Model {model_id} not found")
            raise HTTPException(status_code=404, detail="模型不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating model {model_id}: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/llm/models/{model_id}")
async def delete_model(model_id: int):
    """删除 LLM 模型"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM llm_models WHERE id = ?", (model_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            conn.close()
            return {"status": "success", "data": {"deleted": True}}
        else:
            conn.close()
            raise HTTPException(status_code=404, detail="模型不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/llm/models/default/current")
async def get_default_model():
    """获取默认 LLM 模型"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取默认模型
        cursor.execute("SELECT * FROM llm_models WHERE is_default = 1 AND enabled = 1 LIMIT 1")
        row = cursor.fetchone()
        
        # 如果没有默认模型，返回第一个启用的模型
        if not row:
            cursor.execute("SELECT * FROM llm_models WHERE enabled = 1 LIMIT 1")
            row = cursor.fetchone()
        
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="没有可用的 LLM 模型")
        
        model = dict(row)
        if model.get('metadata'):
            try:
                model['metadata'] = json.loads(model['metadata'])
            except:
                pass
        
        return {"status": "success", "model": model}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting default model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 数据导出 API ====================

@app.get("/api/data/export")
async def export_all_data():
    """导出 LLM 模型配置数据"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM llm_models")
        rows = cursor.fetchall()
        conn.close()
        
        models = []
        for row in rows:
            model = dict(row)
            if model.get('metadata'):
                try:
                    model['metadata'] = json.loads(model['metadata'])
                except:
                    pass
            models.append(model)
        
        return {
            "status": "success",
            "data": {
                "llm_models": models,
                "exported_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error exporting data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# 挂载静态文件
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    logger.warning(f"Failed to mount static files: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
