-- 初始化数据库脚本

-- ==================== 问答记录表 ====================
CREATE TABLE IF NOT EXISTS qa_records (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT,
    question_type VARCHAR(50),
    confidence FLOAT,
    execution_time FLOAT,
    sources TEXT,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- ==================== 知识库文档表 ====================
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50),
    tags TEXT,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    FULLTEXT INDEX ft_content (content)
);

-- ==================== Prompt模板表 ====================
CREATE TABLE IF NOT EXISTS prompt_templates (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(100),
    description TEXT,
    content TEXT NOT NULL,
    version VARCHAR(20),
    variables TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_role (role)
);

-- ==================== Agent任务表 ====================
CREATE TABLE IF NOT EXISTS agent_tasks (
    id VARCHAR(36) PRIMARY KEY,
    question TEXT NOT NULL,
    tools TEXT,
    status VARCHAR(20),
    results TEXT,
    execution_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- ==================== 用户会话表 ====================
CREATE TABLE IF NOT EXISTS user_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    context TEXT,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expired_at TIMESTAMP,
    INDEX idx_user_id (user_id)
);

-- ==================== LLM使用记录表 ====================
CREATE TABLE IF NOT EXISTS llm_usage (
    id VARCHAR(36) PRIMARY KEY,
    model_name VARCHAR(100),
    prompt_tokens INT,
    completion_tokens INT,
    total_tokens INT,
    cost FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model (model_name),
    INDEX idx_created_at (created_at)
);

-- ==================== 审计日志表 ====================
CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(100),
    action VARCHAR(100),
    resource VARCHAR(100),
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
);

-- ==================== 初始化数据 ====================

-- 插入Prompt模板
INSERT INTO prompt_templates (id, name, role, description, content, version, variables) VALUES
('sales_advisor', '销售顾问', 'Sales Advisor', '专注于销售数据和客户信息的顾问', '你是一名专业的销售顾问，具备丰富的销售知识和行业经验。提供数据驱动的建议。', '1.0', '["question","sales_data","customer_info"]'),
('hr_advisor', '人资顾问', 'HR Advisor', '专注于员工信息和薪资福利的顾问', '你是一名专业的人力资源顾问，关注员工信息、薪资福利、考勤记录。', '1.0', '["question","employee_info","benefits_policy"]'),
('tech_advisor', '技术顾问', 'Technical Advisor', '专注于系统架构和技术方案的顾问', '你是一名资深技术架构师，提供可行的技术解决方案。', '1.0', '["question","system_architecture","technical_constraints"]'),
('finance_advisor', '财务顾问', 'Finance Advisor', '专注于财务数据和预算的顾问', '你是一名专业的财务顾问，提供数据驱动的财务建议。', '1.0', '["question","financial_data","budget_info"]');

-- 插入示例文档
INSERT INTO documents (id, title, content, category, tags, source) VALUES
('doc_001', 'Q1销售报告', '2024年Q1销售业绩：总销售额5000万元，同比增长15%。重点客户包括ABC公司、XYZ公司等。', 'sales', '销售,报告,Q1', 'erp_system'),
('doc_002', '员工手册', '公司员工手册包含薪资制度、休假政策、考勤规则、福利待遇等详细规定。', 'hr', '员工,政策,手册', 'hr_system'),
('doc_003', '技术架构文档', '系统采用微服务架构，包含多个独立的服务模块，使用Docker容器化部署。', 'technical', '架构,技术,文档', 'knowledge_base'),
('doc_004', '财务预算方案', '2024年财务预算总额为2000万元，其中研发占40%，运营占35%，市场营销占25%。', 'finance', '财务,预算,2024', 'finance_system');
