import os
import sys
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import aiohttp

from config import get_settings
from models import QuestionRequest, QuestionResponse, ProcessingStatus
from services import QAProcessor, QuestionClassifier, ContextBuilder
from utils import setup_logging

# ==================== 日志配置 ====================
logger = setup_logging(__name__)

# ==================== FastAPI应用 ====================
app = FastAPI(
    title="AI Common Platform - QA Entry Service",
    description="企业级AI问答入口服务",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 依赖注入 ====================
settings = get_settings()

# 内存缓存（轻量级模式，替代Redis）
qa_cache: Dict[str, Dict] = {}

async def get_qa_processor() -> QAProcessor:
    """获取QA处理器"""
    return QAProcessor(
        settings=settings,
        redis=None  # 轻量级模式不使用Redis
    )

# ==================== 模型定义 ====================
class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: str
    service: str
    version: str

# ==================== 路由 ====================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        service="qa_entry",
        version="1.0.0"
    )

@app.post("/api/qa/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    processor: QAProcessor = Depends(get_qa_processor)
):
    """
    接收用户问题并返回答案
    
    参数：
    - question: 用户提问
    - user_id: 用户ID
    - session_id: 会话ID（可选）
    - context: 额外上下文（可选）
    
    返回：
    - id: 问题ID
    - question: 原始问题
    - answer: 生成的答案
    - sources: 数据来源
    - confidence: 置信度
    - execution_time: 执行时间
    - status: 处理状态
    """
    qa_id = str(uuid.uuid4())
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"🆕 [QA #{qa_id[:8]}] 收到问题: {request.question}")
        logger.info(f"👤 用户: {request.user_id}")
        logger.info(f"{'='*60}\n")
        
        # 1. 缓存问题（内存）
        qa_cache[qa_id] = {
            "question": request.question,
            "user_id": request.user_id,
            "timestamp": start_time.isoformat()
        }
        
        # 2. 分类问题
        logger.info("📂 第一步: 问题分类...")
        classifier = QuestionClassifier()
        question_type = classifier.classify(request.question)
        logger.info(f"   ✓ 问题分类: {question_type}\n")
        
        # 3. 构建处理上下文
        logger.info("🔗 第二步: 构建处理上下文...")
        context_builder = ContextBuilder(settings=settings)
        context = await context_builder.build(
            question=request.question,
            user_id=request.user_id,
            question_type=question_type,
            extra_context=request.context
        )
        logger.info(f"   ✓ 上下文构建完成\n")
        
        # 4. 路由到对应处理器
        logger.info("⚙️  第三步: 处理问题...")
        answer_data = await processor.process(
            question_id=qa_id,
            question=request.question,
            question_type=question_type,
            context=context,
            user_id=request.user_id
        )
        
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ [QA #{qa_id[:8]}] 问题处理完成")
        logger.info(f"⏱️  总耗时: {execution_time:.2f}秒")
        logger.info(f"📊 数据来源: {answer_data.get('sources', [])}")
        logger.info(f"{'='*60}\n")
        
        response = QuestionResponse(
            id=qa_id,
            question=request.question,
            answer=answer_data.get("answer", ""),
            sources=answer_data.get("sources", []),
            confidence=answer_data.get("confidence", 0.0),
            execution_time=execution_time,
            question_type=question_type,
            status=ProcessingStatus.COMPLETED
        )
        
        # 缓存响应
        qa_cache[qa_id]["response"] = response.dict()
        
        return response
        
    except Exception as e:
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ [QA #{qa_id[:8]}] 处理问题时出错")
        logger.error(f"🔴 错误: {str(e)}")
        logger.error(f"{'='*60}\n", exc_info=True)
        
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        
        raise HTTPException(
            status_code=500,
            detail={
                "id": qa_id,
                "error": str(e),
                "execution_time": execution_time,
                "status": ProcessingStatus.FAILED
            }
        )

@app.get("/api/qa/{qa_id}")
async def get_question_history(qa_id: str):
    """获取历史问答记录"""
    try:
        if qa_id not in qa_cache:
            raise HTTPException(status_code=404, detail="问答记录不存在")
        
        return {
            "id": qa_id,
            "data": qa_cache[qa_id]
        }
    except Exception as e:
        logger.error(f"获取历史记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/qa/batch")
async def batch_questions(
    requests: List[QuestionRequest],
    processor: QAProcessor = Depends(get_qa_processor)
):
    """批量处理问题"""
    results = []
    for req in requests:
        try:
            # 调用单个问题处理
            result = await ask_question(req, processor)
            results.append(result)
        except Exception as e:
            logger.error(f"批量处理中出错: {str(e)}")
            results.append({"error": str(e)})
    
    return {"results": results, "total": len(requests), "succeeded": len([r for r in results if "error" not in r])}

@app.get("/api/qa/stats")
async def get_stats():
    """获取统计信息"""
    try:
        total_questions = len(qa_cache)
        
        return {
            "total_questions": total_questions,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 启动和关闭事件 ====================
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("QA Entry Service 启动中（轻量级模式，无Redis依赖）...")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("QA Entry Service 关闭中...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


# ==================== 日志配置 ====================
logger = setup_logging(__name__)

# ==================== FastAPI应用 ====================
app = FastAPI(
    title="AI Common Platform - QA Entry Service",
    description="企业级AI问答入口服务",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 依赖注入 ====================
settings = get_settings()

# 内存缓存（轻量级模式，替代Redis）
qa_cache: Dict[str, Dict] = {}

async def get_qa_processor() -> QAProcessor:
    """获取QA处理器"""
    return QAProcessor(
        settings=settings,
        redis=None  # 轻量级模式不使用Redis
    )

# ==================== 模型定义 ====================
class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: str
    service: str
    version: str

# ==================== 路由 ====================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        service="qa_entry",
        version="1.0.0"
    )

@app.post("/api/qa/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    processor: QAProcessor = Depends(get_qa_processor)
):
    """
    接收用户问题并返回答案
    
    参数：
    - question: 用户提问
    - user_id: 用户ID
    - session_id: 会话ID（可选）
    - context: 额外上下文（可选）
    
    返回：
    - id: 问题ID
    - question: 原始问题
    - answer: 生成的答案
    - sources: 数据来源
    - confidence: 置信度
    - execution_time: 执行时间
    - status: 处理状态
    """
    qa_id = str(uuid.uuid4())
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"\n{'='*60}")
        logger.info(f"🆕 [QA #{qa_id[:8]}] 收到问题: {request.question}")
        logger.info(f"👤 用户: {request.user_id}")
        logger.info(f"{'='*60}\n")
        
        # 1. 缓存问题（内存）
        qa_cache[qa_id] = {
            "question": request.question,
            "user_id": request.user_id,
            "timestamp": start_time.isoformat()
        }
        
        # 2. 分类问题
        logger.info("📂 第一步: 问题分类...")
        classifier = QuestionClassifier()
        question_type = classifier.classify(request.question)
        logger.info(f"   ✓ 问题分类: {question_type}\n")
        
        # 3. 构建处理上下文
        logger.info("🔗 第二步: 构建处理上下文...")
        context_builder = ContextBuilder(settings=settings)
        context = await context_builder.build(
            question=request.question,
            user_id=request.user_id,
            question_type=question_type,
            extra_context=request.context
        )
        logger.info(f"   ✓ 上下文构建完成\n")
        
        # 4. 路由到对应处理器
        logger.info("⚙️  第三步: 处理问题...")
        answer_data = await processor.process(
            question_id=qa_id,
            question=request.question,
            question_type=question_type,
            context=context,
            user_id=request.user_id
        )
        
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ [QA #{qa_id[:8]}] 问题处理完成")
        logger.info(f"⏱️  总耗时: {execution_time:.2f}秒")
        logger.info(f"📊 数据来源: {answer_data.get('sources', [])}")
        logger.info(f"{'='*60}\n")
        
        response = QuestionResponse(
            id=qa_id,
            question=request.question,
            answer=answer_data.get("answer", ""),
            sources=answer_data.get("sources", []),
            confidence=answer_data.get("confidence", 0.0),
            execution_time=execution_time,
            question_type=question_type,
            status=ProcessingStatus.COMPLETED
        )
        
        # 缓存响应
        qa_cache[qa_id]["response"] = response.dict()
        
        return response
        
    except Exception as e:
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ [QA #{qa_id[:8]}] 处理问题时出错")
        logger.error(f"🔴 错误: {str(e)}")
        logger.error(f"{'='*60}\n", exc_info=True)
        
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()
        
        raise HTTPException(
            status_code=500,
            detail={
                "id": qa_id,
                "error": str(e),
                "execution_time": execution_time,
                "status": ProcessingStatus.FAILED
            }
        )

@app.get("/api/qa/{qa_id}")
async def get_question_history(qa_id: str):
    """获取历史问答记录"""
    try:
        if qa_id not in qa_cache:
            raise HTTPException(status_code=404, detail="问答记录不存在")
        
        return {
            "id": qa_id,
            "data": qa_cache[qa_id]
        }
    except Exception as e:
        logger.error(f"获取历史记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/qa/batch")
async def batch_questions(
    requests: List[QuestionRequest],
    processor: QAProcessor = Depends(get_qa_processor)
):
    """批量处理问题"""
    results = []
    for req in requests:
        try:
            # 调用单个问题处理
            result = await ask_question(req, processor)
            results.append(result)
        except Exception as e:
            logger.error(f"批量处理中出错: {str(e)}")
            results.append({"error": str(e)})
    
    return {"results": results, "total": len(requests), "succeeded": len([r for r in results if "error" not in r])}

@app.get("/api/qa/stats")
async def get_stats():
    """获取统计信息"""
    try:
        total_questions = len(qa_cache)
        
        return {
            "total_questions": total_questions,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 启动和关闭事件 ====================
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    logger.info("QA Entry Service 启动中（轻量级模式，无Redis依赖）...")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    logger.info("QA Entry Service 关闭中...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
