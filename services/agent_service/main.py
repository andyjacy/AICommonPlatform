from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json

app = FastAPI(
    title="AI Common Platform - Agent Service",
    description="Agent执行和工具调用服务",
    version="1.0.0"
)

# ==================== 枚举 ====================
class ToolType(str, Enum):
    """工具类型"""
    ERP = "erp"
    CRM = "crm"
    HRM = "hrm"
    FINANCIAL = "financial"
    DATA_ANALYSIS = "data_analysis"

class ExecutionStatus(str, Enum):
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

# ==================== 模型 ====================
class Tool(BaseModel):
    """Agent工具"""
    id: str
    name: str
    description: str
    tool_type: ToolType
    parameters: Dict[str, Any] = {}
    endpoint: Optional[str] = None

class AgentTask(BaseModel):
    """Agent任务"""
    id: Optional[str] = None
    question: str
    tools: List[str]  # 工具IDs
    context: Dict[str, Any] = {}
    created_at: Optional[datetime] = None

class TaskResult(BaseModel):
    """任务执行结果"""
    task_id: str
    status: ExecutionStatus
    results: Dict[str, Any] = {}
    executed_tools: List[str] = []
    execution_time: float
    error_message: Optional[str] = None

# ==================== 预定义工具 ====================
TOOLS = {
    "erp_sales": Tool(
        id="erp_sales",
        name="ERP销售查询",
        description="从ERP系统查询销售数据",
        tool_type=ToolType.ERP,
        parameters={"time_range": "str", "department": "str"}
    ),
    "hrm_employee": Tool(
        id="hrm_employee",
        name="人资员工查询",
        description="从HRM系统查询员工信息",
        tool_type=ToolType.HRM,
        parameters={"department": "str", "status": "str"}
    ),
    "financial_budget": Tool(
        id="financial_budget",
        name="财务预算查询",
        description="从财务系统查询预算信息",
        tool_type=ToolType.FINANCIAL,
        parameters={"year": "int", "department": "str"}
    ),
}

# ==================== 工具执行模拟 ====================
def execute_tool(tool_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """执行工具"""
    
    if tool_id == "erp_sales":
        return {
            "tool": tool_id,
            "status": "success",
            "data": {
                "Q1": {"amount": 5000, "growth": 0.15},
                "Q2": {"amount": 5500, "growth": 0.10},
                "currency": "万元"
            }
        }
    elif tool_id == "hrm_employee":
        return {
            "tool": tool_id,
            "status": "success",
            "data": {
                "total_employees": 500,
                "departments": {
                    "sales": 100,
                    "technical": 200,
                    "admin": 100,
                    "hr": 50,
                    "finance": 50
                }
            }
        }
    elif tool_id == "financial_budget":
        return {
            "tool": tool_id,
            "status": "success",
            "data": {
                "total_budget": 2000,
                "allocation": {
                    "research": 0.40,
                    "operations": 0.35,
                    "marketing": 0.25
                },
                "currency": "万元"
            }
        }
    else:
        return {
            "tool": tool_id,
            "status": "failed",
            "error": "未知的工具"
        }

# ==================== 路由 ====================

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "agent_service"}

@app.get("/api/agent/tools")
async def list_tools():
    """获取可用工具列表"""
    return {
        "tools": list(TOOLS.values()),
        "total": len(TOOLS)
    }

@app.get("/api/agent/tools/{tool_id}")
async def get_tool(tool_id: str):
    """获取特定工具信息"""
    tool = TOOLS.get(tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="工具不存在")
    return tool

@app.post("/api/agent/execute", response_model=TaskResult)
async def execute_task(task: AgentTask):
    """
    执行Agent任务
    
    参数：
    - question: 任务问题
    - tools: 需要使用的工具列表
    - context: 执行上下文
    
    返回：
    - 执行结果
    """
    import time
    import uuid
    
    task_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        results = {}
        executed_tools = []
        
        # 执行每个工具
        for tool_id in task.tools:
            if tool_id not in TOOLS:
                continue
            
            tool_result = execute_tool(tool_id, task.context)
            results[tool_id] = tool_result
            if tool_result.get("status") == "success":
                executed_tools.append(tool_id)
        
        execution_time = time.time() - start_time
        
        return TaskResult(
            task_id=task_id,
            status=ExecutionStatus.SUCCESS if executed_tools else ExecutionStatus.FAILED,
            results=results,
            executed_tools=executed_tools,
            execution_time=execution_time
        )
    except Exception as e:
        execution_time = time.time() - start_time
        return TaskResult(
            task_id=task_id,
            status=ExecutionStatus.FAILED,
            execution_time=execution_time,
            error_message=str(e)
        )

@app.post("/api/agent/workflow")
async def create_workflow(workflow_definition: Dict[str, Any]):
    """创建工作流"""
    # 简化的工作流创建
    return {
        "message": "工作流创建成功",
        "workflow_id": "wf_123",
        "definition": workflow_definition
    }

@app.get("/api/agent/tasks/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    # 模拟返回
    return {
        "task_id": task_id,
        "status": "completed",
        "created_at": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
