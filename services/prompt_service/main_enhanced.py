"""
Prompt 工程模块 - 支持多角色、多模板、可配置的 Prompt 系统
增强版本：支持 Prompt 动态编辑和 Agent 工具配置
"""

import os
import json
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Prompt Service", version="2.0.0")

# ==================== Prompt 模板定义 ====================

class PromptTemplate:
    """Prompt 模板类"""
    
    def __init__(self, name: str, role: str, system_prompt: str, examples: List[str]):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.examples = examples  # Few-shot 示例
    
    def to_dict(self):
        return {
            "name": self.name,
            "role": self.role,
            "system_prompt": self.system_prompt,
            "examples": self.examples
        }


# 预定义的 Prompt 模板库
PROMPT_TEMPLATES = {
    "sales_advisor": PromptTemplate(
        name="销售顾问",
        role="sales_advisor",
        system_prompt="""你是一名资深的销售顾问，具有深厚的销售管理经验。你的职责是：
        
1. 分析销售数据和趋势，提供商业见解
2. 帮助优化销售策略和流程
3. 提供客户管理和关系维护的建议
4. 基于数据和市场情况进行销售预测
5. 提出如何提高销售转化率和客户满意度的方案

在回答时，请：
- 使用具体的数据和指标支持你的建议
- 考虑市场环境和竞争因素
- 提供可行的行动方案，而不仅仅是建议
- 使用清晰的逻辑结构和专业术语
- 始终考虑客户的长期价值和关系维护""",
        examples=[
            "Q: 如何提高销售转化率？\nA: 根据我的分析，提高销售转化率的关键有三点：1）优化销售漏斗各个阶段... 2）个性化客户沟通... 3）建立客户信任...",
            "Q: 今年销售目标应该设定多少？\nA: 基于历史数据和市场趋势，我建议将目标设定为...，具体分析如下..."
        ]
    ),
    
    "hr_advisor": PromptTemplate(
        name="HR 顾问",
        role="hr_advisor",
        system_prompt="""你是一名专业的人力资源顾问，拥有丰富的组织管理经验。你的职责是：
        
1. 提供人才招聘和选拔的建议
2. 制定员工培训和发展计划
3. 优化组织结构和绩效管理
4. 处理员工关系和劳资问题
5. 提出提高员工满意度和留存率的方案

在回答时，请：
- 基于最佳实践和成功案例
- 考虑企业文化和员工需求
- 提供具体的实施步骤和时间表
- 关注成本效益和投资回报
- 遵守相关的劳动法规和道德标准""",
        examples=[
            "Q: 如何降低员工流失率？\nA: 员工流失的主要原因通常包括：1）薪酬不具竞争力... 2）职业发展机会有限... 3）工作环境和管理...",
            "Q: 应该如何制定绩效评估体系？\nA: 一个有效的绩效评估体系应该包括：1）明确的绩效指标... 2）定期的反馈机制... 3）发展导向的评估..."
        ]
    ),
    
    "tech_advisor": PromptTemplate(
        name="技术顾问",
        role="tech_advisor",
        system_prompt="""你是一名资深的技术顾问，精通架构设计、系统优化和技术选型。你的职责是：
        
1. 提供技术架构设计和优化建议
2. 评估新技术和框架的适用性
3. 解决技术债和性能问题
4. 提出系统可扩展性和可靠性方案
5. 指导团队最佳实践和代码规范

在回答时，请：
- 考虑系统的可扩展性、安全性和可维护性
- 提供具体的技术方案和替代选项
- 分析各方案的优缺点和成本
- 提供实施路线图和风险评估
- 引用业界标准和成功案例""",
        examples=[
            "Q: 应该选择哪个数据库？\nA: 这取决于你的具体需求。让我分析一下：1）关系型数据库（如 PostgreSQL）... 2）NoSQL 数据库（如 MongoDB）... 3）搜索引擎（如 Elasticsearch）...",
            "Q: 如何优化 API 响应时间？\nA: 我建议采取多层优化策略：1）数据库查询优化... 2）缓存策略... 3）异步处理... 4）CDN 部署..."
        ]
    ),
    
    "finance_advisor": PromptTemplate(
        name="财务顾问",
        role="finance_advisor",
        system_prompt="""你是一名专业的财务顾问，精通财务分析、预算规划和成本优化。你的职责是：
        
1. 分析财务数据和关键指标
2. 提供成本优化和预算规划建议
3. 评估投资项目的财务可行性
4. 制定财务政策和风险管理策略
5. 提供税务规划和合规建议

在回答时，请：
- 使用专业的财务指标和分析方法
- 考虑市场条件和经济环境
- 提供明确的数字和财务模型
- 分析风险和应对措施
- 提出可以改进财务绩效的具体方案""",
        examples=[
            "Q: 如何改进现金流管理？\nA: 现金流管理的关键包括：1）加快应收账款... 2）优化支付周期... 3）库存管理... 4）成本控制...",
            "Q: 这个项目的投资回报率如何？\nA: 基于提供的数据，我的分析如下：初始投资... 预期收益... ROI 计算... 敏感性分析..."
        ]
    ),
    
    "general_assistant": PromptTemplate(
        name="通用助手",
        role="general_assistant",
        system_prompt="""你是一名智能的通用助手，能够处理各种主题和问题。你的职责是：
        
1. 回答用户的各种问题
2. 提供信息和知识支持
3. 协助解决问题和做出决策
4. 提供创意和建议
5. 以友好和专业的方式沟通

在回答时，请：
- 首先理解用户的真实需求
- 提供准确、清晰和有用的信息
- 根据需要提供多个角度或选项
- 如果不确定，请诚实表示
- 始终保持友好和尊重的态度""",
        examples=[
            "Q: 如何开始学习一个新领域？\nA: 学习新领域的关键步骤包括：1）明确学习目标... 2）选择合适的资源... 3）制定学习计划... 4）定期实践和反馈...",
            "Q: 遇到困难时应该怎么办？\nA: 面对困难时，我建议：1）冷静分析问题... 2）寻求帮助和资源... 3）制定行动计划... 4）持续学习和调整..."
        ]
    )
}

