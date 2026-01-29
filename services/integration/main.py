from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

app = FastAPI(
    title="AI Common Platform - Integration Service",
    description="企业系统集成服务",
    version="1.0.0"
)

# ==================== 模拟数据 ====================

# ERP系统数据
ERP_SALES_DATA = {
    "2024": {
        "Q1": {"amount": 5000, "growth": 0.15, "top_products": ["产品A", "产品B"]},
        "Q2": {"amount": 5500, "growth": 0.10, "top_products": ["产品A", "产品C"]},
        "Q3": {"amount": 6000, "growth": 0.09, "top_products": ["产品C", "产品D"]},
        "Q4": {"amount": 6500, "growth": 0.08, "top_products": ["产品D", "产品E"]},
    }
}

ERP_INVENTORY = {
    "产品A": {"stock": 500, "unit": "件", "location": "仓库A"},
    "产品B": {"stock": 300, "unit": "件", "location": "仓库B"},
    "产品C": {"stock": 1000, "unit": "件", "location": "仓库A"},
    "产品D": {"stock": 200, "unit": "件", "location": "仓库C"},
    "产品E": {"stock": 150, "unit": "件", "location": "仓库B"},
}

# HRM系统数据
HRM_DEPARTMENTS = {
    "sales": {"name": "销售部", "head": "张三", "employees": 100, "budget": 500},
    "technical": {"name": "技术部", "head": "李四", "employees": 200, "budget": 1000},
    "admin": {"name": "行政部", "head": "王五", "employees": 100, "budget": 300},
    "hr": {"name": "人资部", "head": "刘六", "employees": 50, "budget": 150},
    "finance": {"name": "财务部", "head": "陈七", "employees": 50, "budget": 200},
}

HRM_EMPLOYEES = [
    {"id": "E001", "name": "张三", "department": "sales", "position": "经理", "salary": 15000},
    {"id": "E002", "name": "李四", "department": "technical", "position": "总监", "salary": 20000},
    {"id": "E003", "name": "王五", "department": "admin", "position": "主任", "salary": 12000},
]

# CRM系统数据
CRM_CUSTOMERS = {
    "C001": {"name": "ABC公司", "industry": "制造", "status": "active", "sales": 500},
    "C002": {"name": "XYZ公司", "industry": "零售", "status": "active", "sales": 300},
    "C003": {"name": "DEF公司", "industry": "金融", "status": "active", "sales": 200},
}

# 财务系统数据
FINANCE_BUDGET = {
    "2024": {
        "total": 2000,
        "allocation": {
            "research": {"amount": 800, "percentage": 40},
            "operations": {"amount": 700, "percentage": 35},
            "marketing": {"amount": 500, "percentage": 25},
        },
        "currency": "万元"
    }
}

# ==================== 模型 ====================
class IntegrationRequest(BaseModel):
    """集成请求"""
    system: str  # erp, crm, hrm, finance
    operation: str  # query, create, update, delete
    data: Dict[str, Any] = {}

# ==================== 路由 ====================

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "integration"}

# ==================== ERP接口 ====================

@app.get("/api/integration/erp/sales/{year}/{quarter}")
async def query_erp_sales(year: str, quarter: str):
    """查询ERP销售数据"""
    try:
        if year in ERP_SALES_DATA and quarter in ERP_SALES_DATA[year]:
            data = ERP_SALES_DATA[year][quarter]
            return {
                "status": "success",
                "system": "erp",
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
        raise HTTPException(status_code=404, detail="数据不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/integration/erp/inventory")
async def query_erp_inventory(product_name: str = None):
    """查询库存"""
    if product_name:
        inventory = ERP_INVENTORY.get(product_name)
        if not inventory:
            raise HTTPException(status_code=404, detail="产品不存在")
        return {
            "status": "success",
            "system": "erp",
            "product": product_name,
            "data": inventory
        }
    return {
        "status": "success",
        "system": "erp",
        "data": ERP_INVENTORY
    }

# ==================== HRM接口 ====================

@app.get("/api/integration/hrm/departments")
async def query_hrm_departments():
    """查询部门信息"""
    return {
        "status": "success",
        "system": "hrm",
        "data": HRM_DEPARTMENTS,
        "total": len(HRM_DEPARTMENTS)
    }

@app.get("/api/integration/hrm/employees")
async def query_hrm_employees(department: str = None):
    """查询员工信息"""
    employees = HRM_EMPLOYEES
    if department:
        employees = [e for e in employees if e["department"] == department]
    
    return {
        "status": "success",
        "system": "hrm",
        "data": employees,
        "total": len(employees)
    }

@app.get("/api/integration/hrm/employees/{employee_id}")
async def query_hrm_employee(employee_id: str):
    """查询特定员工"""
    for emp in HRM_EMPLOYEES:
        if emp["id"] == employee_id:
            return {
                "status": "success",
                "system": "hrm",
                "data": emp
            }
    raise HTTPException(status_code=404, detail="员工不存在")

# ==================== CRM接口 ====================

@app.get("/api/integration/crm/customers")
async def query_crm_customers():
    """查询客户列表"""
    return {
        "status": "success",
        "system": "crm",
        "data": CRM_CUSTOMERS,
        "total": len(CRM_CUSTOMERS)
    }

@app.get("/api/integration/crm/customers/{customer_id}")
async def query_crm_customer(customer_id: str):
    """查询特定客户"""
    customer = CRM_CUSTOMERS.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    return {
        "status": "success",
        "system": "crm",
        "data": customer
    }

# ==================== 财务接口 ====================

@app.get("/api/integration/finance/budget/{year}")
async def query_finance_budget(year: str):
    """查询财务预算"""
    budget = FINANCE_BUDGET.get(year)
    if not budget:
        raise HTTPException(status_code=404, detail="预算数据不存在")
    
    return {
        "status": "success",
        "system": "finance",
        "data": budget
    }

# ==================== 通用接口 ====================

@app.post("/api/integration/query")
async def generic_query(request: IntegrationRequest):
    """通用查询接口"""
    try:
        system = request.system.lower()
        
        if system == "erp":
            return {"status": "success", "data": ERP_SALES_DATA}
        elif system == "hrm":
            return {"status": "success", "data": {"departments": HRM_DEPARTMENTS}}
        elif system == "crm":
            return {"status": "success", "data": CRM_CUSTOMERS}
        elif system == "finance":
            return {"status": "success", "data": FINANCE_BUDGET}
        else:
            raise HTTPException(status_code=400, detail="未知的系统")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/integration/systems")
async def list_systems():
    """获取集成的系统列表"""
    return {
        "systems": [
            {
                "name": "erp",
                "description": "企业资源规划系统",
                "endpoints": ["/erp/sales", "/erp/inventory"]
            },
            {
                "name": "hrm",
                "description": "人力资源管理系统",
                "endpoints": ["/hrm/departments", "/hrm/employees"]
            },
            {
                "name": "crm",
                "description": "客户关系管理系统",
                "endpoints": ["/crm/customers"]
            },
            {
                "name": "finance",
                "description": "财务管理系统",
                "endpoints": ["/finance/budget"]
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
