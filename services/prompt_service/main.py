from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

app = FastAPI(
    title="AI Common Platform - Prompt Service",
    description="提示词管理和组装服务",
    version="1.0.0"
)

# ==================== 模型 ====================
class PromptTemplate(BaseModel):
    """提示词模板"""
    id: Optional[str] = None
    name: str
    role: str
    description: str
    template_content: str
    version: str = "1.0"
    variables: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PromptAssemblyRequest(BaseModel):
    """提示词组装请求"""
    template_id: str
    variables: Dict[str, Any]
    role: str
    context: Optional[Dict[str, Any]] = None

class PromptAssemblyResponse(BaseModel):
    """提示词组装响应"""
    prompt: str
    template_id: str
    role: str
    variable_count: int

# ==================== 预定义提示词模板 ====================
PROMPT_TEMPLATES = {
    "sales_advisor": PromptTemplate(
        id="sales_advisor",
        name="销售顾问",
        role="Sales Advisor",
        description="专注于销售数据和客户信息的顾问",
        template_content="""你是一名专业的销售顾问，具备以下特点：
- 专业的销售知识和行业经验
- 关注销售数据、客户信息、市场趋势
- 提供数据驱动的建议

用户问题：{question}
销售数据上下文：{sales_data}
客户信息：{customer_info}

请提供专业的销售建议：""",
        variables=["question", "sales_data", "customer_info"]
    ),
    "hr_advisor": PromptTemplate(
        id="hr_advisor",
        name="人资顾问",
        role="HR Advisor",
        description="专注于员工信息和薪资福利的顾问",
        template_content="""你是一名专业的人力资源顾问，具备以下特点：
- 人力资源管理的专业知识
- 关注员工信息、薪资福利、考勤记录
- 遵守相关法规和公司政策

用户问题：{question}
员工信息：{employee_info}
福利政策：{benefits_policy}

请提供专业的HR建议：""",
        variables=["question", "employee_info", "benefits_policy"]
    ),
    "tech_advisor": PromptTemplate(
        id="tech_advisor",
        name="技术顾问",
        role="Technical Advisor",
        description="专注于系统架构和技术方案的顾问",
        template_content="""你是一名资深技术架构师，具备以下特点：
- 深厚的技术知识和系统设计经验
- 关注系统架构、技术栈、最佳实践
- 提供可行的技术解决方案

用户问题：{question}
系统架构：{system_architecture}
技术约束：{technical_constraints}

请提供专业的技术建议：""",
        variables=["question", "system_architecture", "technical_constraints"]
    ),
    "finance_advisor": PromptTemplate(
        id="finance_advisor",
        name="财务顾问",
        role="Finance Advisor",
        description="专注于财务数据和预算的顾问",
        template_content="""你是一名专业的财务顾问，具备以下特点：
- 财务分析和会计知识
- 关注财务数据、预算、成本分析
- 提供数据驱动的财务建议

用户问题：{question}
财务数据：{financial_data}
预算信息：{budget_info}

请提供专业的财务建议：""",
        variables=["question", "financial_data", "budget_info"]
    )
}

# ==================== 路由 ====================

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "prompt_service"}

@app.get("/api/prompts")
async def list_templates():
    """获取所有提示词模板"""
    return {
        "templates": list(PROMPT_TEMPLATES.values()),
        "total": len(PROMPT_TEMPLATES)
    }

@app.get("/api/prompts/{template_id}")
async def get_template(template_id: str):
    """获取特定模板"""
    template = PROMPT_TEMPLATES.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template

@app.post("/api/prompts/assemble", response_model=PromptAssemblyResponse)
async def assemble_prompt(request: PromptAssemblyRequest):
    """
    组装提示词
    
    参数：
    - template_id: 模板ID
    - variables: 变量字典
    - role: 角色名称
    - context: 额外上下文
    
    返回：
    - 组装好的提示词
    """
    template = PROMPT_TEMPLATES.get(request.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    try:
        # 组装提示词
        prompt_content = template.template_content.format(**request.variables)
        
        # 如果有额外上下文，添加到提示词
        if request.context:
            context_str = "\n额外信息：\n" + json.dumps(request.context, ensure_ascii=False, indent=2)
            prompt_content += context_str
        
        return PromptAssemblyResponse(
            prompt=prompt_content,
            template_id=request.template_id,
            role=template.role,
            variable_count=len(request.variables)
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"缺少必需变量: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prompts/create")
async def create_template(template: PromptTemplate):
    """创建新模板"""
    if template.id in PROMPT_TEMPLATES:
        raise HTTPException(status_code=400, detail="模板ID已存在")
    
    template.created_at = datetime.utcnow()
    template.updated_at = datetime.utcnow()
    PROMPT_TEMPLATES[template.id] = template
    
    return {"message": "模板创建成功", "template": template}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