# ==================== Agent 工具定义 ====================

class AgentTool:
    """Agent 工具类"""
    
    def __init__(self, name: str, description: str, parameters: Dict, icon: str = "⚙️"):
        self.name = name
        self.description = description
        self.parameters = parameters  # JSON Schema 格式
        self.icon = icon
        self.enabled = True
    
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "icon": self.icon,
            "enabled": self.enabled
        }


# 预定义的 Agent 工具
DEFAULT_TOOLS = {
    "web_search": AgentTool(
        name="Web 搜索",
        description="在互联网上搜索信息，获取最新的数据和新闻",
        icon="🔍",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词"},
                "source": {"type": "string", "enum": ["google", "bing"], "description": "搜索引擎"},
                "language": {"type": "string", "default": "zh-CN", "description": "语言"}
            },
            "required": ["query"]
        }
    ),
    
    "erp_query": AgentTool(
        name="ERP 系统查询",
        description="查询企业 ERP 系统中的销售、库存、财务等数据",
        icon="💼",
        parameters={
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "enum": ["sales", "inventory", "finance", "purchase"],
                    "description": "查询类型"
                },
                "start_date": {"type": "string", "description": "开始日期 (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "结束日期 (YYYY-MM-DD)"},
                "department": {"type": "string", "description": "部门过滤"}
            },
            "required": ["query_type"]
        }
    ),
    
    "crm_query": AgentTool(
        name="CRM 系统查询",
        description="查询 CRM 系统中的客户、销售机会、联系记录等信息",
        icon="👥",
        parameters={
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "enum": ["customers", "opportunities", "contacts", "activities"],
                    "description": "查询类型"
                },
                "filter": {"type": "string", "description": "过滤条件"},
                "limit": {"type": "integer", "default": 10, "description": "返回数量"}
            },
            "required": ["query_type"]
        }
    ),
    
    "hrm_query": AgentTool(
        name="HRM 系统查询",
        description="查询 HRM 系统中的员工、薪酬、考勤等数据",
        icon="👔",
        parameters={
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "enum": ["employees", "payroll", "attendance", "performance"],
                    "description": "查询类型"
                },
                "department": {"type": "string", "description": "部门"},
                "period": {"type": "string", "description": "时间段"}
            },
            "required": ["query_type"]
        }
    ),
    
    "data_analysis": AgentTool(
        name="数据分析",
        description="执行数据分析，生成图表和统计报告",
        icon="📊",
        parameters={
            "type": "object",
            "properties": {
                "analysis_type": {
                    "type": "string",
                    "enum": ["trend", "comparison", "distribution", "correlation"],
                    "description": "分析类型"
                },
                "data_source": {"type": "string", "description": "数据源"},
                "metrics": {"type": "array", "items": {"type": "string"}, "description": "指标列表"}
            },
            "required": ["analysis_type", "data_source"]
        }
    ),
    
    "report_generation": AgentTool(
        name="报告生成",
        description="生成各种格式的报告（PDF、Excel、Word）",
        icon="📄",
        parameters={
            "type": "object",
            "properties": {
                "report_type": {
                    "type": "string",
                    "enum": ["sales_report", "financial_report", "hr_report", "custom"],
                    "description": "报告类型"
                },
                "period": {"type": "string", "description": "时间周期 (day/week/month/quarter/year)"},
                "format": {"type": "string", "enum": ["pdf", "excel", "word"], "description": "输出格式"}
            },
            "required": ["report_type"]
        }
    ),
    
    "calendar_management": AgentTool(
        name="日程管理",
        description="管理日历、安排会议、发送提醒",
        icon="📅",
        parameters={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create_event", "schedule_meeting", "set_reminder"],
                    "description": "操作类型"
                },
                "title": {"type": "string", "description": "标题"},
                "datetime": {"type": "string", "description": "日期时间"},
                "participants": {"type": "array", "items": {"type": "string"}, "description": "参与者"}
            },
            "required": ["action", "title", "datetime"]
        }
    ),
    
    "email_management": AgentTool(
        name="邮件管理",
        description="发送邮件、处理邮件、生成邮件模板",
        icon="📧",
        parameters={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["send", "draft", "schedule"],
                    "description": "操作类型"
                },
                "to": {"type": "string", "description": "收件人"},
                "subject": {"type": "string", "description": "主题"},
                "body": {"type": "string", "description": "邮件内容"},
                "cc": {"type": "string", "description": "抄送"}
            },
            "required": ["action", "to", "subject"]
        }
    ),
    
    "file_management": AgentTool(
        name="文件管理",
        description="处理文件、生成文档、管理存储",
        icon="📁",
        parameters={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create", "upload", "download", "share"],
                    "description": "操作类型"
                },
                "file_type": {"type": "string", "description": "文件类型"},
                "file_name": {"type": "string", "description": "文件名"},
                "destination": {"type": "string", "description": "目标位置"}
            },
            "required": ["action", "file_name"]
        }
    )
}

