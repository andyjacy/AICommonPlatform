from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import time
import sqlite3
import json
import os
from pathlib import Path

app = FastAPI(title="RAG Service Lite", version="2.0.0")

class Document(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    category: str
    tags: List[str] = []
    source: str = "internal"
    created_at: Optional[datetime] = None

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    category: Optional[str] = None

class SearchResult(BaseModel):
    documents: List[Document]
    total: int
    search_time: float

# 向量数据库配置
DB_PATH = "/app/data/vector_store.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    """初始化向量数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT NOT NULL,
        tags TEXT,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def insert_document(doc: Document):
    """插入文档到向量数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT OR REPLACE INTO documents 
        (id, title, content, category, tags, source, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            doc.id,
            doc.title,
            doc.content,
            doc.category,
            json.dumps(doc.tags),
            doc.source,
            doc.created_at
        ))
        conn.commit()
    finally:
        conn.close()

def search_documents(query_text: str, top_k: int = 5, category: Optional[str] = None) -> List[Document]:
    """从向量数据库搜索文档 - 带相关性阈值"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query_lower = query_text.lower()
    query_words = query_lower.split()  # 分解查询词
    
    try:
        sql = '''
        SELECT id, title, content, category, tags, source, created_at FROM documents
        WHERE 1=1
        '''
        params = []
        
        if category:
            sql += ' AND category = ?'
            params.append(category)
        
        # 计算相关性分数：优先匹配标题，其次匹配内容
        # 如果查询词在标题中出现，得3分；在内容中出现，得1分
        sql += '''
        ORDER BY 
            CASE 
                WHEN LOWER(title) LIKE ? THEN 3
                WHEN LOWER(content) LIKE ? THEN 1
                ELSE 0
            END DESC
        LIMIT ?
        '''
        
        search_pattern = f'%{query_lower}%'
        params.extend([search_pattern, search_pattern, top_k])
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            title_match = query_lower in row[1].lower()
            content_match = query_lower in row[2].lower()
            
            # 只返回有匹配的文档
            if title_match or content_match:
                results.append(Document(
                    id=row[0],
                    title=row[1],
                    content=row[2],
                    category=row[3],
                    tags=json.loads(row[4]) if row[4] else [],
                    source=row[5],
                    created_at=row[6]
                ))
        
        conn.close()
        return results
    except Exception as e:
        logger.error(f"搜索失败: {str(e)}")
        conn.close()
        return []

def get_all_documents() -> List[Document]:
    """获取所有文档"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, title, content, category, tags, source, created_at FROM documents')
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            doc = Document(
                id=row['id'],
                title=row['title'],
                content=row['content'],
                category=row['category'],
                tags=json.loads(row['tags']) if row['tags'] else [],
                source=row['source'],
                created_at=row['created_at']
            )
            results.append(doc)
        
        return results
    finally:
        conn.close()

# 初始化数据库
init_db()

# 知识库样本数据 - 企业多个业务环节
SAMPLE_DOCUMENTS = [
    # ==================== 销售部门 ====================
    Document(
        id="doc_001",
        title="Q1销售报告",
        content="2024年Q1销售业绩报告：总销售额5000万元，同比增长15%。主要销售渠道包括线上渠道占60%，线下渠道占40%。重点客户贡献了35%的销售额。销售排名前三的产品为A产品、B产品、C产品。",
        category="sales",
        tags=["销售", "报告", "Q1", "业绩"],
        source="erp_system"
    ),
    Document(
        id="doc_sales_strategy",
        title="销售策略和目标",
        content="2024年销售目标：全年销售额20亿元，同比增长20%。重点目标市场：华东区域(25%)、华北区域(30%)、华中区域(25%)、其他(20%)。销售团队目标：拓展新客户100家，续约率达到95%。推行积分制激励政策。",
        category="sales",
        tags=["策略", "目标", "规划"],
        source="sales_department"
    ),
    Document(
        id="doc_customer_analysis",
        title="客户群体分析",
        content="现有客户分类：大客户(500家，贡献60%)、中型客户(2000家，贡献30%)、小客户(5000家，贡献10%)。主要客户行业：金融(35%)、制造(25%)、零售(20%)、其他(20%)。客户平均CLV为150万元。",
        category="sales",
        tags=["客户", "分析", "数据"],
        source="crm_system"
    ),
    Document(
        id="doc_sales_commission",
        title="销售佣金和激励政策",
        content="销售佣金结构：基础工资+销售提成(2-5%)。完成目标100%奖励20%，完成80-99%奖励10%，完成不足80%无奖励。季度优秀销售额外奖励5000元。新客户开发奖励：签约额的1%。",
        category="sales",
        tags=["薪酬", "激励", "政策"],
        source="hr_system"
    ),
    
    # ==================== 人力资源 ====================
    Document(
        id="doc_002",
        title="员工手册",
        content="公司员工基本待遇：月薪5000-15000元，根据职位等级确定。年假20天，加班补偿按政策执行。产假3个月，陪产假7天。员工福利包括五险一金、体检、培训、餐补、交通补贴。",
        category="hr",
        tags=["员工", "政策", "待遇"],
        source="hr_system"
    ),
    Document(
        id="doc_org_structure",
        title="组织结构和部门",
        content="公司组织结构分为5大部门：销售部(100人)、研发部(80人)、运营部(50人)、市场部(30人)、行政部(20人)。CEO直属有CTO、CFO、COO三位高管。各部门均设部长和经理级别。",
        category="hr",
        tags=["组织", "结构", "部门"],
        source="org_chart"
    ),
    Document(
        id="doc_recruitment",
        title="招聘政策和流程",
        content="公司年度招聘目标：100人。招聘流程：简历筛选→笔试→面试(一面、二面、三面)→背景调查→入职。应届毕业生享受3个月培养期，薪资另议。社招人员薪资按市场价确定。",
        category="hr",
        tags=["招聘", "流程", "政策"],
        source="hr_system"
    ),
    Document(
        id="doc_training",
        title="员工培训和发展",
        content="公司每年投入300万元用于员工培训。培训项目包括：新员工培训(2周)、岗位技能培训(每月)、管理培训(针对晋升)、外部培训(每年2次)。员工可申请专业认证，公司报销50-100%费用。",
        category="hr",
        tags=["培训", "发展", "投入"],
        source="training_center"
    ),
    Document(
        id="doc_performance",
        title="绩效管理体系",
        content="公司实行360度绩效评估。评估周期为季度(占40%)和年度(占60%)。绩效评分分为5个等级：优秀(90+)、良好(80-89)、合格(70-79)、基本(60-69)、不合格(60以下)。绩效与薪酬、晋升、奖金挂钩。",
        category="hr",
        tags=["绩效", "评估", "体系"],
        source="hr_system"
    ),
    
    # ==================== 财务部门 ====================
    Document(
        id="doc_004",
        title="财务预算方案",
        content="2024年总预算10亿元，其中研发投入30%(3亿)、销售投入35%(3.5亿)、运营投入25%(2.5亿)、管理投入10%(1亿)。按季度分配执行，每季度2.5亿元。月度预算控制在8000万元。",
        category="finance",
        tags=["财务", "预算", "规划"],
        source="finance_system"
    ),
    Document(
        id="doc_cost_control",
        title="成本控制政策",
        content="公司成本控制目标：降低运营成本10%。主要措施：1)优化供应链成本、2)提升生产效率、3)减少管理开支、4)优化人员配置。成本节约奖励政策：节约额的5%作为部门奖励基金。",
        category="finance",
        tags=["成本", "控制", "目标"],
        source="finance_system"
    ),
    Document(
        id="doc_revenue_forecast",
        title="收入预测和趋势",
        content="根据历史数据，预测2024年全年收入20亿元。季度分布：Q1占20%、Q2占25%、Q3占30%、Q4占25%。主要收入来源：产品销售(70%)、服务收入(20%)、其他(10%)。毛利率预计在45-50%之间。",
        category="finance",
        tags=["收入", "预测", "趋势"],
        source="finance_system"
    ),
    Document(
        id="doc_cash_flow",
        title="现金流管理",
        content="公司现金流管理目标：保持充足现金储备应对3-6个月运营。应收账款回款周期目标：30天内80%、60天内95%。应付账款周期：30-60天。融资能力：目前有2条融资额度共5亿元。",
        category="finance",
        tags=["现金流", "管理", "流动性"],
        source="finance_system"
    ),
    
    # ==================== 技术部门 ====================
    Document(
        id="doc_003",
        title="技术架构文档",
        content="系统采用微服务架构，包含8个核心服务模块。使用Python FastAPI框架开发，支持高并发处理。数据库使用PostgreSQL和MySQL，使用Redis缓存。部署在Docker容器中，使用Kubernetes编排。支持99.9%的可用性。",
        category="technical",
        tags=["架构", "技术", "设计"],
        source="wiki"
    ),
    Document(
        id="doc_tech_stack",
        title="技术栈和工具",
        content="前端：React 18、TypeScript、Ant Design。后端：Python FastAPI、Node.js。数据库：PostgreSQL、MySQL、Redis、Elasticsearch。部署：Docker、Kubernetes、AWS云。监控：Prometheus、Grafana、ELK。版本控制：Git、GitHub。",
        category="technical",
        tags=["技术栈", "工具", "框架"],
        source="tech_team"
    ),
    Document(
        id="doc_api_standards",
        title="API标准和规范",
        content="公司API开发标准：REST API设计、JSON格式传输、使用JWT认证。响应时间目标<200ms。版本管理：v1/v2/v3。错误处理：统一错误码、详细错误信息。文档工具：Swagger/OpenAPI、自动化文档生成。",
        category="technical",
        tags=["API", "标准", "规范"],
        source="tech_team"
    ),
    Document(
        id="doc_deployment",
        title="部署和运维流程",
        content="部署流程：代码提交→自动化测试→灰度发布→全量上线。每周发布一次，紧急修复随时处理。运维目标：系统可用性99.95%、平均恢复时间<15分钟。SLA保证：关键系统24小时支持。",
        category="technical",
        tags=["部署", "运维", "流程"],
        source="devops_team"
    ),
    
    # ==================== 供应链和采购 ====================
    Document(
        id="doc_supplier_mgmt",
        title="供应商管理政策",
        content="公司管理供应商1000+家。供应商分级：一级(战略供应商50家)、二级(稳定供应商200家)、三级(其他750家)。采购流程：需求评估→供应商选择→合同签订→订单执行→质检验收。付款周期：30-60天。",
        category="supply_chain",
        tags=["供应商", "管理", "采购"],
        source="procurement"
    ),
    Document(
        id="doc_inventory",
        title="库存管理方案",
        content="公司库存目标：保持15-30天的销售周期库存。库存分类：原材料、半成品、成品。ABC分类管理：A类(80%价值)→每周盘点、B类(15%价值)→每月盘点、C类(5%价值)→每季度盘点。库存周转率目标：12次/年。",
        category="supply_chain",
        tags=["库存", "管理", "优化"],
        source="warehouse"
    ),
    Document(
        id="doc_procurement_cost",
        title="采购成本优化",
        content="采购成本占总成本的40%。优化目标：降低采购成本5%。措施：1)集中采购降低单价、2)长期合同锁定价格、3)改进产品设计降低成本、4)使用替代材料。每年目标节省成本500万元。",
        category="supply_chain",
        tags=["采购", "成本", "优化"],
        source="procurement"
    ),
    
    # ==================== 市场营销 ====================
    Document(
        id="doc_market_positioning",
        title="市场定位和竞争分析",
        content="公司主要面对中大型企业客户，在市场中排名前3。主要竞争对手分析：竞争对手A(功能完整)、竞争对手B(价格便宜)。我们的优势：用户体验好、服务质量高、创新能力强。市场增长率：年10-15%。",
        category="marketing",
        tags=["市场", "竞争", "分析"],
        source="marketing_system"
    ),
    Document(
        id="doc_brand_strategy",
        title="品牌策略",
        content="品牌核心价值：创新、可靠、服务至上。品牌口号：'让数据驱动决策'。品牌投入：广告30%、PR 20%、赞助20%、其他30%。目标：提升品牌知名度至80%、认可度至70%。",
        category="marketing",
        tags=["品牌", "策略", "定位"],
        source="marketing_system"
    ),
    Document(
        id="doc_007",
        title="市场营销策略",
        content="2024年营销策略重点聚焦于社交媒体营销和内容营销。预计通过B2B平台和行业展会拓展新客户。品牌推广预算占营销总投入的40%。数字营销投入占55%，传统媒体占45%。目标：获取新客户200家。",
        category="marketing",
        tags=["营销", "策略", "推广"],
        source="marketing_system"
    ),
    
    # ==================== 产品和运营 ====================
    Document(
        id="doc_006",
        title="产品功能清单",
        content="核心产品功能包括：用户管理、数据分析、报表生成、权限控制、审计日志、实时监控、数据导入导出。支持REST API集成，提供Python/Java/JavaScript SDK。产品版本：免费版、专业版、企业版三个等级。",
        category="product",
        tags=["产品", "功能", "特性"],
        source="pm_system"
    ),
    Document(
        id="doc_product_roadmap",
        title="产品开发路线图",
        content="2024年产品规划：Q1-Q2 AI能力增强、Q3 移动端优化、Q4 国际化支持。重点功能：实时协作、高级数据分析、行业模板库、开放平台。预计新增功能50+个。",
        category="product",
        tags=["产品", "规划", "路线图"],
        source="pm_system"
    ),
    Document(
        id="doc_customer_support",
        title="客户支持和服务",
        content="客户支持7×24小时在线。支持渠道：工单系统、电话、邮件、微信。平均响应时间<30分钟。客户满意度目标：95%。年度续约率目标：90%。客户生命周期价值：300万元。",
        category="operations",
        tags=["支持", "服务", "客户"],
        source="customer_service"
    ),
    
    # ==================== 安全合规 ====================
    Document(
        id="doc_008",
        title="系统安全政策",
        content="数据加密采用AES-256标准，通信采用TLS 1.2+。用户密码需要定期更新，支持多因素认证。系统日志保留6个月。访问控制：基于角色的权限管理。合规性：符合GDPR、等保三级。",
        category="security",
        tags=["安全", "政策", "合规"],
        source="security_team"
    ),
    Document(
        id="doc_data_privacy",
        title="数据隐私政策",
        content="用户数据隐私保护：不与第三方共享，用户有权申请删除。数据分类：公开、机密、个人。数据保留期：30个月后自动删除。审计日志：所有数据访问都有记录。定期安全审计：每季度一次。",
        category="security",
        tags=["隐私", "数据", "保护"],
        source="security_team"
    ),
]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rag_service_lite", "version": "2.0.0"}

@app.post("/api/rag/init")
async def initialize_knowledge_base():
    """初始化知识库 - 将样本数据写入向量数据库"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM documents')
        conn.commit()
        conn.close()
        
        for doc in SAMPLE_DOCUMENTS:
            insert_document(doc)
        
        return {
            "status": "success",
            "message": f"Successfully initialized {len(SAMPLE_DOCUMENTS)} documents",
            "total": len(SAMPLE_DOCUMENTS)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize: {str(e)}")

@app.post("/api/rag/search", response_model=SearchResult)
async def search_knowledge_base(query: SearchQuery):
    """从向量数据库搜索文档"""
    start_time = time.time()
    
    try:
        results = search_documents(query.query, query.top_k, query.category)
        search_time = time.time() - start_time
        
        # 如果没有找到结果，返回空列表而不是提示文档
        # QA Entry 会根据空结果决定是否调用 LLM
        return SearchResult(documents=results, total=len(results), search_time=search_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/rag/documents")
async def list_documents():
    """获取所有文档"""
    try:
        docs = get_all_documents()
        return {"documents": docs, "total": len(docs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@app.post("/api/rag/documents")
async def add_document(doc: Document):
    """添加新文档到向量数据库"""
    try:
        if not doc.id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM documents')
            count = cursor.fetchone()['count']
            conn.close()
            doc.id = f"doc_{count + 1:03d}"
        
        insert_document(doc)
        return {"status": "success", "id": doc.id, "message": "Document added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add document: {str(e)}")

@app.delete("/api/rag/documents/{doc_id}")
async def delete_document(doc_id: str):
    """删除文档"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Document {doc_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
