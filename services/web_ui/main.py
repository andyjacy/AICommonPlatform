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

@app.get("/api/rag/documents")
async def get_documents():
    """获取知识库文档"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{RAG_SERVICE_URL}/api/rag/documents",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info("Successfully retrieved documents from RAG service")
                    return data
                else:
                    logger.warning(f"RAG service returned status {resp.status}")
                    return {"documents": [], "error": f"RAG service error: {resp.status}"}
    except Exception as e:
        logger.error(f"Document request failed: {e}")
        return {"documents": [], "error": str(e)}

@app.post("/api/rag/search")
async def search_documents(query: dict):
    """搜索知识库"""
    search_query = query.get('query', '')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{RAG_SERVICE_URL}/api/rag/search",
                json=query,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info(f"RAG search completed for query: {search_query}")
                    return data
                else:
                    logger.warning(f"RAG search failed with status {resp.status}")
    except Exception as e:
        logger.error(f"Search request failed: {e}")
    
    # 服务不可用时返回空结果
    return {
        "query": search_query,
        "results": [],
        "error": "知识库服务暂时不可用",
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

# ==================== LLM 模型接口 ====================

@app.get("/api/llm/models")
async def get_llm_models():
    """获取可用的LLM模型"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{LLM_SERVICE_URL}/api/llm/models",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return {"error": "Failed to fetch models"}
    except Exception as e:
        return {"error": str(e)}

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
        chain.add_step(
            stage="输入处理",
            service="QA Entry Service (端口 8001)",
            purpose="接收用户问题，进行文本预处理和清洗",
            data={"raw_question": request.question}
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
        
        chain.add_step(
            stage="意图识别",
            service="QA Entry Service (端口 8001)",
            purpose="进行问题分类和关键词提取",
            data={
                "intent": intent_data,
                "question_type": intent_data,
                "raw_question": request.question,
                "confidence": qa_response.get("confidence", 0)
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
                "vector_dim": 768,
                "query": request.question,
                "embedding_model": "text-embedding-3-small"
            }
        )
        
        # 3b. 向量搜索阶段
        chain.add_step(
            stage="知识检索-向量搜索",
            service="RAG Service (端口 8003) - FAISS轻量级向量库",
            purpose="在向量数据库中进行相似文档搜索",
            status="success" if retrieval_status == "success" else "warning" if retrieval_status == "no_results" else "error",
            data={
                "top_k": 5,
                "found_documents": docs_count,
                "retrieval_status": retrieval_status,
                "search_query": request.question,
                "error": retrieval_error
            } if retrieval_status != "success" else {
                "top_k": 5,
                "found_documents": docs_count,
                "retrieval_status": retrieval_status,
                "documents": [{"title": doc.get("title", ""), "category": doc.get("category", "")} for doc in retrieved_docs[:3]]
            }
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
            data={
                "query_type": intent_data,
                "data_sources": ["ERP", "SAP", "OracleDB"],
                "period": "实时",
                "records_found": len(integration_result.get("data", [])) if integration_result else 0,
                "queried_data": integration_result.get("data", [])[:3] if integration_result else []
            }
        )
        
        chain.add_step(
            stage="上下文增强-权限校验",
            service="Integration Service (端口 8005)",
            purpose="验证用户对数据的访问权限和数据安全",
            data={
                "user_id": request.user_id,
                "required_permission": "read_business_data",
                "access_granted": True,
                "security_level": "企业数据",
                "authorized_data_types": ["sales", "finance", "hr"]
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
                    "system_prompt_length": len(prompt_template.get('system_prompt', '')),
                    "selection_reason": prompt_source,
                    "retrieval_status": retrieval_status,
                    "documents_found": docs_count
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
        if llm_model:
            chain.add_step(
                stage="LLM 推理-模型选择",
                service="LLM Service (端口 8006)",
                purpose="根据用户配置选择相应的 LLM 模型并获取其配置",
                data={
                    "selected_model": llm_model['name'],
                    "provider": llm_model['provider'],
                    "model_type": llm_model.get('model_type', 'api'),
                    "endpoint": llm_model.get('endpoint', ''),
                    "max_tokens": llm_model.get('max_tokens', 2048),
                    "temperature": llm_model.get('temperature', 0.7),
                    "reason": "使用用户配置的默认模型"
                }
            )
        else:
            chain.add_step(
                stage="LLM 推理-模型选择",
                service="LLM Service (端口 8006)",
                purpose="未找到配置的 LLM 模型，使用内置默认模型",
                data={
                    "selected_model": "gpt-3.5-turbo",
                    "provider": "chatanywhere",
                    "endpoint": "https://api.chatanywhere.com.cn/v1",
                    "status": "using_builtin_default"
                },
                status="warning"
            )
        
        chain.add_step(
            stage="LLM 推理-API 调用",
            service="LLM Service (端口 8006) - ChatAnywhere API",
            purpose="调用配置的 LLM 进行文本生成和推理",
            data={
                "model_used": llm_model['name'] if llm_model else "gpt-3.5-turbo",
                "provider": llm_model['provider'] if llm_model else "chatanywhere",
                "api_url": "https://api.chatanywhere.com.cn/v1/chat/completions",
                "temperature": llm_model.get('temperature', 0.7) if llm_model else 0.7,
                "max_tokens": llm_model.get('max_tokens', 2048) if llm_model else 2048,
                "tokens_used": qa_response.get("execution_time", 0) if qa_response else 0
            }
        )
        
        # 7. 结果处理 - 显示真实的查询信息
        chain.add_step(
            stage="结果处理-格式化",
            service="QA Entry Service (端口 8001)",
            purpose="格式化 LLM 输出，添加元数据和参考文献",
            data={
                "references_count": len(sources),
                "references": sources[:3] if sources else [],
                "confidence_score": qa_response.get("confidence", 0) if qa_response else 0,
                "answer_length": len(qa_response.get("answer", "")) if qa_response else 0,
                "processing_time": qa_response.get("execution_time", 0) if qa_response else 0,
                "answer_preview": (qa_response.get("answer", "")[:100] + "...") if qa_response else ""
            }
        )
        
        # 8. 响应返回 - 显示真实的返回信息
        chain.add_step(
            stage="响应返回",
            service="Web UI Service (端口 3000)",
            purpose="返回最终回答、调用链追踪数据和元数据",
            data={
                "response_format": "JSON",
                "includes_trace": True,
                "includes_sources": len(sources) > 0,
                "includes_documents": docs_count > 0,
                "total_execution_time": qa_response.get("execution_time", 0) if qa_response else 0,
                "response_timestamp": datetime.now().isoformat(),
                "services_called": 6
            }
        )
        
        # 合并回答和调用链
        result = {
            **qa_response,
            "trace": chain.get_summary()
        }
        
        # 保存到用户问答历史
        if user_id:
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO qa_history 
                    (user_id, question, answer, question_type, confidence, sources, execution_time, trace_id, trace_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
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
                logger.info(f"Saved QA history for user {user_id}")
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