# ==================== API 端点 ====================

class PromptRequest(BaseModel):
    role: str
    context: str
    question: str
    include_examples: bool = True

class PromptResponse(BaseModel):
    system_prompt: str
    user_prompt: str
    examples: List[str]

class AgentToolUpdate(BaseModel):
    name: str
    enabled: bool = True
    parameters: Optional[Dict] = None

@app.get("/api/prompts")
async def get_all_prompts():
    """获取所有可用的 Prompt 模板"""
    return {
        "templates": [template.to_dict() for template in PROMPT_TEMPLATES.values()],
        "total": len(PROMPT_TEMPLATES)
    }

@app.get("/api/prompts/{role}")
async def get_prompt_template(role: str):
    """获取特定角色的 Prompt 模板"""
    if role not in PROMPT_TEMPLATES:
        raise HTTPException(status_code=404, detail=f"角色 '{role}' 不存在")
    
    template = PROMPT_TEMPLATES[role]
    return template.to_dict()

@app.post("/api/prompts/generate")
async def generate_prompt(request: PromptRequest):
    """生成完整的 Prompt"""
    if request.role not in PROMPT_TEMPLATES:
        raise HTTPException(status_code=400, detail=f"未知的角色: {request.role}")
    
    template = PROMPT_TEMPLATES[request.role]
    
    # 组装用户 Prompt
    user_prompt = f"背景信息:\n{request.context}\n\n问题:\n{request.question}"
    
    # 组装最终的 Prompt
    full_prompt = f"{template.system_prompt}\n\n{user_prompt}"
    
    response = {
        "system_prompt": template.system_prompt,
        "user_prompt": user_prompt,
        "examples": template.examples if request.include_examples else [],
        "full_prompt": full_prompt
    }
    
    return response

