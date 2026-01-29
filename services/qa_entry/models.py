from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

class ProcessingStatus(str, Enum):
    """处理状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"

class QuestionRequest(BaseModel):
    """问题请求模型"""
    question: str = Field(..., description="用户问题")
    user_id: str = Field(..., description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="额外上下文")
    
    class Config:
        schema_extra = {
            "example": {
                "question": "今年Q1的销售额是多少?",
                "user_id": "user123",
                "session_id": "session_456",
                "context": {"department": "sales"}
            }
        }

class QuestionResponse(BaseModel):
    """问题响应模型"""
    id: str = Field(..., description="问题ID")
    question: str = Field(..., description="原始问题")
    answer: str = Field(..., description="生成的答案")
    sources: List[str] = Field(default_factory=list, description="数据来源")
    confidence: float = Field(default=0.0, description="置信度(0-1)")
    execution_time: float = Field(..., description="执行时间(秒)")
    question_type: Optional[str] = Field(None, description="问题分类")
    status: ProcessingStatus = Field(..., description="处理状态")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "qa_123abc",
                "question": "今年Q1的销售额是多少?",
                "answer": "根据我们的数据，Q1总销售额为5000万元，同比增长15%。",
                "sources": ["rag_doc_1", "system_call_erp"],
                "confidence": 0.95,
                "execution_time": 2.5,
                "question_type": "sales_inquiry",
                "status": "completed"
            }
        }

class ClassificationResult(BaseModel):
    """分类结果"""
    question_type: str
    confidence: float
    category: str
    sub_category: Optional[str] = None

class ContextData(BaseModel):
    """上下文数据"""
    user_profile: Dict[str, Any] = Field(default_factory=dict)
    department: Optional[str] = None
    role: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    extra: Dict[str, Any] = Field(default_factory=dict)