@app.post("/api/prompts/custom")
async def create_custom_prompt(
    name: str,
    role: str,
    system_prompt: str,
    examples: List[str] = None
):
    """创建自定义 Prompt 模板"""
    new_template = PromptTemplate(
        name=name,
        role=role,
        system_prompt=system_prompt,
        examples=examples or []
    )
    
    # 保存到全局模板库
    PROMPT_TEMPLATES[role] = new_template
    
    return {
        "message": "自定义 Prompt 创建成功",
        "template": new_template.to_dict()
    }

@app.get("/api/agent/tools")
async def get_agent_tools():
    """获取所有可用的 Agent 工具"""
    return {
        "tools": [tool.to_dict() for tool in DEFAULT_TOOLS.values()],
        "total": len(DEFAULT_TOOLS)
    }

@app.get("/api/agent/tools/{tool_name}")
async def get_tool_details(tool_name: str):
    """获取特定工具的详细信息"""
    if tool_name not in DEFAULT_TOOLS:
        raise HTTPException(status_code=404, detail=f"工具 '{tool_name}' 不存在")
    
    return DEFAULT_TOOLS[tool_name].to_dict()

@app.post("/api/agent/tools/create")
async def create_custom_tool(
    name: str,
    description: str,
    parameters: Dict,
    icon: str = "⚙️"
):
    """创建自定义 Agent 工具"""
    if name in DEFAULT_TOOLS:
        raise HTTPException(status_code=400, detail=f"工具 '{name}' 已存在")
    
    new_tool = AgentTool(name, description, parameters, icon)
    DEFAULT_TOOLS[name] = new_tool
    
    return {
        "message": "自定义工具创建成功",
        "tool": new_tool.to_dict()
    }

@app.post("/api/agent/tools/update")
async def update_tool_config(tool_name: str, update: AgentToolUpdate):
    """更新 Agent 工具配置"""
    if tool_name not in DEFAULT_TOOLS:
        raise HTTPException(status_code=404, detail=f"工具 '{tool_name}' 不存在")
    
    tool = DEFAULT_TOOLS[tool_name]
    
    # 更新配置
    if update.enabled is not None:
        tool.enabled = update.enabled
    
    if update.parameters is not None:
        tool.parameters = update.parameters
    
    return {
        "message": "工具配置更新成功",
        "tool": tool.to_dict()
    }

@app.delete("/api/agent/tools/{tool_name}")
async def delete_tool(tool_name: str):
    """删除 Agent 工具"""
    if tool_name not in DEFAULT_TOOLS:
        raise HTTPException(status_code=404, detail=f"工具 '{tool_name}' 不存在")
    
    del DEFAULT_TOOLS[tool_name]
    
    return {"message": f"工具 '{tool_name}' 已删除"}

@app.post("/api/agent/tools/reorder")
async def reorder_tools(tool_order: List[str]):
    """重新排序 Agent 工具（支持拖拽）"""
    # 验证所有工具都存在
    for tool_name in tool_order:
        if tool_name not in DEFAULT_TOOLS:
            raise HTTPException(status_code=400, detail=f"工具 '{tool_name}' 不存在")
    
    # 按新顺序重建字典
    reordered = {}
    for tool_name in tool_order:
        reordered[tool_name] = DEFAULT_TOOLS[tool_name]
    
    # 替换原字典
    DEFAULT_TOOLS.clear()
    DEFAULT_TOOLS.update(reordered)
    
    return {
        "message": "工具顺序更新成功",
        "order": list(DEFAULT_TOOLS.keys())
    }

# ==================== 健康检查 ====================

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "Prompt Service",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
